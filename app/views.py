from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from .models import Profile,Route
from django.contrib.auth import authenticate,logout,login
from django.contrib import messages


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


def signup_view(request):
    if request.method=='POST':
        if request.POST['first_name'] and request.POST['last_name'] and request.POST['email'] and request.POST['password1'] and request.POST['password2']:
            if request.POST['password1'] == request.POST['password2']:
                try:
                    user = User.objects.get(username=request.POST['email'])
                    return render(request,'app/index.html',
                                  {'warning': "The email address you provided has already been registered",'view':'signup'})
                except User.DoesNotExist:
                    first_name = request.POST['first_name']
                    last_name = request.POST['last_name']
                    username= request.POST['email']
                    email =request.POST['email']
                    password =request.POST['password1']
                    user = User.objects.create_user(username =username,first_name = first_name, last_name=last_name,email =email,password =password)
                    new_user_profile = Profile(user=user)
                    new_user_profile.phone = request.POST['phone']
                    new_user_profile.save()

                    authenticate(usernam=username,password=password)
                    login(request, user)
                    return redirect('home')
            else:
                return render(request, 'app/index.html', {'warning': "Password do not match",'view':'signup'})
        else:
            return render(request, 'app/index.html', {'warning': "All fields are required", 'view': 'signup'})

    return render(request, 'app/index.html', {'view': 'signup'})


def logout_view(request):
    logout(request)
    return redirect('home')


def payment_view(request):
    if  request.user.is_authenticated :
        if request.POST['date'] and request.POST['time'] and  request.POST['origin'] and request.POST['destination'] and request.POST['seats']:
            name = request.user.first_name + request.user.first_name
            date = request.POST['date']
            time = request.POST['time']
            origin = request.POST['origin']
            destination = request.POST['destination']
            amount = request.POST['amount']
            return render (request, 'app/payment.html', {'name':name, 'date':date, 'time':time, 'origin':origin, 'destination':destination, 'amount':amount})
        else:
            return redirect('booking',{'message':'all fields are reqiured'})
    return redirect('login', message='Please login to continue')



