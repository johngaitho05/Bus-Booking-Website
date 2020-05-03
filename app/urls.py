from django.urls import path
from . import views

urlpatterns = [
    path('logout/', views.logout_view, name='logout'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('', views.home_view, name='home'),
    path('booking/', views.booking_view, name='booking'),
    path('booking/get-destinations/', views.get_destinations),
    path('booking/summary', views.summary, name='summary'),
    path('payment/<int:booking_id>', views.payment_view, name='payment'),
    path('change-password/', views.update_password, name='change_password'),
    path('profile/', views.update_user, name='update_user'),
    path('booking/check-seats/', views.check_seats, name='check_seats'),

]
