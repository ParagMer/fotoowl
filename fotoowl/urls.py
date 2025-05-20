"""
URL configuration for fotoowl project.

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
from django.contrib import admin
from django.urls import path
from fotoowl_app.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/create/', users_register.as_view(), name='users-register'),
    path('users/login/', users_login.as_view(), name='users-login'),
    path('users/listing/', UserListAPIView.as_view(), name='user-list'),
    path('book/list/', BookListAPIView.as_view(), name='book-create'),
    path('book/toborrow/', BookToBorrow.as_view(), name='book-borrow'),
    path('book/borrow/request/', BookBorrowRequest.as_view(), name='book-borrow-request'),
    path('book/borrow/history/', BookBorrowHistory.as_view(), name='book-borrow-history'),
]
