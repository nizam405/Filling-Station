import datetime
import calendar

def all_dates_in_month(year, month):
    cal = calendar.monthcalendar(year, month)
    all_dates = [datetime.date(year, month, day) for week in cal for day in week if day != 0]
    return all_dates

def year_choices():
    return [r for r in range(2020,datetime.date.today().year+1)]

def current_year():
    return datetime.date.today().year

def next_month(year,month):
    first_date = datetime.date(year,month,1)
    next_month_date = first_date + datetime.timedelta(days=31)
    return (next_month_date.year, next_month_date.month)

def last_day_of_month(year,month):
    year, month = next_month(year,month)
    next_month_first_date = datetime.date(year,month,1)
    target_date = next_month_first_date - datetime.timedelta(days=1)
    return target_date

def get_prev_month(year,month):
    first_date = datetime.date(int(year),int(month),1)
    prev_date = first_date - datetime.timedelta(days=1)
    return (prev_date.year,prev_date.month)