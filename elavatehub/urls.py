from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('elavateapp.urls')),  # Use include to link to the app's URLs
]
