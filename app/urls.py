
from django.urls import path
from . import views

urlpatterns = [
    path('',views.home_view, name='home'),
    path('booking',views.booking_view, name='booking'),
    path('logout',views.logout_view, name='logout'),
    path('login',views.login_view,name='login'),
    path('signup', views.signup_view,name='signup'),
    path('payment',views.payment_view, name='payment'),
    path('change-password',views.update_password, name='change_password'),
    path('profile',views.update_user, name='update_user'),

]
