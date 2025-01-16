import datetime
from pybengali import convert_e2b_digit as e2b

today = datetime.date.today()
currentMonth = today.month
prevMonth = 12 if today.month == 1 else today.month-1

firstYear = 2022
currentYear = today.year
YEAR = [(i,e2b(i)) for i in range(firstYear, currentYear+1)]