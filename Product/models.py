from django.db import models
from django.urls import reverse
from django.db.models import Sum
from django.utils.safestring import mark_safe
import datetime
from pybengali import convert_e2b_digit
from Transaction.functions import last_balance_date
from .choices import PRODUCT_CATEGORIES, FUEL, LUBRICANT, STOCK_IN_TYPE_CHOICES
from Core.functions import account_start_date

class Product(models.Model):
    name = models.CharField(max_length=100, verbose_name="মালের নাম")
    short_name =  models.CharField(max_length=10, verbose_name="মালের সংক্ষিপ্ত নাম")
    category = models.CharField(max_length=20, choices=PRODUCT_CATEGORIES, default=LUBRICANT, verbose_name="ধরন")
    packaged = models.BooleanField(verbose_name='মোড়কজাত',default=True)
    # need_rescale = models.BooleanField(default=False, verbose_name="মজুদ মাপতে হয়")
    # lot_unit = models.CharField(max_length=20,choices=UNIT_CHOICES,null=True,blank=True,verbose_name='লট একক')
    # retail_unit = models.CharField(max_length=20,choices=UNIT_CHOICES,null=True,blank=True,verbose_name='খুচরা একক')
    capacity = models.FloatField(default=None, null=True, blank=True, verbose_name="পরিমান")
    active = models.BooleanField(default=True, verbose_name='সক্রিয়')
    date_created = models.DateField(default=last_balance_date)

    class Meta:
        ordering = ['-active','category','name','capacity']
    
    @property
    def unit(self):
        return "পিছ" if self.packaged else "লিঃ"
    
    @property
    def retail_unit(self):
        if self.category == LUBRICANT:
            return "লিঃ"
    
    @property
    def last_purchase_rates(self):
        return PurchaseRate.objects.filter(product=self.pk, active=True)
    
    @property
    def last_selling_rates(self):
        return SellingRate.objects.filter(product=self.pk, active=True)
    
    # নির্দিষ্ট তারিখের ক্রয়মূল্য
    def get_purchase_rate(self,date=datetime.date.today()):
        rates = PurchaseRate.objects.filter(product=self.pk, date__lte=date)
        if rates: return rates.latest()
        else: return None

    @property
    def purchase_rate(self):
        return self.get_purchase_rate()
    
    # নির্দিষ্ট তারিখের বিক্রয়মূল্য
    def get_selling_rate(self,date=datetime.date.today()):
        rates = SellingRate.objects.filter(product=self.pk, date__lte=date)
        if rates: return rates.latest()
        else: return None

    @property
    def selling_rate(self):
        return self.get_selling_rate()
    
    @property
    def profit_rate(self):
        return self.selling_rate.amount - self.purchase_rate.amount

    def __str__(self):
        output = f"{self.name}"
        if self.packaged: output += f" {self.capacity}"
        return output
    
    def to_html(self):
        output = ""
        if self.packaged:
            output += f"<span class='eng'>{self.name}</span> {convert_e2b_digit(self.capacity)} {self.retail_unit}"
        else: output += self.name
        return mark_safe(output)
    
    def get_absolute_url(self):
        return reverse("products")

# Abstract Rate Variant Class
class BaseRateVariant(models.Model):
    name = models.CharField(max_length=50, verbose_name="নাম")
    normal = models.BooleanField(default=False, verbose_name='স্বাভাবিক দর')

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

# Purchase Rate
class PurchaseRateVariant(BaseRateVariant):
    def get_absolute_url(self):
        return reverse("purchase-rate-variant")
    
# Selling Rate
class SellingRateVariant(BaseRateVariant):
    def get_absolute_url(self):
        return reverse("selling-rate-variant")
    
