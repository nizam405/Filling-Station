from django.forms import Select

class SelectProduct(Select):
    def create_option(self, name, value, label, selected, index, subindex, attrs):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)

        if value:
            option['attrs']['purchase_rate'] = value.instance.purchase_rate
            option['attrs']['selling_rate'] = value.instance.selling_rate
        return option