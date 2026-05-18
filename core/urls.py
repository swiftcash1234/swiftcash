from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('apply/', views.apply, name='apply'),
    path('offers/', views.loan_offers, name='offers'),
    path('payment/', views.payment, name='payment'),
    path('privacy/', views.privacy, name='privacy'),
    path('terms/', views.terms, name='terms'),
    path('contact/', views.contact, name='contact'),
    
    # API Endpoints
    path('api/auth/me/', views.get_me, name='get_me'),
    path('api/loan/apply/', views.submit_application, name='submit_application'),
    path('api/loan/offers/', views.get_offers, name='get_offers'),
    path('api/payment/initiate/', views.initiate_payment, name='initiate_payment'),
    path('api/payment/status/', views.check_status, name='check_status'),
    path('api/payment/confirm/', views.confirm_payment, name='confirm_payment'),
]
