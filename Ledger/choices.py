import datetime
from pybengali import convert_e2b_digit as e2b

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

today = datetime.date.today()
currentMonth = today.month
prevMonth = 12 if today.month == 1 else today.month-1

firstYear = 2022
currentYear = today.year
YEAR = [(i,e2b(i)) for i in range(firstYear, currentYear+1)]