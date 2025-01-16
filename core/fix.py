import datetime
from Product.models import Stock, ConsumeStock, Purchase, Sell, Rate, SellingRate, PurchaseRate, SellingRateVariant, PurchaseRateVariant, StorageReading, Excess, Shortage
from Transaction.functions import first_balance_date, save_cashbalance
from Transaction.models import CashBalance
from Customer.models import DueSell, CustomerDue, GroupofCompanyDue
from Ledger.models import Storage
import datetime
from Product.models import Product, InitialStock
from Product.choices import LUBRICANT, FUEL, LOOSE_LUBRICANT
from Ledger.models import CustomerBalance,GroupofCompanyBalance
from Core.functions import prev_day, next_month, account_start_date
from Expenditure.models import Expenditure as Expense, ExpenditureGroup as ExpenseGroup
from Revenue.models import Revenue, RevenueGroup
from IncomeExpenditure.models import Income, Expenditure, IncomeGroup, ExpenditureGroup
from Owner.models import OwnersEquity

# Ensure rate variant
class Fix():
    np_rate_variant = None
    sp_rate_variant = None
    ns_rate_variant = None
    ss_rate_variant = None
    
    all_purchase_rates = None
    all_selling_rates = None

    all_purchases = None
    all_sells = None
    all_duesells = None
    storage_readings = None

    def ensure_rate_variant(self):
        self.np_rate_variant, created = PurchaseRateVariant.objects.get_or_create(name='স্বাভাবিক দর',defaults={'normal':True})
        self.sp_rate_variant, created = PurchaseRateVariant.objects.get_or_create(name='বিশেষ দর',defaults={'normal':False})
        self.ns_rate_variant, created = SellingRateVariant.objects.get_or_create(name='স্বাভাবিক দর',defaults={'normal':True})
        self.ss_rate_variant, created = SellingRateVariant.objects.get_or_create(name='বিশেষ দর',defaults={'normal':False})
    
    def get_all_queries(self):
        self.all_purchase_rates = PurchaseRate.objects.all().order_by('date')
        self.all_selling_rates = SellingRate.objects.all().order_by('date')

        self.all_purchases = Purchase.objects.all().order_by('date')
        self.all_sells = Sell.objects.all().order_by('date')
        self.all_duesells = DueSell.objects.all().order_by('date')
        self.storage_readings = StorageReading.objects.all().order_by('date')

    def clear_previous(self):
        print('Clearing purchase_rate and selling_rate from Sell, DueSell, Purchase, Storage, StorageReading.....')
        Sell.objects.filter(selling_rate__isnull=False).update(selling_rate=None)
        DueSell.objects.filter(selling_rate__isnull=False).update(selling_rate=None)
        Purchase.objects.filter(purchase_rate__isnull=False).update(purchase_rate=None)
        Storage.objects.filter(purchase_rate__isnull=False).update(purchase_rate=None)
        StorageReading.objects.filter(purchase_rate__isnull=False).update(purchase_rate=None)

        print('Deleting previous purchase rates.........')
        PurchaseRate.objects.all().delete()
        print('Deleting previous selling rates.........')
        SellingRate.objects.all().delete()
        print('Done')

        print("Deleting Excess and Shortage")
        Excess.objects.all().delete()
        Shortage.objects.all().delete()

        print("Deleting Stock")
        Stock.objects.all().delete()
        ConsumeStock.objects.all().delete()
    
    def repair_products(self):
        products = Product.objects.all()
        for product in products:
            if product.name == 'অকটেন' or product.name == 'ডিজেল':
                product.packaged = False
                product.category = FUEL
            elif product.name == 'মবিল':
                product.packaged = False
                product.category = LOOSE_LUBRICANT
            else:
                product.packaged = True
                product.category = LUBRICANT
            product.save()

    def initialize(self):
        # Cashbalance
        first_balance = CashBalance.objects.earliest()
        all_balance = CashBalance.objects.all().exclude(pk=first_balance.pk)
        all_balance.delete()
        first_balance.date = account_start_date()
        first_balance.save()
        # Owner Equity
        oes = OwnersEquity.objects.filter(month=10,year=2022)
        for oe in oes:
            # date = next_month(datetime.date(oe.year,oe.month,1))
            oe.date = account_start_date()
            oe.save()
        
        self.repair_products()
        self.copy_initial_stocks()
        self.copy_customer_balances()
        self.copy_income_expenditure()

    def copy_initial_stocks(self):
        print('Copying Initial Stocks..........')
        InitialStock.objects.all().delete()

        ledger_date = prev_day(account_start_date())
        year = ledger_date.year
        month = ledger_date.month
        primary_stocks = Storage.objects.filter(year=year,month=month)
        for p_stock in primary_stocks:
            if p_stock.quantity == 0: continue
            
            p_rate = PurchaseRate.objects.create(
                date = account_start_date(),
                product = p_stock.product,
                variant = self.np_rate_variant,
                amount = p_stock.price/p_stock.quantity,
                active = False
            )
            InitialStock.objects.create(
                date = account_start_date(),
                product = p_stock.product,
                quantity = p_stock.quantity,
                purchase_rate = p_rate,
                price = p_stock.price
            )
    
    def copy_customer_balances(self):
        print('Copying customer balances........')
        CustomerDue.objects.all().delete()
        GroupofCompanyDue.objects.all().delete()

        ledger_date = prev_day(account_start_date())
        year = ledger_date.year
        month = ledger_date.month
        cust_balances = CustomerBalance.objects.filter(year=year,month=month)
        for bal in cust_balances:
            date = next_month(datetime.date(bal.year,bal.month,1))
            CustomerDue.objects.create(
                date        = date,
                customer    = bal.customer,
                amount      = bal.amount,
                bad_debt    = bal.bad_debt
            )

        goc_balances = GroupofCompanyBalance.objects.filter(year=year,month=month)
        for bal in goc_balances:
            date = next_month(datetime.date(bal.year,bal.month,1))
            GroupofCompanyDue.objects.create(
                date        = date,
                customer    = bal.customer,
                amount      = bal.amount,
                bad_debt    = bal.bad_debt
            )
            
    def create_purchase_rate(self,instance:Rate|Purchase,variant,amount=0):
        if isinstance(instance, Purchase): amount=instance.rate
        elif isinstance(instance, Rate): amount = instance.purchase_rate
        purchase_rate = PurchaseRate.objects.create(
            date    = instance.date,
            product = instance.product,
            variant = variant,
            amount  = amount,
            active  = False
        )
        # print(purchase_rate)
        return purchase_rate
    
    def create_selling_rate(self,instance:Rate|Sell|DueSell,variant,amount=0):
        if isinstance(instance, (Sell,DueSell)): amount=instance.rate
        elif isinstance(instance, Rate): amount = instance.selling_rate
        selling_rate = SellingRate.objects.create(
            date    = instance.date,
            product = instance.product,
            variant = variant,
            amount  = amount,
            active  = False
        )
        # print(selling_rate)
        return selling_rate
    
    def copy_rates(self):
        print('Updating Rates........')
        rates = Rate.objects.all().order_by('date')
        for rate in rates:
            prev_rate = rate.prev_rate()
            if prev_rate:
                # Purchase Rate
                if rate.purchase_rate != prev_rate.purchase_rate:
                    if self.all_purchase_rates:
                        purchase_rates = self.all_purchase_rates.filter(
                            date__lte   = rate.date,
                            product     = rate.product,
                            variant     = self.np_rate_variant,
                            amount      = rate.purchase_rate,
                        )
                        if not purchase_rates: self.create_purchase_rate(rate,self.np_rate_variant)
                    else: self.create_purchase_rate(rate,self.np_rate_variant)
                        
                # Selling Rate
                if rate.selling_rate != prev_rate.selling_rate:
                    if self.all_selling_rates:
                        selling_rates = self.all_selling_rates.filter(
                            date__lte   = rate.date,
                            product     = rate.product,
                            variant     = self.ns_rate_variant,
                            amount      = rate.selling_rate,
                        )
                        if not selling_rates: self.create_selling_rate(rate,self.ns_rate_variant)
                    else: self.create_selling_rate(rate,self.ns_rate_variant)
            else:
                self.create_purchase_rate(rate,self.np_rate_variant)
                self.create_selling_rate(rate,self.ns_rate_variant)
        print('Done')
                        
    def add_purchase_rate_to_purchase(self,date):
        print('Adding purchase rate to purchases-',date)
        for purchase in self.all_purchases.filter(date=date):
            if purchase.purchase_rate: continue
            rates = self.all_purchase_rates.filter(
                date__lte   = purchase.date, 
                product     = purchase.product,
                variant__normal =True
            )
            if rates.exists():
                rate = rates.latest()
                if purchase.rate == rate.amount: # normal rate
                    purchase.purchase_rate = rate
                    purchase.save()
                    # print(purchase, rate)
                    continue

            # special_rate_variant = PurchaseRateVariant.objects.get(normal=False)
            special_rates = self.all_purchase_rates.filter(
                date__lte   = purchase.date,
                product     = purchase.product,
                variant     = self.sp_rate_variant,
                amount      = purchase.rate,
            )

            # If no matching rate was found, create a new one
            if special_rates.exists():
                special_rate = special_rates.latest()
            else:
                special_rate = self.create_purchase_rate(purchase, self.sp_rate_variant)
            purchase.purchase_rate = special_rate
            purchase.save()
            # print(purchase, 'Special:', special_rate)

    def add_selling_rate_to_sell(self, date):
        print('Adding selling rate to sell-',date)
        sells = self.all_sells.filter(date=date)
        for sell in sells:
            rates = self.all_selling_rates.filter(
                date__lte   = sell.date,
                product     = sell.product,
                variant__normal=True
            )
            if rates.exists():
                rate = rates.latest()
                if sell.rate == rate.amount: # normal rate
                    sell.selling_rate = rate
                    sell.save()
                    # print(sell,  rate)
                    continue
            # special_rate_variant = SellingRateVariant.objects.get(normal=False)
            special_rates   = self.all_selling_rates.filter(
                date__lte   = sell.date,
                product     = sell.product,
                variant     = self.ss_rate_variant,
                amount      = sell.rate,
            )
            if special_rates.exists():
                special_rate = special_rates.latest()
            else:
                special_rate = self.create_selling_rate(sell, self.ss_rate_variant)
            sell.selling_rate = special_rate
            sell.save()
            # print(sell, 'Special:', special_rate)

    def add_selling_rate_to_duesell(self, date):
        print('Adding selling rate to duesell-',date)
        duesells = self.all_duesells.filter(date=date)
        for duesell in duesells:
            rates = self.all_selling_rates.filter(
                date__lte   = duesell.date,
                product     = duesell.product,
                variant__normal = True
            )
            if rates.exists():
                rate = rates.latest()
                if duesell.rate == rate.amount: # normal rate
                    duesell.selling_rate = rate
                    duesell.save()
                    # print(duesell, rate)
                    continue
            # special_rate_variant = SellingRateVariant.objects.get(normal=False)
            special_rates = self.all_selling_rates.filter(
                date__lte   = duesell.date,
                product     = duesell.product,
                variant     = self.ss_rate_variant,
                amount      = duesell.rate,
            )
            if special_rates.exists():
                special_rate = special_rates.latest()
            else:
                special_rate = self.create_selling_rate(duesell, self.ss_rate_variant)
            duesell.selling_rate = special_rate
            duesell.save()
            # print(duesell, 'Special:', special_rate)

    def add_rate_to_storage_reading(self, date):
        if date>first_balance_date():
            print('Adding rate to storage reading', date)
            for sr in self.storage_readings.filter(date=date):
                sr.get_purchase_rate()
                sr.save()
                # print(sr)
        # except StorageReading.DoesNotExist: pass
    
    def copy_income_expenditure(self):
        print('Copying Income Expenditure')
        IncomeGroup.objects.all().delete()
        Income.objects.all().delete()
        ExpenditureGroup.objects.all().delete()
        Expenditure.objects.all().delete()

        rev_groups = RevenueGroup.objects.all()
        exp_groups = ExpenseGroup.objects.all()
        for obj in rev_groups:
            print(obj)
            group = IncomeGroup.objects.create(name=obj.name,serial=obj.serial)
            revenues = Revenue.objects.filter(group=obj)
            for rev_obj in revenues:
                Income.objects.create(
                    date    = rev_obj.date, 
                    group   = group, 
                    detail  = rev_obj.detail, 
                    amount  = rev_obj.amount
                )
        for obj in exp_groups:
            print(obj)
            group = ExpenditureGroup.objects.create(name=obj.name,serial=obj.serial)
            expenses = Expense.objects.filter(group=obj)
            for exp_obj in expenses:
                Expenditure.objects.create(
                    date    = exp_obj.date, 
                    group   = group, 
                    detail  = exp_obj.detail, 
                    amount  = exp_obj.amount
                )
    
    def update_transactions(self):
        start_date = account_start_date()
        # end_date = datetime.date(2022,12,31)
        # start_date = datetime.date(2023,6,7)
        end_date = datetime.date(2024,8,25)
        while start_date <= end_date:
            print(start_date)
            self.add_purchase_rate_to_purchase(start_date)
            self.add_selling_rate_to_sell(start_date)
            self.add_selling_rate_to_duesell(start_date)
            self.add_rate_to_storage_reading(start_date)
            save_cashbalance(start_date)
            start_date += datetime.timedelta(days=1)

    def active_last_rates(self):
        products = Product.objects.all()
        for product in products:
            np_rates = self.all_purchase_rates.filter(product=product,variant__normal=True)
            if np_rates: 
                np_rate = np_rates.latest()
                np_rate.active = True
                np_rate.save()
                print('Active rate:',np_rate)
            sp_rates = self.all_purchase_rates.filter(product=product,variant__normal=False)
            if sp_rates: 
                sp_rate = sp_rates.latest()
                sp_rate.active = True
                sp_rate.save()
                print('Active rate:',sp_rate)
            ns_rates = self.all_selling_rates.filter(product=product,variant__normal=True)
            if ns_rates: 
                ns_rate = ns_rates.latest()
                ns_rate.active = True
                ns_rate.save()
                print('Active rate:',ns_rate)
            ss_rates = self.all_selling_rates.filter(product=product,variant__normal=False)
            if ss_rates: 
                ss_rate = ss_rates.latest()
                ss_rate.active = True
                ss_rate.save()
                print('Active rate:',ss_rate)

    def migrate(self):
        self.clear_previous()
        self.ensure_rate_variant()
        self.copy_rates()
        self.initialize()
        self.get_all_queries()
        self.update_transactions()
        self.active_last_rates()

fix = Fix()

def delete_oes():
    oes = OwnersEquity.objects.exclude(month=10,year=2022)
    oes.delete()

# set last balance date to Fix.update_transactions().end_date

# CMD: py manage.py shell

# Shell:
"""
from Core.fix import delete_oes, fix
delete_oes()

"""


# CMD: py manage.py migrate
# CMD: py manage.py runserver

# update Business Information
# Update Owners share information
# Update DailyStorage Dec (16-20), 2022 page-42 octen+disel
# Update DailyStorage (16 Jun, 3 July), 2023 page-28,30 disel
# Update DailyStorage (9 July), 2023 page-28,30 omera extra super

# Shell: fix.migrate()
# Shell: exit()

# Delete Product.models.Rate
# Delete Apps: Ledger, Expenditure, Revenue
# Remove year,month from OwnersEquity
# Delete all noted with Remove/Delete

# Migrate Database

# Un-comment save method of BaseIncomeExpenditureGroup
# Un-comment Product.signals methods