# Abstract Rate Class
class BaseRate(models.Model):
    date = models.DateField(default=last_balance_date, verbose_name="কার্যকরের তারিখ (হইতে)")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="মালের নাম")
    variant = models.ForeignKey(BaseRateVariant, null=True, on_delete=models.SET_NULL)
    # packaged = models.BooleanField(verbose_name='মোড়কজাত',default=True)
    amount = models.FloatField(default=0, verbose_name="একক প্রতি মুল্য")
    active = models.BooleanField(default=True)

    class Meta:
        abstract = True
        ordering = ['-date']
        get_latest_by = "date"
        indexes = [
            models.Index(fields=['product', 'variant']),
            models.Index(fields=['date']),
            models.Index(fields=['amount']),
        ]

    def prev_rate(self):
        rates = self.__class__.objects.filter(product=self.product, variant=self.variant, date__lt=self.date)
        if rates:
            return rates.latest()
        return None
    
    @property
    def rate_update(self):
        if self.prev_rate():
            return self.prev_rate().amount - self.amount
        return 0
    
    @property
    def rate_status(self):
        status = 'same'
        prev_rate = self.prev_rate()
        if prev_rate:
            if prev_rate.amount < self.amount: status = 'up'
            elif prev_rate.amount > self.amount: status = 'down'
        return status
    
    def save(self, *args, **kwargs):
        # Deactivate previous active rate of save variant
        if self.active:
            self.__class__.objects.filter(
                product=self.product, 
                variant=self.variant, 
                active=True
            ).exclude(pk=self.pk).update(active=False)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.product} {self.date}: {self.amount} ({self.variant})"

class PurchaseRate(BaseRate):
    """
    Fields:
        date (datetime.date): Rate update date, 
        product (ForeignKey[Product]): object, 
        variant (ForeignKey[PurchaseRateVariant]): object, 
        amount (Float): Rate amount, 
        active (bool): is active?
    """
    variant = models.ForeignKey(to=PurchaseRateVariant, null=True, on_delete=models.SET_NULL, verbose_name='ধরন')
    
    def get_absolute_url(self):
        return reverse("purchase-rates", kwargs={"product": self.product.pk})
    
    def save(self, *args, **kwargs):
        if not self.variant:
            self.variant = PurchaseRateVariant.objects.get(normal=True)
        super().save(*args, **kwargs)

class SellingRate(BaseRate):
    """
    Fields:
        date: datetime.date,
        product: ForeignKey[Product], 
        variant: ForeignKey[SellingRateVariant], 
        amount: Float, 
        active: Boolean
    """
    variant = models.ForeignKey(to=SellingRateVariant, null=True, on_delete=models.SET_NULL, verbose_name='ধরন')

    @property
    def profit(self):
        purchase_rates = PurchaseRate.objects.filter(
            date__lte=self.date, 
            product=self.product,
            variant__normal=True
            )
        if purchase_rates:
            purchase_rate = purchase_rates.latest()
            return self.amount - purchase_rate.amount
        else: return 0
    
    def get_absolute_url(self):
        return reverse("selling-rates", kwargs={"product": self.product.pk})
    
    def save(self, *args, **kwargs):
        if not self.variant:
            try:
                self.variant = SellingRateVariant.objects.get(normal=True)
            except SellingRateVariant.DoesNotExist:
                raise ValueError('Default variant with normal=True does not exist')
        super().save(*args, **kwargs)

# Create on post_save CashBalance
class InitialStock(models.Model):
    date        = models.DateField(default=last_balance_date)
    product     = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity    = models.FloatField(default=0)
    purchase_rate = models.ForeignKey(PurchaseRate, null=True, on_delete=models.SET_NULL)
    rate        = models.FloatField(default=0)
    price       = models.FloatField(default=0)

    class Meta:
        ordering = ['-date','product__name']
        get_latest_by = ['date']
    
    @property
    def can_change(self):
        return self.date == account_start_date()

    def save(self, *args, **kwargs):
        if self.purchase_rate:
            self.rate = self.purchase_rate.amount
            self.price = self.rate * self.quantity
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("initial-stock", kwargs={"date": self.date})
    
    def __str__(self):
        return f"{self.date} {self.product} {self.quantity}x{self.rate}={self.price}"
    
