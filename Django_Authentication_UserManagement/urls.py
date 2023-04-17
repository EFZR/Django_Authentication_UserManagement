from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('website.urls')),
    path('', include('django.contrib.auth.urls')),
    path('admin/', admin.site.urls),
]

# django.contrib.auth.urls is a built-in Django app that provides all the URLs, views, and templates needed to handle user authentication,
# including login, logout, password change, and password reset. It also provides a default User model that is built for extensibility.
# This can be found in the django directory in the site-packages folder of your virtual environment.
