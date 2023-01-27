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