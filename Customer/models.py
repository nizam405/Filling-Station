from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.db.models import Sum

from Product.models import Product, SellingRate, Sell
from .choices import customer_type, INDIVIDUAL, GROUP
from Transaction.functions import last_balance_date
from Core.functions import first_date_of_month

class GroupofCompany(models.Model):
    name = models.CharField(max_length=255, verbose_name="নাম")
    # সক্রিয় করলে customer dropdown list এ দেখাবে
    active = models.BooleanField(default=True, verbose_name='সক্রিয়')
    date_created = models.DateField(default=last_balance_date)
    serial = models.SmallIntegerField(default=0, verbose_name="ক্রম")
    active = models.BooleanField(default=True, verbose_name='সক্রিয়')

    class Meta:
        ordering = ['serial']

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse("groupofcompanies")

class Customer(models.Model):
    name        = models.CharField(max_length=255, verbose_name="নাম", unique=True)
    short_name  = models.CharField(max_length=25, verbose_name="সংক্ষিপ্ত নাম", null=True, blank=True)
    cust_type   = models.CharField(max_length=20, verbose_name="ধরণ", choices=customer_type, default=INDIVIDUAL)
    group       = models.ForeignKey(GroupofCompany, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="গ্রুপ")
    mobile      = models.CharField(max_length=11, null=True, blank=True, verbose_name="মোবাইল")
    serial      = models.SmallIntegerField(default=0, verbose_name="ক্রম")
    # সক্রিয় করলে customer dropdown list এ দেখাবে
    active      = models.BooleanField(default=True, verbose_name='সক্রিয়')
    date_created= models.DateField(default=last_balance_date)

    class Meta:
        ordering = ['-active','cust_type','group','serial','name']
        get_latest_by = ['date_created']
    
    def get_next_serial(self):
        max_serial = Customer.objects.aggregate(models.Max('serial'))['serial__max']
        if max_serial is None:
            return 1
        else:
            return max_serial + 1

    def __str__(self):
        txt = self.name
        if self.group: txt += f" ({self.group})"
        return txt
    
    def get_absolute_url(self):
        return reverse("customers")

class DueSell(models.Model):
    date = models.DateField(default=last_balance_date, verbose_name="তারিখ")
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, verbose_name="ক্রেতা", 
        limit_choices_to={'active':True})
    product = models.ForeignKey(Product, default=1, on_delete=models.SET_NULL, null=True, verbose_name="মাল", 
        limit_choices_to={'active':True})
    quantity = models.FloatField(default=1, verbose_name="পরিমাণ")
    rate = models.FloatField(default=0.0, verbose_name="দর")
    selling_rate = models.ForeignKey(SellingRate, null=True, on_delete=models.SET_NULL)
    price = models.FloatField(null=True, blank=False, verbose_name="মোট")
    sell = models.OneToOneField(Sell, on_delete=models.SET_NULL, null=True, verbose_name='বিক্রয়')

    class Meta:
        ordering = ['-date','customer','product__category','product__name']
        get_latest_by = ['date']

    def __str__(self):
        return f"DueSell: {self.date} - {self.customer} - {self.product} - {self.quantity} Ltr. - {self.price} Tk."
    
    def get_absolute_url(self):
        return reverse('create-duesell', kwargs={'date':self.date})
    
    def save(self, *args, **kwargs):
        self.rate = self.selling_rate.amount
        self.price = self.rate * self.quantity
        super().save(*args, **kwargs)
    
class DueCollection(models.Model):
    date = models.DateField(default=last_balance_date, verbose_name="তারিখ")
    customer = models.ForeignKey(to=Customer, on_delete=models.SET_NULL, null=True, verbose_name="ক্রেতা", 
        limit_choices_to={'active':True})
    amount = models.FloatField(null=True, blank=False, verbose_name="টাকা")

    class Meta:
        ordering = ['-date']
        get_latest_by = ['date']
    
    @property
    def remaining_due(self):
        from .functions import get_remaining_due
        from Core.functions import first_date_of_month
        from_date = first_date_of_month(self.date)
        due,bad_debt = get_remaining_due(from_date,self.date,self.customer)
        return due

    def __str__(self):
        return f"DueCollection: {self.date} - {self.customer} - {self.amount}"
    
    def get_absolute_url(self):
        return reverse('daily-transactions', kwargs={'date':self.date})


# Balance should contain Initial balance.
class BaseCustomerDue(models.Model):
    date    = models.DateField(default=last_balance_date, verbose_name="তারিখ")
    amount  = models.FloatField(null=True, blank=False, verbose_name="পরিমাণ")
    bad_debt= models.BooleanField(default=False, verbose_name="অনিশ্চিত")

    class Meta:
        abstract = True
        ordering = ['-date','customer__serial']
        get_latest_by = ['date','customer__serial']
    
    # @property
    # def due_sells(self):
    #     if isinstance(self, CustomerDue):
    #         queryset = DueSell.objects.filter(customer=self.customer,date=self.date)
    #     else: 
    #         queryset = DueSell.objects.filter(customer__group=self.customer,date=self.date)
    #     return queryset
    
    # @property
    # def due_sells_amount(self):
    #     queryset = self.due_sells
    #     return queryset.aggregate(Sum('price'))['price__sum'] if queryset else 0
    
    # @property
    # def due_collections(self):
    #     if isinstance(self, CustomerDue):
    #         queryset = DueCollection.objects.filter(customer=self.customer,date=self.date)
    #     else: 
    #         queryset = DueCollection.objects.filter(customer__group=self.customer,date=self.date)
    #     return queryset
    
    # @property
    # def due_collections_amount(self):
    #     queryset = self.due_collections
    #     return queryset.aggregate(Sum('amount'))['amount__sum'] if queryset else 0
    
    # @property
    # def current_due(self):
    #     return self.amount + self.due_sells_amount - self.due_collections_amount

    def __str__(self):
        output = f"{self.date} {self.customer} : {self.amount}"
        if self.bad_debt: output += " অনিশ্চিত"
        return output
    
class CustomerDue(BaseCustomerDue):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name="ক্রেতা",
                limit_choices_to={'cust_type': INDIVIDUAL})
    
    def get_absolute_url(self):
        return reverse("customer-ledger", kwargs={"pk": self.pk})

class GroupofCompanyDue(BaseCustomerDue):
    customer = models.ForeignKey(GroupofCompany, on_delete=models.CASCADE, verbose_name="ক্রেতা")

    # @property
    # def sub_company_due(self):
    #     customers = Customer.objects.filter(group=self.customer)
    #     data = []
    #     for cust in customers:
    #         due_sells = self.due_sells.filter(customer=cust)
    #         data.append({
    #             'customer': cust,
    #             'duesell_amount': due_sells.aggregate(Sum('price'))['price__sum'] or None,
    #             'due_sells': due_sells
    #         })
    #     return data
    
    def get_absolute_url(self):
        return reverse("groupofcompany-balance")