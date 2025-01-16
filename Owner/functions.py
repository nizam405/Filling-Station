from django.db.models import Sum

from Core.functions import next_day, last_date_of_month, first_date_of_month
from Transaction.functions import get_cashbalance
from Product.views.functions import get_total_ending_stock_amount, monthly_product_category_details
from Product.choices import FUEL, LOOSE_LUBRICANT
from IncomeExpenditure.models import Expenditure, Income
from Owner.models import OwnersEquity, Investment, Withdraw, Owner, Profit, FixedAsset
from Owner.choices import EQUITY_RATE, SPECIFIC_RATE, SPECIFIC_PROFIT
from Loan.models import BorrowLoan, LendLoan, RefundBorrowedLoan, RefundLendedLoan
from Customer.views.functions import get_customer_ledger_info

def generate_net_profit(from_date,to_date):
    context = {}
    products_info = monthly_product_category_details(from_date,to_date)
    category_details = products_info['category_details']
    context['products_all_cat'] = category_details
    context['products_total'] = products_info['total']

    ending_stock = products_info['total']['ending_stock']
    total_profit = products_info['total']['sell_profit']
    context['ending_stock'] = ending_stock

    # Excess/Shortage
    for category,details in category_details.items():
        if category==FUEL or category==LOOSE_LUBRICANT:
            for data in details['dataset']:
                if 'ending_stock_diff' in data:
                    diff = data['ending_stock_diff']['price']
                    total_profit += diff
    # diff = sum(data['ending_stock_diff'].price for data in category_details.items())
    # print(diff)
    
    # Incomes
    incomes = Income.objects.filter(date__gte=from_date,date__lte=to_date).order_by('group')
    income_groups = incomes.values('group__name').annotate(amount=Sum('amount'))
    income_amount = incomes.aggregate(Sum('amount'))['amount__sum'] if incomes else 0
    context['income_groups'] = income_groups
    # context['income_amount'] = income_amount
    total_income = total_profit + income_amount
    context['total_income'] = total_income

    # Expenditures
    expenditures = Expenditure.objects.filter(date__gte=from_date,date__lte=to_date).order_by('group')
    exp_groups = expenditures.values('group__name').annotate(exp_amount=Sum('amount'))
    expenditure_amount = expenditures.aggregate(Sum('amount'))['amount__sum'] if expenditures else 0
    context['expenditures'] = exp_groups
    context['expenditure_amount'] = expenditure_amount

    # Totals
    net_profit = total_income - expenditure_amount
    context['net_profit'] = net_profit
    Profit.objects.update_or_create(date=to_date, defaults={'amount':net_profit})
    return context
    
def generate_owner_equity(total_oe,owner,owner_profit,to_date,ownersequity,investments,withdraws):
    owner_info = {'owner':owner}
    # প্রারম্ভিক মূলধন
    current_oes = ownersequity.filter(owner=owner)
    current_oe_amount = current_oes.latest().amount if current_oes else 0
    owner_info['prev_oe'] = current_oe_amount
    owner_info['profit'] = owner_profit
    
    # অতিরিক্ত মূলধন
    owner_investments = investments.filter(owner=owner)
    owner_investment = owner_investments.aggregate(Sum('amount'))['amount__sum'] if owner_investments else 0
    owner_info['investment'] = owner_investment
    
    # উত্তোলন
    wds = withdraws.filter(owner=owner)
    wd_amount = wds.aggregate(Sum('amount'))['amount__sum'] if wds else 0
    owner_info['withdraw'] = wd_amount
    
    # সমাপনী মূলধন
    owner_info['rem_profit'] = owner_profit - wd_amount
    ending_oe_amount = current_oe_amount + owner_investment - wd_amount + owner_profit
    owner_info['ending_oe_amount'] = ending_oe_amount
    ending_share = (ending_oe_amount*100)/total_oe if total_oe else 0
    owner_info['ending_share'] = ending_share
    if to_date == last_date_of_month(to_date):
        current_oe = current_oes.latest()
        current_oe.profit = owner_profit
        current_oe.save()
        OwnersEquity.objects.update_or_create(
            date    = next_day(to_date),
            owner   = owner,
            defaults= {
                'amount': ending_oe_amount, 
                'share' : ending_share,
            }
        )
    return owner_info

