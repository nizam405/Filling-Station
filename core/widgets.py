from django.forms import Select, ModelChoiceField
from Customer.models import DueCollection, DueSell
from Ledger.models import GroupofCompanyBalance, CustomerBalance, BadDebt
from django.db.models import Sum

class SelectProduct(Select):
    def create_option(self, name, value, label, selected, index, subindex, attrs):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)

        if value:
            option['attrs']['purchase_rate'] = value.instance.purchase_rate
            option['attrs']['selling_rate'] = value.instance.selling_rate
        return option

class SelectCustomer(Select):
    def create_option(self, name, value, label, selected, index, subindex, attrs):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)

        if value:
            # value.instance is customer object
            if value.instance.cust_type == 'Group':
                balances = GroupofCompanyBalance.objects.filter(customer=value.instance.group)
                sells = DueSell.objects.filter(customer__group=value.instance.group)
                collections = DueCollection.objects.filter(customer__group=value.instance.group)
                baddebts = BadDebt.objects.filter(customer__group=value.instance.group)
            else:
                balances = CustomerBalance.objects.filter(customer=value.instance)
                sells = DueSell.objects.filter(customer=value.instance)
                collections = DueCollection.objects.filter(customer=value.instance)
                baddebts = BadDebt.objects.filter(customer=value.instance)
            # get sum
            balance = balances.last().amount if balances else 0
            baddebt = baddebts.aggregate(Sum('amount'))['amount__sum'] if baddebts else 0
            balance -= baddebt
            due = sells.aggregate(Sum('amount'))['amount__sum'] if sells else 0
            due += balance
            collection_amount = collections.aggregate(Sum('amount'))['amount__sum'] if collections else 0
            # Add attributes
            option['attrs']['due'] = due
            option['attrs']['collection'] = collection_amount
        return option