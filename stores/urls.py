"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path

from stores.views import PublicStoreListAPI, PrivateStoreListAPI, MyStoreListAPI, PrepayIsValidAPI

urlpatterns = [
    path('public/', PublicStoreListAPI.as_view()),
    path('private/', PrivateStoreListAPI.as_view()),
    path('me/', MyStoreListAPI.as_view()),
    path('prepay/is_valid/', PrepayIsValidAPI.as_view()),
]
