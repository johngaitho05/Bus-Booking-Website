from datetime import datetime, date, time, timedelta
import time
from django.http.response import JsonResponse, Http404
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
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


# page for changing password
@loginRequired
def update_password(request):
    if request.method == 'POST':
        username = request.user.username
        oldpass = request.POST['old_password']
        newpass1 = request.POST['new_password1']
        newpass2 = request.POST['new_password2']
        if oldpass and newpass1 and newpass2:
            if newpass1 == newpass2:
                user = authenticate(username=username, password=oldpass)
                if user is not None:
                    user.set_password(newpass1)
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
    return render(request, 'app/index.html', {'view': 'none'})


# checking available seats
@loginRequired
def checkseats(request):
    if request.method == 'POST':
        origin = request.POST['origin']
        destination = request.POST['destination']
        booking_date = request.POST['booking_date']
        booking_time = request.POST['booking_time']
        routes = Route.objects.all()
        if origin and destination and booking_time and booking_date:
            try:
                formatted_date = datetime.strptime(booking_date, "%Y-%m-%d")
                formatted_time = datetime.strptime(booking_time + ':00', "%H:%M:%S")
                bookings = Booking.objects.filter(origin=origin, destination=destination,
                                                  date=formatted_date, time=formatted_time)
                bookings_list = [booking for booking in bookings]
                n = len(bookings_list) - 1
                booked_seats = 0
                while n >= 0:
                    booked_seats += bookings_list[n].seats
                    n -= 1
                if booked_seats <= 59:
                    return render(request, "app/booking.html",
                                  {'available_seats': 60 - booked_seats, "origin": origin,
                                   'destination': destination, 'date': booking_date, 'time': booking_time})
            except Booking.DoesNotExist:
                return render(request, "app/booking.html",
                              {'available_seats': 60, "origin": origin,
                               'destination': destination, 'date': booking_date, 'time': booking_time})
        return render(request, 'app/booking.html', {'routes': routes, 'booking_warning': 'Missing fields detected'})
    return redirect('booking')


today = date.today()
future = today + timedelta(weeks=1)


# the booking page view
def booking_view(request):
    if not request.user.is_authenticated:
        return render(request, 'app/index.html',
                      {'view': 'login', 'login_message': 'Please login to continue', 'where_to': 'booking'})
    routes = getroutes()
    if request.method == 'POST':
        name = request.user.first_name + " " + request.user.last_name
        origin = request.POST['origin']
        destination = request.POST['destination']
        booking_date = request.POST['booking_date']
        booking_time = request.POST['booking_time']
        seats = request.POST['seats']
        phone = request.user.profile.phone
        if origin and destination and booking_time and booking_date and seats:
            try:
                route = Route.objects.get(origin=origin, destination=destination)
                amount = int(route.cost) * int(seats)
                booking = Booking.objects.create(name=name, origin=origin, destination=destination,
                                                 date=booking_date, time=booking_time, seats=seats, amount=amount)
                booking_id = booking.id
                return render(request, 'app/summary.html', {'name': name,
                                                            'origin': origin, 'destination': destination,
                                                            'date': booking_date,
                                                            'time': booking_time, 'seats': seats, 'amount': amount,
                                                            'phone': phone,
                                                            'booking_id': booking_id})
            except Route.DoesNotExist:
                return render(request, 'app/booking.html',
                              {'routes': routes, 'booking_warning':
                                  'None of our vehicles passes through that route. Try another route'
                                  , 'min_date': today, 'max_date': future})
        return render(request, 'app/booking.html', {'origins': routes['origins'],
                                                    'destinations': routes['destinations'], 'booking_warning':
                                                        'Missing fields detected', 'min_date': today,
                                                    'max_date': future})
    return render(request, 'app/booking.html', {'origins': routes['origins'],
                                                'min_date': str(today), 'max_date': str(future)})


# the payment page view
@loginRequired
def summary(request):
    if request.method == 'POST':
        name = request.user.first_name + request.user.first_name
        date = request.POST['date']
        time = request.POST['time']
        origin = request.POST['origin']
        destination = request.POST['destination']
        amount = request.POST['amount']
        if name and date and time and origin and destination and amount:
            return render(request, 'app/summary.html',
                          {'name': name, 'date': date, 'time': time, 'origin': origin, 'destination': destination,
                           'amount': amount})
        else:
            return redirect('booking', {'message': 'Blank fields detected'})


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


@loginRequired
def delete_booking(request):
    if request.method == 'POST':
        boom = 600
        while boom > 0:
            time.sleep(1)
            boom -= 1
        booking = Booking.objects.get(id=int(request.POST['booking_id']))
        if booking.paid is False:
            booking.delete()
            return redirect('home')


@csrf_exempt
def get_destinations(request):
    if request.is_ajax():
        origin = request.POST['origin']
        routes = Route.objects.filter(origin=origin)
        destinations = [route.destination for route in routes]
        return JsonResponse({'destinations': destinations})
    raise Http404("Request is not ajax")


def check_seats(request):
    pass

