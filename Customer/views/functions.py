from django.urls import reverse
from django.db.models import Sum
from Customer.models import Customer, GroupofCompany, DueSell, DueCollection, CustomerDue, GroupofCompanyDue

def base_customer_ledger_info(from_date,to_date,customer):
    data = {}
    if isinstance(customer, Customer):
        customer_dues = CustomerDue.objects.filter(customer=customer.pk,date=from_date)
        data.update({
            'name'      : customer.name,
            'ledger_url': reverse('customer-ledger',kwargs={'date':to_date,'customer':customer.pk}),
        })
        duesells = DueSell.objects.filter(date__gte=from_date, date__lte=to_date, customer=customer.pk)
        duecollections = DueCollection.objects.filter(date__gte=from_date, date__lte=to_date, customer=customer.pk)
    else:
        customer_dues = GroupofCompanyDue.objects.filter(customer=customer.pk, date=from_date)
        data.update({
            'name'      : "** " + customer.name,
            'ledger_url': reverse('groupofcompany-ledger',kwargs={'date':to_date,'customer':customer.pk}),
        })
        duesells = DueSell.objects.filter(date__gte=from_date, date__lte=to_date, customer__group=customer.pk)
        duecollections = DueCollection.objects.filter(date__gte=from_date, date__lte=to_date, customer__group=customer.pk)
    initial_due = customer_dues.earliest().amount if customer_dues else 0
    data.update({
        'link_css'      : "text-dark",
        'initial_due'   : initial_due,
        'duesell'       : 0,
        'duecollection' : 0,
        'current_due'   : 0,
        'baddebt'       : False,
    })
    if customer_dues:
        if customer_dues.latest().bad_debt: 
            data['baddebt'] = True
            data['link_css'] = "text-secondary"

    if duesells or duecollections: data['baddebt'] = False

    duesell_amount = duesells.aggregate(Sum('price'))['price__sum'] or 0
    data.update({'duesell': duesell_amount})
    
    collection = duecollections.aggregate(Sum('amount'))['amount__sum'] if duecollections else 0
    data.update({ 'duecollection': collection})

    # কোনো কার্যকলাপ না থাকলে টপশিটে আসবে না
    if initial_due != 0 or duesell_amount != 0 or collection != 0:
        current_due = initial_due + duesell_amount - collection
        data.update({'current_due': current_due})
    return data

def get_customer_ledger_info(from_date,to_date):
    dataset = {}
    customers = []
    total_initial_due   = 0
    total_duesell       = 0
    total_collection    = 0
    total_current_due   = 0
    # Group of Companies
    group_of_companies = GroupofCompany.objects.all()
    for goc in group_of_companies:
        data = base_customer_ledger_info(from_date,to_date,goc)
        total_initial_due   += data['initial_due']
        total_duesell       += data['duesell']
        total_collection    += data['duecollection']
        total_current_due   += data['current_due']
        if data['initial_due'] != 0 or data['duesell'] != 0 or data['duecollection'] != 0 or data['current_due'] != 0:
            customers.append(data)
    # Individual Customers
    individual_customers = Customer.objects.filter(cust_type='Individual')
    for customer in individual_customers:
        data = base_customer_ledger_info(from_date,to_date,customer)
        total_initial_due   += data['initial_due']
        total_duesell       += data['duesell']
        total_collection    += data['duecollection']
        total_current_due   += data['current_due']
        if data['initial_due'] != 0 or data['duesell'] != 0 or data['duecollection'] != 0 or data['current_due'] != 0:
            customers.append(data)

    dataset['customers']        = customers
    dataset['customers_total']  = {
        'total_initial_due' : total_initial_due,
        'total_duesell'     : total_duesell,
        'total_collection'  : total_collection,
        'total_current_due' : total_current_due,
    }
    return dataset
