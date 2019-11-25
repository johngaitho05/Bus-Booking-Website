from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from .models import Profile,Route
from django.contrib.auth import authenticate,logout,login
import re
from django.contrib import messages


def loginRequired(func):
    def wrapper(request,*args,**kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        return func(request,*args,**kwargs)
    return wrapper


def check_authentication(func):
    def wrapper(request,*args,**kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        return func(request,*args,**kwargs)
    return wrapper


def home_view(request):
    return render(request,'app/index.html',{'view':'none'})


def booking_view(request):
    if not request.user.is_authenticated:
        return render(request,'app/index.html',{'view':'login','login_message':'Please login to continue', 'where_to':'booking'})
    routes = Route.objects.all()
    if request.method == 'POST':
        if request.POST['origin'] and request.POST['destination'] and request.POST['booking_date'] and request.POST['booking_time'] and request.POST['seats']:
            name =request.user.first_name + " " + request.user.last_name
            origin = request.POST['origin']
            destination = request.POST['destination']
            date = request.POST['booking_date']
            time = request.POST['booking_time']
            seats = request.POST['seats']
            phone = request.user.profile.phone
            try:
                route = Route.objects.get(origin=origin,destination=destination)
                amount = int(route.cost)* int(seats)
                return render(request,'app/payment.html',{'name':name, 'origin':origin,'destination':destination,'date':date,'time':time,'seats':seats,'amount':amount,'phone':phone})
            except Route.DoesNotExist:
                return render(request, 'app/booking.html', {'routes':routes, 'booking_warning': 'None of our vehicles passes through that route. Try another route'})
        else:
            return redirect('booking',{'routes':routes,'booking_warning':'All fields are required'})
    return render(request,'app/booking.html',{'routes':routes})

@check_authentication
def login_view(request):
    if request.method == 'POST':
        if request.POST['username'] and request.POST['password']:
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username = username,password = password)
            if user is not None:
                if user.is_active:
                    login(request,user)
                    if request.POST['where_to']:
                        return redirect(str(request.POST['where_to']))
                    else:
                        return redirect('home')
                else:
                    # print 'The password is valid,but the account has been disabled'
                    return render(request,'app/index.html',{'view':'login','login_waring':'Your account has been suspended'})
            else:
                return render(request,'app/index.html',{'view':'login','login_warning':'Invalid username or password'})
    return render(request,'app/index.html',{'view':'login'})

@check_authentication
def signup_view(request):
    if request.method=='POST':
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
                            return render (request,'app/index.html',
                                           {'view':'signup','warning':"Invalid Phone number. Please try again"})

                        else:
                            return render(request, 'app/index.html',
                                          {'view': 'signup', 'warning': "Invalid Email Address.Please try again "})
            else:
                return render(request, 'app/index.html', {'warning': "Password do not match",'view':'signup'})
        else:
            return render(request, 'app/index.html', {'warning': "All fields are required", 'view': 'signup'})

    return render(request, 'app/index.html', {'view': 'signup'})


def logout_view(request):
    logout(request)
    return redirect('home')

@loginRequired
def payment_view(request):
    if request.method == 'POST':
        name = request.user.first_name + request.user.first_name
        date = request.POST['date']
        time = request.POST['time']
        origin = request.POST['origin']
        destination = request.POST['destination']
        amount = request.POST['amount']
        if name and date and time and origin and destination and amount:
            return render (request, 'app/payment.html', {'name':name, 'date':date, 'time':time, 'origin':origin, 'destination':destination, 'amount':amount})
        else:
            return redirect('booking',{'message':'all fields are reqiured'})


@loginRequired
def update_user(request):
    if request.method == 'POST':
        fname = request.POST['first_name']
        lname = request.POST['last_name']
        number = request.POST['phone']
        email = request.POST['email']
        if fname and lname and number and email:
            if number_is_correct(number) and email_is_correct(email):
                user = User.objects.get(username = request.user.username)
                user.first_name = fname
                user.last_name =lname
                user.username = email
                user.email = email
                user_profile = Profile.objects.get(phone = user.profile.phone)
                user_profile.phone = format_number(number)
                user.save()
                user_profile.save()
                logout(request)
                return render(request,'app/index.html',{'view':'login','message':'Account updated, login to continue'})
            elif not number_is_correct(number):
                return render(request,'app/index.html',{'view':'user_profile','warning':'Invalid phone number'})
            else:
                return render(request, 'app/index.html', {'view': 'user_profile', 'warning': 'Invalid Email Address'})
        else:
            return render(request, 'app/index.html', {'view': 'user_profile', 'warning': 'Please fill in the missing fields'})


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
                                      {'view':'login','message':'Password changed successfully. Login to continue'})
                else:
                    return render(request, 'app/index.html',
                                  {'view':'change_password','warning': 'The old password is incorrect'})
            else:
                return render(request, 'app/index.html',{'view':''
                     'change_password','warning':'New passwords do not match'})

        else:
            return render(request, 'app/index.html', {'view': ''
                                                              'change_password',
                                                      'warning': 'Blank field(s) detected'})
    return redirect('home')






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


def format_number(number):
    if number[0] == '0':
        formatted_number = '254' + number[1:]
    elif number[0] == '7':
        formatted_number = '254' + number
    else:
        formatted_number = number
    return formatted_number


def email_is_correct(email):
    regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
    if re.search(regex, email):
        return True
    else:
        return False


