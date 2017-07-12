from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse

def current_datetime(request):

    html = "mEun7MAQpQ2z2DgliwH0GLleKV1zK9m1jXCz5N2LL4Q.3fZwQCMRQ4RxEA1i-PFKfqOP73dii7vxDBc6eHOSjaI"
    return HttpResponse(html)