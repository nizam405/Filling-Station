from .functions import account_start_date
from Transaction.functions import last_balance_date

MONTHS = [
    (1, 'জানুয়ারি'),
    (2, 'ফেব্রুয়ারি'),
    (3, 'মার্চ'),
    (4, 'এপ্রিল'),
    (5, 'মে'),
    (6, 'জুন'),
    (7, 'জুলাই'),
    (8, 'আগস্ট'),
    (9, 'সেপ্টেম্বর'),
    (10, 'অক্টোবর'),
    (11, 'নভেম্বর'),
    (12, 'ডিসেম্বর'),
]


def balance_years():
    from FillingStation.templatetags.extra_tags import number_in_bangla
    start = account_start_date().year
    end = last_balance_date().year+1
    years = []
    for year in range(start,end):
        years.append((year,number_in_bangla(year)))
    return years
