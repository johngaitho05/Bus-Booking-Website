from datetime import datetime, date, time, timedelta
import time

import pytz
from django.http.response import JsonResponse, Http404
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.timezone import make_aware
from django.views.decorators.csrf import csrf_exempt

from .models import Profile, Route, Booking
from mpesa_api.mpesa_credentials import LipanaMpesaPassword
from django.contrib.auth import authenticate, logout, login
import re
from django.contrib import messages


def loginRequired(func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        return func(request, *args, **kwargs)

    return wrapper


def check_authentication(func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        return func(request, *args, **kwargs)

    return wrapper


@check_authentication
def login_view(request):
    if request.method == 'POST':
        if request.POST['username'] and request.POST['password']:
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    if request.POST['where_to']:
                        return redirect(str(request.POST['where_to']))
                    else:
                        return redirect('home')
                else:
                    # print 'The password is valid,but the account has been disabled'
                    return render(request, 'app/index.html',
                                  {'view': 'login', 'login_waring': 'Your account has been suspended'})
            else:
                return render(request, 'app/index.html',
                              {'view': 'login', 'login_warning': 'Invalid username or password'})
    return render(request, 'app/index.html', {'view': 'login'})


@check_authentication
def signup_view(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        number = request.POST['phone']
        if first_name and last_name and email and password1 and password2:
            if request.POST['password1'] == request.POST['password2']:
                try:
                    phone_number = format_number(request.POST['phone'])
                    user = Profile.objects.get(phone=phone_number)
                    return render(request, 'app/index.html',
                                  {'warning': "The Phone number you provided "
                                              "has already been registered with another account",
                                   'view': 'signup'})
                except Profile.DoesNotExist:
                    try:
                        user = User.objects.get(username=request.POST['email'])
                        return render(request, 'app/index.html',
                                      {'warning': "The email address you provided has already "
                                                  "been registered with another account", 'view': 'signup'})
                    except User.DoesNotExist:
                        if number_is_correct(number) and email_is_correct(email):
                            user = User.objects.create_user(username=email, first_name=first_name,
                                                            last_name=last_name, email=email, password=password1)
                            new_user_profile = Profile(user=user)
                            new_user_profile.phone = format_number(number)
                            new_user_profile.save()
                            authenticate(usernam=email, password=password1)
                            login(request, user)
                            return redirect('home')
                        elif not number_is_correct(number):
                            return render(request, 'app/index.html',
                                          {'view': 'signup', 'warning': "Invalid Phone number. Please try again"})

                        else:
                            return render(request, 'app/index.html',
                                          {'view': 'signup', 'warning': "Invalid Email Address.Please try again "})
            else:
                return render(request, 'app/index.html', {'warning': "Password do not match", 'view': 'signup'})
        else:
            return render(request, 'app/index.html', {'warning': "All fields are required", 'view': 'signup'})

    return render(request, 'app/index.html', {'view': 'signup'})


def logout_view(request):
    logout(request)
    return redirect('home')


# page for editing user details
@loginRequired
def update_user(request):
    if request.method == 'POST':
        fname = request.POST['first_name']
        lname = request.POST['last_name']
        number = request.POST['phone']
        email = request.POST['email']
        if fname and lname and number and email:
            if number_is_correct(number) and email_is_correct(email):
                user = User.objects.get(username=request.user.username)
                user.first_name = fname
                user.last_name = lname
                user.username = email
                user.email = email
                user_profile = Profile.objects.get(phone=user.profile.phone)
                user_profile.phone = format_number(number)
                user.save()
                user_profile.save()
                logout(request)
                return render(request, 'app/index.html',
                              {'view': 'login', 'message': 'Account updated, login to continue'})
            elif not number_is_correct(number):
                return render(request, 'app/index.html', {'view': 'user_profile', 'warning': 'Invalid phone number'})
            else:
                return render(request, 'app/index.html', {'view': 'user_profile', 'warning': 'Invalid Email Address'})
        else:
            return render(request, 'app/index.html',
                          {'view': 'user_profile', 'warning': 'Please fill in the missing fields'})
    return redirect('home')


# page for changing password
@loginRequired
def update_password(request):
    if request.method == 'POST':
        username = request.user.username
        old_pass = request.POST['old_password']
        new_pass1 = request.POST['new_password1']
        new_pass2 = request.POST['new_password2']
        if old_pass and new_pass1 and new_pass2:
            if new_pass1 == new_pass2:
                user = authenticate(username=username, password=old_pass)
                if user is not None:
                    user.set_password(new_pass1)
                    user.save()
                    logout(request)
                    return render(request, 'app/index.html',
                                  {'view': 'login', 'message': 'Password changed successfully. Login to continue'})
                else:
                    return render(request, 'app/index.html',
                                  {'view': 'change_password', 'warning': 'The old password is incorrect'})
            else:
                return render(request, 'app/index.html', {'view': ''
                                                                  'change_password',
                                                          'warning': 'New passwords do not match'})

        else:
            return render(request, 'app/index.html', {'view': ''
                                                              'change_password',
                                                      'warning': 'Blank field(s) detected'})
    return redirect('home')


# the homepage view
def home_view(request):
    bookings = []
    if request.user.is_authenticated:
        bookings = Booking.objects.filter(user=request.user)
    return render(request, 'app/index.html', {'view': 'none', 'bookings': bookings})


# the booking page view
@csrf_exempt
def booking_view(request):
    today = date.today()
    future = today + timedelta(weeks=1)
    bookings = Booking.objects.filter(user=request.user)
    if not request.user.is_authenticated:
        return render(request, 'app/index.html',
                      {'view': 'login', 'login_message': 'Please login to continue', 'where_to': 'booking'})
    routes = getroutes()
    if request.is_ajax():
        user = request.user
        route = Route.objects.filter(id=request.POST['route_id']).first()
        t_datetime = request.POST['datetime']
        seats = make_seats_list(request.POST['seats'])
        amount = request.POST['amount']
        if route and t_datetime and seats:
            booking = Booking.objects.create(user=user, route=route, travelling_datetime=t_datetime, seats=seats,
                                             amount=amount)
            data = {'booking_id': booking.id}
            return JsonResponse(data)
        else:
            response = {'message': 'Something went wrong. Please try again'}
            return JsonResponse(response)

    return render(request, 'app/booking.html', {'origins': routes['origins'],
                                                'min_date': str(today),
                                                'max_date': str(future),
                                                'bookings': bookings})


# the payment page view
@loginRequired
def summary(request):
    if request.method == 'POST':
        booking = Booking.objects.filter(id=request.POST['booking_id']).first()
        return render(request, 'app/summary.html', {'booking': booking})
    return redirect('booking')


def payment_view(request, booking_id):
    booking = Booking.objects.get(id=booking_id)
    phone = request.user.profile.phone
    return render(request, 'app/payment.html',
                  {'booking': booking, 'paybill': LipanaMpesaPassword.Business_short_code, 'phone': phone})


# function to check if the entered phone number is correct
def number_is_correct(number):
    try:
        print(int(number))
        if number[0] == '0' and len(number) == 10 or number[0] == '7' and \
                len(number) == 9 or number[0:3] == '254' and len(number) == 12:
            return True
        else:
            return False
    except ValueError:
        return False


# formatting the phone number before saving
def format_number(number):
    if number[0] == '0':
        formatted_number = '254' + number[1:]
    elif number[0] == '7':
        formatted_number = '254' + number
    else:
        formatted_number = number
    return formatted_number


# checking whether the entered email is correct using regex
def email_is_correct(email):
    regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
    if re.search(regex, email):
        return True
    else:
        return False


# querying all available routes from the database
def getroutes():
    routes = Route.objects.all()
    if routes:
        origins = set([route.origin for route in routes])
        destinations = set([route.destination for route in routes])
        routes_dict = {'origins': origins, 'destinations': destinations}
        return routes_dict
    return {"origins": [], 'destinations': []}


@csrf_exempt
def get_destinations(request):
    if request.is_ajax():
        origin = request.POST['origin']
        routes = Route.objects.filter(origin=origin)
        destinations = [route.destination for route in routes]
        return JsonResponse({'destinations': destinations})
    return redirect('home')


@csrf_exempt
def check_seats(request):
    if request.is_ajax():
        delete_unpaid()
        origin = request.POST['origin']
        destination = request.POST['destination']
        t_date = request.POST['date']
        t_time = request.POST['time'] + ':00'
        if origin and destination and origin and t_date and t_time:
            t_datetime = make_aware((datetime.strptime(t_date + " " + t_time, "%Y-%m-%d %H:%M:%S")))
            route = Route.objects.filter(origin=origin, destination=destination, active=True).first()
            if route:
                bookings = Booking.objects.filter(route=route, travelling_datetime=t_datetime)
                bookings = [booking for booking in bookings]
                booked_seats = []
                for booking in bookings:
                    booked_seats += booking.seats
                return JsonResponse({'booked_seats': booked_seats,
                                     'first_class': route.first_class_cost,
                                     'economy': route.economy_class_cost,
                                     'datetime': t_datetime,
                                     'route_id': route.id,
                                     })
            return JsonResponse({'message': 'There are no scheduled journeys for the selected route'})

        return JsonResponse({'message': 'Missing fields detected. Please fill in all required fields'})

    return redirect('home')


def make_seats_list(string):
    seats = string.split(',')
    seats.pop()
    return [int(seat_id) for seat_id in seats]


def delete_unpaid():
    filter_datetime = timezone.now()-timezone.timedelta(minutes=30)
    Booking.objects.filter(booking_datetime__lte=filter_datetime, paid=False).delete()