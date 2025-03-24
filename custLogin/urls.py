from django.urls import path
from . import views
from django.shortcuts import render


urlpatterns = [
    path('manager/login/', views.manager_login, name='manager_login'),
    path('manager/dashboard/', views.manager_dashboard, name='manager_dashboard'),

    path('customer/login/', views.customer_login, name='customer_login'),
    path('customer/dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('manager/create-customer', views.create_customer, name='create_customer'),
    path('manager/customer/<int:id>/', views.view_customer, name='view_customer'),
    path('manager/customer/<int:id>/edit', views.edit_customer, name='edit_customer'),
    path('manage/customer/<int:id>/confirm-cashout', views.confirm_cashout, name='confirm_cashout'),
    path('manager/customer/<int:id>/delete/', views.delete_customer, name='delete_customer'),
    path('', lambda request: render(request, 'home.html'), name='home'),

]