def generate_owners_equity(from_date,to_date):
    # মালিকানা স্বত্ব বিবরণী
    net_profit = Profit.objects.get(date=to_date).amount
    context = {}
    # হাতে নগদ
    cash = get_cashbalance(to_date)
    context['cash'] = cash

    # দেনাদার
    customer_dues = get_customer_ledger_info(from_date,to_date)['customers_total']['total_current_due']
    context['dues'] = customer_dues
    # দেনাদার - প্রদত্ত হাওলাদ এর বকেয়া
    lended_loans = LendLoan.objects.filter(date__lte=to_date)
    lended_amount = lended_loans.aggregate(Sum('amount'))['amount__sum'] if lended_loans else 0
    refund_lended_loans = RefundLendedLoan.objects.filter(date__lte=to_date)
    refund_lended_loan_amount = refund_lended_loans.aggregate(Sum('amount'))['amount__sum'] if refund_lended_loans else 0
    remaining_lended_loan = lended_amount - refund_lended_loan_amount
    context['remaining_lended_loan'] = remaining_lended_loan
    # সমাপনি মূলধন
    ending_stock = get_total_ending_stock_amount(from_date,to_date)
    # স্থায়ী সম্পত্তি
    fixed_assets = FixedAsset.objects.filter(date__lte=to_date)
    fixed_assets_amount = fixed_assets.aggregate(Sum('price'))['price__sum'] if fixed_assets else 0
    context['fixed_assets'] = fixed_assets_amount
    
    # মোট সম্পদ
    total_asset = cash + customer_dues + remaining_lended_loan + ending_stock + fixed_assets_amount

    # প্রারম্ভিক মূলধন
    capital_amount = 0
    ownersequity = OwnersEquity.objects.filter(date=from_date)
    capital_amount = ownersequity.aggregate(Sum('amount'))['amount__sum'] if ownersequity else 0
    context['capital'] = capital_amount
    # অতিরিক্ত মূলধন
    investments = Investment.objects.filter(date__gte=from_date, date__lte=to_date)
    investment_amount = investments.aggregate(Sum('amount'))['amount__sum'] if investments else 0

    # উত্তোলন
    withdraws = Withdraw.objects.filter(date__gte=from_date, date__lte=to_date)
    withdraw_amount = withdraws.aggregate(Sum('amount'))['amount__sum'] if withdraws else 0
    context['withdraws'] = -withdraw_amount
    context['rem_profit'] = net_profit - withdraw_amount
    # পাওনাদার - পাপ্ত হাওলাদ এর বকেয়া
    borrowed_loans = BorrowLoan.objects.filter(date__lte=to_date)
    borrowed_amount = borrowed_loans.aggregate(Sum('amount'))['amount__sum'] if borrowed_loans else 0
    refund_borrowed_loans = RefundBorrowedLoan.objects.filter(date__lte=to_date)
    refund_borrowed_loan_amount = refund_borrowed_loans.aggregate(Sum('amount'))['amount__sum'] if refund_borrowed_loans else 0
    remaining_borrowed_loan = borrowed_amount - refund_borrowed_loan_amount
    context['remaining_borrowed_loan'] = remaining_borrowed_loan

    total_oe = capital_amount + remaining_borrowed_loan + investment_amount - withdraw_amount + net_profit
    context['total_oe'] = total_oe

    diff = int(total_oe-total_asset)
    context['diff'] = diff
    total_asset += diff
    context['total_asset'] = total_asset
    # Distribute Profit
    if diff == 0:
        owners = Owner.objects.filter(date_created__lte=from_date)
        remaining_profit = net_profit
        profit_dist = []

        # Distribute Profit to Specific Profit Owners
        specific_profit_owners = owners.filter(profit_share_category=SPECIFIC_PROFIT)
        for owner in specific_profit_owners:
            owner_profit = owner.profit
            owner_info = generate_owner_equity(
                total_oe    = total_oe,
                owner       = owner,
                owner_profit= owner_profit,
                to_date     = to_date,
                ownersequity= ownersequity,
                investments = investments,
                withdraws   = withdraws
            )
            remaining_profit -= owner_profit
            profit_dist.append(owner_info)

        # Distribute Profit to Specific Rate Owners
        specific_eq_owners = owners.filter(profit_share_category=SPECIFIC_RATE)
        for owner in specific_eq_owners:
            owner_profit = net_profit*owner.profit_share
            owner_info = generate_owner_equity(
                total_oe    = total_oe,
                owner       = owner,
                owner_profit= owner_profit,
                to_date     = to_date,
                ownersequity= ownersequity,
                investments = investments,
                withdraws   = withdraws
            )
            remaining_profit -= owner_profit
            profit_dist.append(owner_info)

        # Distribute Profit to Equity Rate Owners
        equity_rate_owners = owners.filter(profit_share_category=EQUITY_RATE)
        for owner in equity_rate_owners:
            prev_oe = ownersequity.filter(owner=owner)
            if prev_oe:
                # এই পদ্ধতিতে মাসের মাঝে কেউ মূলধন দিয়ে যুক্ত হলে, সে চলতিমাসের মুনাফা পাবে না
                owner_profit = prev_oe.share/100 if prev_oe.share else 0
                owner_info = generate_owner_equity(
                    total_oe    = total_oe,
                    owner       = owner,
                    owner_profit= owner_profit,
                    to_date     = to_date,
                    ownersequity= ownersequity,
                    investments = investments,
                    withdraws   = withdraws
                )
                profit_dist.append(owner_info)
        context['profit_distribution'] = profit_dist
    return context