# Abstract Purchase or Sell Class
class BasePurchaseSell(models.Model):
    date = models.DateField(default=last_balance_date)
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE, 
        verbose_name="মাল", limit_choices_to={'active':True})
    # packaged = models.BooleanField(verbose_name='মোড়কজাত',default=True)
    # unit = models.CharField(max_length=20,choices=UNIT_CHOICES,verbose_name='একক')
    quantity = models.FloatField(default=0, verbose_name="পরিমাণ")
    # Do not put rate and amount field in Form
    rate = models.FloatField(default=0, verbose_name="দর")
    price = models.FloatField(null=True, blank=False, verbose_name="মূল্য")

    class Meta:
        abstract = True
        ordering = ['-date','product__category','product__name']
        get_latest_by = 'date'
        indexes = [
            models.Index(fields=['product','date']),
            models.Index(fields=['product']),
            models.Index(fields=['price']),
            models.Index(fields=['quantity']),
        ]
    
    def get_rate_field(self):
        if self.__class__ == Purchase:
            rate_field = self.purchase_rate
        elif self.__class__ == Sell:
            rate_field = self.selling_rate
        else:
            rate_field = None
        return rate_field

    def __str__(self):
        rate_field = self.get_rate_field()
        variant = rate_field.variant.name if rate_field else None
        return f"{self.__class__.__name__}: {self.product.name}-({variant}) {self.rate}x{self.quantity}={self.price}"
    
    def save(self, *args, **kwargs):
        # purchase_rate/selling_rate may be deleted accidentally. 
        # To avail this set rate field from purchase_rate object immediately
        rate_field = self.get_rate_field()
        # if rate_field and not self.rate:
        self.rate = rate_field.amount
        self.price = self.rate * self.quantity
        super().save(*args, **kwargs)

class Purchase(BasePurchaseSell):
    purchase_rate = models.ForeignKey(PurchaseRate, 
        # limit_choices_to={'active':True},
        verbose_name="দর",
        null=True,
        on_delete=models.SET_NULL,
        blank=False
    )

    class Meta(BasePurchaseSell.Meta):
        indexes = BasePurchaseSell.Meta.indexes + [models.Index(fields=['product','date','purchase_rate'])]

    @property
    def stock(self):
        return Stock.objects.get(purchase=self.pk)

    @property
    def consumed(self) -> int:
        return self.stock.consumed
    
    def get_absolute_url(self):
        return reverse("create-purchase", kwargs={'date':self.date})

class Sell(BasePurchaseSell):
    """
    Required fields:  date, product, quantity, selling_rate
    Generated fields: stock, rate, amount, adjustment
    """
    selling_rate = models.ForeignKey(SellingRate, 
        limit_choices_to={'active':True},
        verbose_name='দর',
        null=True,
        on_delete=models.SET_NULL,
        blank=False
    )

    class Meta(BasePurchaseSell.Meta):
        indexes = BasePurchaseSell.Meta.indexes + [models.Index(fields=['product','date','selling_rate'])]
    
    def prev_sell(self):
        return self.__class__.objects.filter(
            date__lte=self.date, 
            product=self.product, 
            selling_rate__variant=self.selling_rate.variant
        ).exclude(pk=self.pk).order_by('-date').latest()
    
    def get_absolute_url(self):
        return reverse("create-sell", kwargs={'date':self.date})

# Stock related models
# class Tank(models.Model):
#     product = models.ForeignKey(Product,
#         on_delete=models.CASCADE,
#         limit_choices_to={'category':LOOSE},
#         verbose_name='মালের নাম'
#     )
#     capacity = models.FloatField(default=0, verbose_name='ধারণক্ষমতা')

#     def __str__(self):
#         return f'{self.product}: {self.capacity} লিঃ'

# class FuelDispenser(models.Model):pass

class StorageReading(models.Model):
    date = models.DateField(default=last_balance_date, verbose_name="তারিখ")
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE, limit_choices_to={'category':FUEL}, verbose_name="মাল")
    tank_deep = models.FloatField(null=True, blank=False, verbose_name="ট্যাংক-এ অবশিষ্ট")
    lorry_load = models.FloatField(default=0, verbose_name="গাড়ীতে লোডকৃত")
    purchase_rate = models.ForeignKey(PurchaseRate, null=True, on_delete=models.SET_NULL)
    rate = models.FloatField(default=0)

    class Meta:
        ordering = ['-date']
        get_latest_by = "date"
        constraints = [models.UniqueConstraint(fields=['date','product'],name='unique_storage_reading')]

    @property
    def quantity(self):
        return self.tank_deep+self.lorry_load
    
    @property
    def remaining(self):
        from Product.views.functions import get_remaining_stock
        remaining = get_remaining_stock(self.date,self.date, self.product)
        return remaining['quantity']
    
    @property
    def difference(self):
        return self.quantity - self.remaining

    def __str__(self):
        return f"StorageReading: {self.date}: {self.product} - {self.tank_deep}+{self.lorry_load} = {self.quantity}"
    
    def get_absolute_url(self):
        return reverse("daily-transactions", kwargs={'date':self.date})
    
    def get_purchase_rate(self):
        if self.difference > 0: # Excess
            rates = PurchaseRate.objects.filter(date__lte=self.date, product=self.product, variant__normal=True)
            if rates.exists():
                self.purchase_rate = rates.latest()
                self.rate = self.purchase_rate.amount
    
    def save(self, *args, **kwargs):
        self.get_purchase_rate()
        super().save(*args, **kwargs)

