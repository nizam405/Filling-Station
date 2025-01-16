from Core.models import Settings
from Transaction.functions import last_balance_date
import datetime
from django.conf import settings

def org_settings(request):
    try:
        org_settings = Settings.objects.earliest()
        return {'org_settings': org_settings}
    except: return {}

def current_date(request):
    date = request.META.get('navigation_date', last_balance_date())
    date = datetime.datetime.strftime(date,settings.DATE_FORMAT)
    return {'current_date':date}