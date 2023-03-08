
customer_type = [
    ("Individual", "একক প্রতিষ্ঠান"),
    ("Group", "গ্রুপ"),
]

customer_status = [
    ("active", "সক্রিয়"),
    ("inactive", "নিষ্ক্রিয়"),
]

# def customerDueChoice(model):
#     queryset = model.objects.filter(status='active')
#     group = queryset.values('group').distinct()
#     individuals = queryset.filter(group__isnull=True)
#     queryset = group | individuals
#     print(queryset)
#     return queryset