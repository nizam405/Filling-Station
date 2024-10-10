from Core.models import Settings

def business_name(request):
    return {"business_name":"প্রধান ফিলিং স্টেশন"}

def settings(request):
    if Settings.objects.exists():
        settings = Settings.objects.earliest()
        return {'settings': settings}
    else: return None