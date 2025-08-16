
from django.contrib import admin
from django.urls import path,include


from django.http import JsonResponse

def home(request):
    return JsonResponse({"status": "Job service is running"})






urlpatterns = [
    path('admin/', admin.site.urls),
    path('job/',include('jobs.urls'))
]


urlpatterns += [
    path('', home), 
]
