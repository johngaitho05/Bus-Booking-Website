from datetime import datetime, date, time, timedelta
import time

import pytz
from django.http.response import JsonResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.timezone import make_aware
from django.views.decorators.csrf import csrf_exempt

from .models import Profile, Route, Booking, Message
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


@csrf_exempt
@check_authentication
def login_view(request):
    if request.is_ajax():
        username = request.POST['username']
        password = request.POST['password']
        if username and password:
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return JsonResponse({'message': 'Success', 'response_code': 0})
                return JsonResponse({'message': 'Your account is been suspended. '
                                                'Contact our support team for assistance',
                                     'response_code': 1})
        return JsonResponse({'message': 'Invalid username or password', 'response_code': 1})
    return render(request, 'app/index.html', {'view': 'login'})


@csrf_exempt
@check_authentication
def signup_view(request):
    if request.is_ajax():
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        number = request.POST['phone']
        if first_name and last_name and email and password1 and password2:
            if password1 == password2:
                try:
                    phone_number = format_number(request.POST['phone'])
                    user = Profile.objects.get(phone=phone_number)
                    return JsonResponse({'message': "The Phone number you provided has already been registered"
                                                    " with another account", 'response_code': 1})
                except Profile.DoesNotExist:
                    try:
                        user = User.objects.get(username=email)
                        return JsonResponse({'message': 'The exists an account associated with that the email address.'
                                                        'Please login or use a different email address',
                                             'response_code': 1})
                    except User.DoesNotExist:
                        if number_is_correct(number) and email_is_correct(email):
                            user = User.objects.create_user(username=email, first_name=first_name,
                                                            last_name=last_name, email=email, password=password1)
                            new_user_profile = Profile(user=user)
                            new_user_profile.phone = format_number(number)
                            new_user_profile.save()
                            authenticate(usernam=email, password=password1)
                            login(request, user)
                            return JsonResponse({'message': 'Success', 'response_code': 0})
                        elif not number_is_correct(number):
                            return JsonResponse({'message': "Invalid phone number", 'response_code': 1})

                        return JsonResponse({'message': "Invalid email address", 'response_code': 1})

            return JsonResponse({'message': "Password do not match", 'response_code': 1})

        return JsonResponse({'message': "Blank fields detected", 'response_code': 1})

    return render(request, 'app/index.html', {'view': 'signup'})


def logout_view(request):
    logout(request)
    return redirect('home')


# page for editing user details
@csrf_exempt
@loginRequired
def update_user(request):
    if request.is_ajax():
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        number = request.POST['phone']
        email = request.POST['email']
        if first_name and last_name and number and email:
            if number_is_correct(number) and email_is_correct(email):
                user = User.objects.get(username=request.user.username)
                updated_info = {'first_name': first_name, 'last_name': last_name, 'email': email}
                for (key, value) in updated_info.items():
                    setattr(user, key, value)
                user.profile.phone = number
                user.save()
                user.profile.save()
                return JsonResponse({'response_code': 0, 'message': 'Successfully updated'})
            elif not number_is_correct(number):
                return JsonResponse({'response_code': 1, 'message': 'Invalid phone number'})
            return JsonResponse({'response_code': 1, 'message': 'Invalid email address'})
        return JsonResponse({'response_code': 1, 'message': 'Blank fields detected'})
    return redirect('home')


# page for changing password
@csrf_exempt
@loginRequired
def update_password(request):
    if request.is_ajax():
        username = request.user.username
        old_pass = request.POST['old_pass']
        new_pass1 = request.POST['new_pass1']
        new_pass2 = request.POST['new_pass2']
        if old_pass and new_pass1 and new_pass2:
            if new_pass1 == new_pass2:
                user = authenticate(username=username, password=old_pass)
                if user is not None:
                    user.set_password(new_pass1)
                    user.save()
                    login(request, user)
                    return JsonResponse({'message': 'Password changed successfully', 'response_code': 0})

                return JsonResponse({'message': 'The old password is incorrect', 'response_code': 1})

            return JsonResponse({'message': 'New passwords do not match', 'response_code': 1})

        return JsonResponse({'message': 'Blank field(s) detected', 'response_code': 1})
    return redirect('home')


# the homepage view
def home_view(request):
    bookings = []
    if request.user.is_authenticated:
        bookings = Booking.objects.filter(user=request.user)
    return render(request, 'app/index.html', {'view': 'none', 'bookings': bookings})


# the booking page view
@csrf_exempt
@loginRequired
def booking_view(request):
    today = date.today()
    future = today + timedelta(weeks=1)
    bookings = Booking.objects.filter(user=request.user)
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
        booking = get_object_or_404(Booking, id=request.POST['booking_id'])
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
            current_time = timezone.now()
            if t_datetime <= current_time:
                return JsonResponse(
                    {'message': 'Invalid time. The selected time must be greater than the current time'})
            route = Route.objects.filter(origin=origin, destination=destination, active=True).first()
            if route:
                bookings = Booking.objects.filter(route=route, travelling_datetime=t_datetime)
                bookings = [booking for booking in bookings]
                booked_seats = []
                for booking in bookings:
                    booked_seats += booking.seats
                return JsonResponse({'booked_seats': booked_seats,
                                     'first_class': int(route.first_class_cost),
                                     'economy': int(route.economy_class_cost),
                                     'datetime': t_datetime,
                                     'route_id': route.id,
                                     })
            return JsonResponse({'message': 'There are no scheduled journeys for the selected route'})

        return JsonResponse({'message': 'Missing fields detected. Please fill in all required fields'})

    return redirect('home')


@csrf_exempt
def save_message(request):
    if request.is_ajax():
        name = request.POST['name']
        email = request.POST['email']
        subject = request.POST['subject']
        message = request.POST['message']
        if name and email and subject and message:
            if email_is_correct(email):
                Message.objects.create(name=name, email=email, subject=subject, message=message)
                return JsonResponse({'message': 'We have received your message and we will get back to you soon',
                                     'response_code': 0})
            return JsonResponse({'message': 'Invalid email address', 'response_code': 1})

        return JsonResponse({'message': 'Please fill out the blank fields', 'response_code': 1})
    return redirect('home')


def make_seats_list(string):
    seats = string.split(',')
    seats.pop()
    return sorted([int(seat_id) for seat_id in seats])


def delete_unpaid():
    filter_datetime = timezone.now() - timezone.timedelta(minutes=30)
    Booking.objects.filter(booking_datetime__lte=filter_datetime, paid=False).delete()
