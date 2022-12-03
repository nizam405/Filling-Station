import datetime

def year_choices():
    return [r for r in range(2020,datetime.date.today().year+1)]

def current_year():
    return datetime.date.today().year