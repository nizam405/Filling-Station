import datetime
from django.conf import settings

class DateConverter:
    regex = '\d{1,4}-\d{1,2}-\d{2}'
    format = settings.DATE_FORMAT

    def to_python(self, value:datetime.date):
        # Convert the date string to a date object
        return datetime.datetime.strptime(value, self.format).date()
    
    def to_url(self, value):
        # Ensure value is a datetime object before formatting it
        if isinstance(value, str):
            value = datetime.datetime.strptime(value, self.format)
        return value.strftime(self.format)
