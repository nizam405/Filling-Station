from .models import CashBalance

def has_cashbalance(request):
    has_data = CashBalance.objects.exists()
    return {'has_cashbalance': has_data}

# def current_date(request):
#     date = request.