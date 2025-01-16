from django.forms import Select
from Customer.models import DueCollection, DueSell
from Ledger.models import GroupofCompanyBalance, CustomerBalance
from django.db.models import Sum
import json

class SelectProduct(Select):
    def create_option(self, name, value, label, selected, index, subindex, attrs):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)

        if value:
            product = value.instance
            active_purchase_rates = product.purchaserate_set.filter(active=True)
            active_selling_rates = product.sellingrate_set.filter(active=True)
            if active_purchase_rates:
                pur_rates = [{"value":rate.pk, "amount":rate.amount, "normal":rate.variant.normal} for rate in active_purchase_rates]
                option['attrs']['purchase_rates'] = json.dumps(pur_rates)
            if active_selling_rates:
                sel_rates = [{"value":rate.pk, "amount":rate.amount, "normal":rate.variant.normal} for rate in active_selling_rates]
                option['attrs']['selling_rates'] = json.dumps(sel_rates)
        return option

# class SelectCustomer(Select):
#     def create_option(self, name, value, label, selected, index, subindex, attrs):
#         option = super().create_option(name, value, label, selected, index, subindex, attrs)

#         if value:
#             # value.instance is customer object
#             if value.instance.cust_type == 'Group':
#                 balances = GroupofCompanyBalance.objects.filter(customer=value.instance.group)
#                 sells = DueSell.objects.filter(customer__group=value.instance.group)
#                 collections = DueCollection.objects.filter(customer__group=value.instance.group)
#             else:
#                 balances = CustomerBalance.objects.filter(customer=value.instance)
#                 sells = DueSell.objects.filter(customer=value.instance)
#                 collections = DueCollection.objects.filter(customer=value.instance)
#             # get sum
#             balance = balances.last().amount if balances else 0
#             due = sells.aggregate(Sum('amount'))['amount__sum'] if sells else 0
#             due += balance
#             collection_amount = collections.aggregate(Sum('amount'))['amount__sum'] if collections else 0
#             # Add attributes
#             option['attrs']['due'] = due
#             option['attrs']['collection'] = collection_amount
#         return option