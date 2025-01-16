import datetime
import calendar
from django.contrib.contenttypes.models import ContentType
from django.db.models.fields.related import ManyToOneRel, ManyToManyRel
from Transaction.functions import last_balance_date_of_month

def account_start_date():
    from .models import Settings
    try:
        return Settings.objects.first().start_date
    except: return datetime.date.today()

def next_day(current_date):
    return current_date + datetime.timedelta(days=1)

def prev_day(current_date):
    return current_date - datetime.timedelta(days=1)

def current_year():
    return datetime.date.today().year

def first_date_of_month(date:datetime.date):
    return datetime.date(date.year,date.month,1)

def prev_month(date:datetime.date):
    first_date = first_date_of_month(date)
    prev = first_date - datetime.timedelta(days=1)
    return prev

def next_month(date:datetime.date):
    first_date = datetime.date(date.year,date.month,1)
    next_month_date = first_date + datetime.timedelta(days=31)
    return first_date_of_month(next_month_date)

def last_date_of_month(date:datetime.date):
    next_month_date = next_month(date)
    return next_month_date - datetime.timedelta(days=1)

def accounts_dates_in_month(from_date,to_date=None):
    from_date = first_date_of_month(from_date)
    end = last_balance_date_of_month(from_date)
    if to_date and to_date<end:
        end = to_date
    dates = []
    while from_date <= end:
        dates.append(from_date)
        from_date += datetime.timedelta(days=1)
    return dates

def all_dates_in_month(year, month):
    cal = calendar.monthcalendar(year, month)
    all_dates = [datetime.date(year, month, day) for week in cal for day in week if day != 0]
    return all_dates

def year_choices():
    return [r for r in range(2000,datetime.date.today().year+1)]

# Remove
def get_next_month(year,month):
    next_month_date = datetime.date(year,month,1) + datetime.timedelta(days=31)
    return (next_month_date.year, next_month_date.month)

def last_day_of_month(year,month):
    year, month = get_next_month(year,month)
    next_month_first_date = datetime.date(year,month,1)
    target_date = next_month_first_date - datetime.timedelta(days=1)
    return target_date

def get_prev_month(year,month):
    first_date = datetime.date(int(year),int(month),1)
    prev_date = first_date - datetime.timedelta(days=1)
    return (prev_date.year,prev_date.month)
# ----------------


# ------------------------------
def get_all_related_objects(obj):
    """
    Get all related objects for a given model instance.
    """
    content_type = ContentType.objects.get_for_model(obj)
    related_objects = []

    # Loop through all related fields in the model
    for relation in content_type.model_class()._meta.get_fields():
        # Only process reverse relations (ManyToOneRel, ManyToManyRel)
        if isinstance(relation, (ManyToOneRel, ManyToManyRel)):
            # Get the reverse accessor name for the related field
            related_field_name = relation.get_accessor_name()

            try:
                # Use the reverse accessor to get related objects
                related_query = getattr(obj, related_field_name).all()
                
                # Check if there are objects related to this field
                if related_query.exists():
                    related_objects.extend(related_query)  # Add found related objects
            except AttributeError as e:
                print(f"AttributeError: {e} for {obj} on field {related_field_name}")
            except Exception as e:
                print(f"Unexpected error: {e} for {obj} on field {related_field_name}")

    return related_objects