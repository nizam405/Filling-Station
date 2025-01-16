from django.db.models import Sum
from .models import Customer, GroupofCompany, CustomerDue, GroupofCompanyDue, DueSell, DueCollection
from .choices import INDIVIDUAL
from Core.functions import next_day

def get_remaining_due(from_date,to_date,customer):
    if isinstance(customer, Customer):
        prev_dues = CustomerDue.objects.filter(date=from_date, customer=customer)
        due_sells = DueSell.objects.filter(date__gte=from_date,date__lte=to_date, customer=customer)
        due_collections = DueCollection.objects.filter(date__gte=from_date,date__lte=to_date, customer=customer)
    else:
        prev_dues = GroupofCompanyDue.objects.filter(date=from_date,customer=customer)
        due_sells = DueSell.objects.filter(date__gte=from_date,date__lte=to_date, customer__group=customer)
        due_collections = DueCollection.objects.filter(date__gte=from_date,date__lte=to_date, customer__group=customer)

    prev_due = prev_dues.last() if prev_dues else None
    prev_amount = prev_due.amount if prev_due else 0

    due_sell_amount = due_sells.aggregate(Sum('price'))['price__sum'] or 0
    due_collection_amount = due_collections.aggregate(Sum('amount'))['amount__sum'] or 0
    amount = prev_amount + due_sell_amount - due_collection_amount
    bad_debt = prev_due.bad_debt if prev_due else False
    return (amount,bad_debt)

def base_save_customer_dues(from_date,to_date,customer,DueModel:CustomerDue|GroupofCompanyDue):
    amount,bad_debt = get_remaining_due(from_date,to_date,customer)
    if amount != 0:
        DueModel.objects.create(
            date    = next_day(to_date), 
            customer= customer, 
            amount  = amount,
            bad_debt= bad_debt
        )

def save_customer_dues(from_date,to_date):
    customers = Customer.objects.filter(cust_type=INDIVIDUAL)
    for customer in customers:
        base_save_customer_dues(from_date,to_date,customer,CustomerDue)
    group_of_conpanies = GroupofCompany.objects.all()
    for goc in group_of_conpanies:
        base_save_customer_dues(from_date,to_date,goc,GroupofCompanyDue)