class Stock(models.Model):
    date = models.DateField(default=last_balance_date)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    stock_in_type = models.CharField(max_length=50, choices=STOCK_IN_TYPE_CHOICES)
    purchase_rate = models.ForeignKey(PurchaseRate, null=True, on_delete=models.SET_NULL)
    consumable = models.BooleanField(default=True)
    # Objects for tracing
    initial_stock = models.ForeignKey(InitialStock, null=True, blank=True, on_delete=models.CASCADE) # on accounts start date
    purchase = models.ForeignKey(Purchase, null=True, blank=True, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-date','-stock_in_type']
        get_latest_by = ['date','stock_in_type']
    
    @property
    def quantity(self):
        quantity = 0
        if self.initial_stock:
            quantity += self.initial_stock.quantity
        else: quantity += self.purchase.quantity
        return quantity

    @property
    def total_quantity(self):
        quantity = self.quantity
        quantity += self.excess['quantity']
        quantity -= self.shortage['quantity']
        return quantity
    
    @property
    def remaining(self):
        return self.quantity - self.sell['quantity']
    
    @property
    def ending(self):
        return self.total_quantity - self.sell['quantity']
    
    @property
    def sell(self):
        objects = ConsumeStock.objects.filter(stock=self.pk)
        return {
            'objects':objects,
            'quantity': objects.aggregate(Sum('quantity'))['quantity__sum'] if objects else 0,
            'price': sum(object.price for object in objects) if objects else 0,
        }
    
    @property
    def excess(self):
        objects = Excess.objects.filter(stock=self.pk)
        return {
            'objects':objects,
            'quantity': objects.aggregate(Sum('quantity'))['quantity__sum'] if objects else 0,
            'price': sum(object.price for object in objects) if objects else 0,
        }
    
    @property
    def shortage(self):
        objects = Shortage.objects.filter(stock=self.pk)
        return {
            'objects':objects,
            'quantity': objects.aggregate(Sum('quantity'))['quantity__sum'] if objects else 0,
            'price': sum(object.price for object in objects) if objects else 0,
        }
    
    @property
    def price(self) -> int:
        return self.total_quantity * self.purchase_rate.amount
    
    @property
    def remaining_price(self) -> int:
        return self.remaining * self.purchase_rate.amount
    
    @property
    def gross_profit(self):
        profit = self.sell_profit
        if not self.consumable:
            profit += self.excess['price']
            profit -= self.shortage['price']
        return profit
    
    @property
    def sell_profit(self) -> int:
        objects = ConsumeStock.objects.filter(stock=self.pk)
        return objects.aggregate(Sum('profit'))['profit__sum'] if objects.exists() else 0
    
    @property
    def next_consumable_stock(self):
        consumable_stocks = self.objects.filter(
            consumable=True,
            product=self.product,
            date__gte=self.date
        )
        consumable_stocks.exclude(pk=self.pk)
        return consumable_stocks.earliest()
    
    def __str__(self):
        return f"Stock: {self.date} {self.product.name}-{self.quantity}x{self.purchase_rate.amount}. Rem: {self.remaining} {self.stock_in_type}"

class ExcessShortage(models.Model):
    date = models.DateField(default=last_balance_date)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    storage_reading = models.ForeignKey(StorageReading, on_delete=models.CASCADE, null=True)
    quantity = models.FloatField(default=0)

    class Meta:
        abstract = True
        ordering = ['-date']
        get_latest_by = ['date']
    
    @property
    def price(self):
        return self.quantity * self.stock.purchase_rate.amount
    
    def get_absolute_url(self):
        return reverse("stock-details", kwargs={"pk": self.stock.pk})
    
    def __str__(self):
        return f"{self.date} {self.stock.product.short_name} : {self.quantity}"
    

class Excess(ExcessShortage):pass
class Shortage(ExcessShortage):pass

class ConsumeStock(models.Model):
    date = models.DateField(default=last_balance_date)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    quantity = models.FloatField(default=0)
    # Objects for tracing
    sell = models.ForeignKey(Sell, on_delete=models.CASCADE, null=True)
    profit_rate = models.FloatField(default=0)
    profit = models.FloatField(default=0)

    @property
    def rate(self):
        return self.sell.selling_rate.amount

    @property
    def price(self):
        return self.sell.selling_rate.amount * self.quantity
    
    @property
    def stock_rate(self):
        return self.stock.purchase_rate.amount

    @property
    def stock_price(self):
        return self.stock.purchase_rate.amount * self.quantity

    def save(self, *args, **kwargs):
    #     purchase_rate = self.stock.price/self.stock.quantity
    #     selling_rate = self.sell.price/self.sell.quantity
    #     self.profit_rate = selling_rate - purchase_rate
        self.profit_rate = self.sell.selling_rate.amount - self.stock.purchase_rate.amount
        self.profit = self.profit_rate * self.quantity
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Comsume: {self.stock.product.name} {self.quantity} {self.stock}"

# Remove this after migration ----------------------------
class Rate(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="মালের নাম")
    date = models.DateField(default=last_balance_date, verbose_name="কার্যকরের তারিখ (হইতে)", help_text="YYYY-MM-DD")
    purchase_rate = models.FloatField(default=0, verbose_name="একক প্রতি ক্রয়মুল্য")
    selling_rate = models.FloatField(default=0, verbose_name="একক প্রতি বিক্রয়মুল্য")

    class Meta:
        ordering = ['-date']
        get_latest_by = "date"

    def prev_rate(self):
        rates = self.__class__.objects.filter(product=self.product, date__lt=self.date)
        if rates:
            return rates.latest()
        else: None

    def prev_month_rate(self, current_month_year=None, current_month=None):
        if current_month_year==None or current_month==None:
            current_month_year = self.date.year
            current_month = self.date.month

        first_day = datetime.date(current_month_year, current_month,1)
        rates = self.__class__.objects.filter(product=self.product, date__lt=first_day)
        if rates:
            return rates.latest()
        else: None
    
    @property
    def prev_month_rate(self):
        return self.prev_month_rate()
    
    @property
    def purchase_rate_update(self):
        if self.prev_rate():
            return self.prev_rate().purchase_rate - self.purchase_rate
        else: return 0
    
    @property
    def selling_rate_update(self):
        if self.prev_rate():
            return self.prev_rate().selling_rate - self.selling_rate
        else: return 0

    @property
    def profit_rate(self):
        return self.selling_rate - self.purchase_rate
    
    @property
    def profit_rate_update(self):
        if self.prev_rate():
            return self.profit_rate - self.prev_rate().profit_rate

    def save(self, *args, **kwargs):
        # Use update_or_create on view, Rate will not have two value on same day
        update = True
        rates = self.__class__.objects.filter(product=self.product)
        if rates: # if the product has prev rate, collect data from it
            last_rate = rates.latest()
            last_selling_rate = last_rate.selling_rate
            if not self.selling_rate:
                self.selling_rate = last_selling_rate 
            last_purchase_rate = last_rate.purchase_rate
            if not self.purchase_rate:
                self.purchase_rate = last_purchase_rate 
            # Don't update if both selling rate and purchase rate have not changed
            if not self.pk and self.selling_rate == last_selling_rate and self.purchase_rate == last_purchase_rate:
                update = False

        if update:
            return super().save(*args, **kwargs)

    def __str__(self):
        return f"Rate: {self.product.name} - {self.date} - Purchase: {self.purchase_rate}, Selling: {self.selling_rate}"
    
    def get_absolute_url(self):
        return reverse("products")
# -----------------------------------------------