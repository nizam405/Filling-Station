from django import template

register = template.Library()

@register.filter(name="ezynumber")
def price_separate(price):
    new_str = ""
    price_str = str(price)[::-1]
    if '.' in price_str:
        indx = price_str.index('.')+1
        new_str += price_str[0:indx]
        price_str = price_str[indx:]
    length = len(price_str)
    if length > 3:
        new_str += price_str[0:3] + "," + price_str[3]
        if length == 5: new_str += price_str[4]
        if length > 5:
            new_str += price_str[4] + "," + price_str[5]
            if length == 7: new_str += price_str[6]
            if length > 7:
                new_str += price_str[6] + "," + price_str[7:]
    else:
        return price
    rev = new_str[::-1]
    return rev

@register.filter(name='zip')
def zip_lists(object_list):
    nums = [i for i in range(1,object_list.count()+1)]
    return zip(object_list,nums)

@register.filter(name='formsetNumber')
def formset_number(formset):
    print(len(formset))
    nums = [i for i in range(0,len(formset))]
    return zip(formset,nums)