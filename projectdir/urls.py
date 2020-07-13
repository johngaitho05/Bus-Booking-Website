
from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('super/', admin.site.urls),
    path('', include('app.urls')),
    path('api/', include('mpesa_api.urls')),
]
