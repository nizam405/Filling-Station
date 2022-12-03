from django import template

register = template.Library()

@register.filter(name='zip')
def zip_lists(object_list):
    nums = [i for i in range(1,object_list.count()+1)]
    return zip(object_list,nums)


