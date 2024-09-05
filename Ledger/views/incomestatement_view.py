from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.db.models import Sum
import datetime
from django.contrib.auth.mixins import LoginRequiredMixin

from Expenditure.models import Expenditure
from Revenue.models import Revenue
from Ledger.models import CustomerBalance, GroupofCompanyBalance, Profit
from Ledger.forms import DateFilterForm
from Transaction.models import CashBalance
from Customer.models import DueSell, DueCollection
from Owner.models import Withdraw, OwnersEquity, Owner, Investment, FixedAsset
from Loan.models import BorrowLoan, LendLoan, RefundBorrowedLoan, RefundLendedLoan
from Ledger.functions import get_products_info
from Core.choices import last_day_of_month

class IncomeStatementView(LoginRequiredMixin,TemplateView):
    template_name = 'Ledger/incomestatement.html'

    def get(self, request, *args, **kwargs):
        # maintain cashbalance date to avoid blank page
        if CashBalance.objects.count() > 1:
            first_bal_date = CashBalance.objects.order_by('date').first().date
            last_bal_date = CashBalance.objects.order_by('date').last().date

            first_date = datetime.date(first_bal_date.year,first_bal_date.month,1)
            first_date = first_date + datetime.timedelta(days=31)
        else:
            return redirect('daily-transactions')

        if 'month' in self.request.GET and 'year' in self.request.GET:
            self.kwargs['month'] = int(self.request.GET['month'])
            self.kwargs['year'] = int(self.request.GET['year'])
        elif 'month' not in self.kwargs and 'year' not in self.kwargs:
            self.kwargs['month'] = last_bal_date.month
            self.kwargs['year'] = last_bal_date.year
        month = self.kwargs['month']
        year = self.kwargs['year']
        
        target_date = datetime.date(year,month,1)
        prev_month_date = target_date - datetime.timedelta(days=1)
        # For very first time
        if last_bal_date.year == first_bal_date.year and last_bal_date.month == first_bal_date.month:
            target_date = first_bal_date + datetime.timedelta(days=1)
            prev_month_date = first_bal_date - datetime.timedelta(days=first_bal_date.day)
        self.kwargs['target_date'] = target_date
        # Dont let go future
        if target_date > last_bal_date:
            return redirect('incomestatement', month=last_bal_date.month, year=last_bal_date.year)
        elif target_date <= first_bal_date:
            return redirect('incomestatement', month=first_date.month, year=first_date.year)

        self.kwargs['prev_month'] = prev_month_date.month
        self.kwargs['prev_month_year'] = prev_month_date.year
        # here num_days+7 to make sure it goes to next month
        next_date = target_date + datetime.timedelta(days=31)
        self.kwargs['next_date'] = next_date
        next_month_1st = datetime.date(next_date.year,next_date.month,1)
        last_day_month = next_month_1st - datetime.timedelta(days=1)

        # Status: compare cashbalance date == last_day_month
        cashbalance = CashBalance.objects.filter(date__year=year,date__month=month).order_by('date').last()
        to_date = cashbalance.date
        self.kwargs['to_date'] = to_date
        self.kwargs['status'] = to_date == last_day_month
        self.kwargs['last_bal_date'] = last_bal_date

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = DateFilterForm(self.request.GET or self.kwargs or None)
        context['date_form'] = form
        context['month'] = self.kwargs['month']
        context['year'] = self.kwargs['year']
        context['prev'] = {
            'month': self.kwargs['prev_month'],
            'year': self.kwargs['prev_month_year']
        }
        context['next'] = {
            'month': self.kwargs['next_date'].month,
            'year': self.kwargs['next_date'].year
        }
        context['status'] = self.kwargs['status']
        context['last_bal_date'] = self.kwargs['last_bal_date']

        month = int(self.kwargs['month'])
        year = int(self.kwargs['year'])
        prev_month = self.kwargs['prev_month']
        prev_month_year = self.kwargs['prev_month_year']
        from_date = self.kwargs['target_date']
        to_date = self.kwargs['to_date']

        # Products Info
        product_info, total_profit, total_profit_diff = get_products_info(year,month)
        context['total_profit'] = total_profit
        loose_products = [product for product in product_info if product['product'].type == 'Loose']
        context['loose_products'] = loose_products
        pack_products = [product for product in product_info if product['product'].type == 'Pack']
        pack_qnt = sum(product['sell_qnt'] for product in pack_products)
        pack_profit = sum(product['profit'] for product in pack_products)
        context['pack_product'] = {
            'qnt': pack_qnt,
            'profit': pack_profit,
        }
        ex_products = [product for product in product_info if product['ending_storage_diff'] != 0]
        ex_revenue = sum(product['ending_storage_diff_amount'] for product in ex_products if product['ending_storage_diff']>0)
        ex_loss = sum(product['ending_storage_diff_amount'] for product in ex_products if product['ending_storage_diff']<0)
        context['ex_products'] = ex_products

        # Profit Adjustment
        context['total_profit_diff'] = total_profit_diff
        
        # Revenues
        revenues = Revenue.objects.filter(date__gte=from_date,date__lte=to_date).order_by('group')
        rev_groups = revenues.values('group__name').annotate(rev_amount=Sum('amount'))
        revenue_amount = revenues.aggregate(Sum('amount'))['amount__sum'] if revenues else 0
        context['revenues'] = rev_groups
        context['revenue_amount'] = revenue_amount
        total_income = total_profit + revenue_amount + ex_revenue
        context['total_income'] = total_income

        # Expenditures
        expenditures = Expenditure.objects.filter(date__gte=from_date,date__lte=to_date).order_by('group')
        exp_groups = expenditures.values('group__name').annotate(exp_amount=Sum('amount'))
        expenditure_amount = expenditures.aggregate(Sum('amount'))['amount__sum'] if expenditures else 0
        expenditure_amount += abs(ex_loss)
        context['expenditures'] = exp_groups
        context['expenditure_amount'] = expenditure_amount

        # Totals
        net_profit = total_income - expenditure_amount
        context['net_profit'] = net_profit
        saved_profit, created = Profit.objects.update_or_create(
            year=year, month=month, defaults={'amount':net_profit}
        )

        # মালিকানা স্বত্ব বিবরণী
        # হাতে নগদ
        cash = CashBalance.objects.get(date=to_date).amount
        context['cash'] = cash

        # দেনাদার
        dues = 0
            # Prev Balances
        prev_cust_balances = CustomerBalance.objects.filter(month=prev_month, year=prev_month_year,customer__group__isnull=True)
        prev_cust_balances_amount = prev_cust_balances.aggregate(Sum('amount'))['amount__sum'] if prev_cust_balances else 0
        dues += prev_cust_balances_amount
        prev_goc_balances = GroupofCompanyBalance.objects.filter(month=prev_month, year=prev_month_year)
        prev_goc_balances_amount = prev_goc_balances.aggregate(Sum('amount'))['amount__sum'] if prev_goc_balances else 0
        dues += prev_goc_balances_amount
            # Due sells
        due_sells = DueSell.objects.filter(date__gte=from_date,date__lte=to_date)
        dues += due_sells.aggregate(Sum('amount'))['amount__sum'] if due_sells else 0
            # Due collections
        due_collections = DueCollection.objects.filter(date__gte=from_date,date__lte=to_date)
        dues -= due_collections.aggregate(Sum('amount'))['amount__sum'] if due_collections else 0
        context['dues'] = dues
        # দেনাদার - প্রদত্ত হাওলাদ এর বকেয়া
        lended_loans = LendLoan.objects.filter(date__lte=to_date)
        lended_amount = lended_loans.aggregate(Sum('amount'))['amount__sum'] if lended_loans else 0
        refund_lended_loans = RefundLendedLoan.objects.filter(date__lte=to_date)
        refund_lended_loan_amount = refund_lended_loans.aggregate(Sum('amount'))['amount__sum'] if refund_lended_loans else 0
        remaining_lended_loan = lended_amount - refund_lended_loan_amount
        context['remaining_lended_loan'] = remaining_lended_loan
        # স্থায়ী সম্পত্তি
        fixed_assets = FixedAsset.objects.all()
        fixed_assets_amount = fixed_assets.aggregate(Sum('price'))['price__sum'] if fixed_assets else 0
        context['fixed_assets'] = fixed_assets_amount
        # সমাপনী মজুদ
        ending_storage_amount = 0
        ending_storage_amount = sum(product['ending_storage_amount'] for product in product_info)
        # print('ending storage amount', ending_storage_amount)
        ending_storage_amount += ex_revenue + ex_loss
        context['ending_storage_amount'] = ending_storage_amount
        
        total_asset = cash + dues + remaining_lended_loan + ending_storage_amount + fixed_assets_amount

        # প্রারম্ভিক মূলধন
        capital_amount = 0
        ownersequity = OwnersEquity.objects.filter(month=prev_month,year=prev_month_year)
        if ownersequity:
            capital_amount = ownersequity.aggregate(Sum('amount'))['amount__sum']
        context['capital'] = capital_amount
        # অতিরিক্ত মূলধন
        investments = Investment.objects.filter(date__gte=from_date, date__lte=to_date)
        investment_amount = investments.aggregate(Sum('amount'))['amount__sum'] if investments else 0
        # উত্তোলন
        withdraws = Withdraw.objects.filter(date__gte=from_date, date__lte=to_date)
        withdraw_amount = withdraws.aggregate(Sum('amount'))['amount__sum'] if withdraws else 0
        context['withdraws'] = withdraw_amount
        context['rem_profit'] = net_profit - withdraw_amount
        # পাওনাদার - পাপ্ত হাওলাদ এর বকেয়া
        borrowed_loans = BorrowLoan.objects.filter(date__lte=to_date)
        borrowed_amount = borrowed_loans.aggregate(Sum('amount'))['amount__sum'] if borrowed_loans else 0
        refund_borrowed_loans = RefundBorrowedLoan.objects.filter(date__lte=to_date)
        refund_borrowed_loan_amount = refund_borrowed_loans.aggregate(Sum('amount'))['amount__sum'] if refund_borrowed_loans else 0
        remaining_borrowed_loan = borrowed_amount - refund_borrowed_loan_amount
        context['remaining_borrowed_loan'] = remaining_borrowed_loan

        amount_before_profit = capital_amount + remaining_borrowed_loan + investment_amount - withdraw_amount
        total_oe = amount_before_profit + net_profit
        context['total_oe'] = total_oe

        diff = total_asset-total_oe
        context['diff'] = int(diff)
        total_asset -= diff
        context['total_asset'] = total_asset

        # Distribute Profit
        if total_asset == total_oe:
            owners = Owner.objects.all()
            profit_dist = []
            owner_profit = net_profit/2

            for owner in owners:
                owner_info = {'owner':owner}
                # প্রারম্ভিক মূলধন
                prev_oe = ownersequity.filter(owner=owner)
                prev_oe_amount = prev_oe.last().amount if prev_oe else 0
                owner_info['prev_oe'] = prev_oe_amount
                owner_info['profit'] = owner_profit
                
                # অতিরিক্ত মূলধন
                owner_investments = investments.filter(owner=owner)
                owner_investment = owner_investments.aggregate(Sum('amount'))['amount__sum'] if owner_investments else 0
                owner_info['investment'] = owner_investment
                
                # উত্তোলন
                wds = withdraws.filter(owner=owner)
                wd_amount = wds.aggregate(Sum('amount'))['amount__sum'] if wds else 0
                owner_info['withdraw'] = wd_amount
                
                # বর্তমান মালিকানা
                owner_info['rem_profit'] = owner_profit - wd_amount
                current_oe = prev_oe_amount + owner_investment - wd_amount + owner_profit
                owner_info['current_oe'] = current_oe
                current_share = (current_oe*100)/total_oe if total_oe else 0
                owner_info['current_share'] = current_share

                profit_dist.append(owner_info)

                oe, create = OwnersEquity.objects.update_or_create(
                    month=month,year=year,owner=owner,
                    defaults={'profit':owner_profit,'amount':current_oe, 'share':current_share})
            context['profit_distribution'] = profit_dist
        return context

class ProfitAdjustment(LoginRequiredMixin,TemplateView):
    template_name = 'Ledger/profit_adjustment.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        month = self.kwargs['month']
        year = self.kwargs['year']
        context['month'] = month
        context['year'] = year
        last_bal_date = CashBalance.objects.latest().date
        context['last_bal_date'] = last_bal_date
        to_date = last_day_of_month(year,month)
        if last_bal_date <= to_date: context['status'] = True
        product_info, total_profit, total_profit_diff = get_products_info(year,month)
        context['product_info'] = product_info
        context['total_profit_diff'] = total_profit_diff
        return context
    