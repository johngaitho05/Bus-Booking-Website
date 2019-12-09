from django.shortcuts import render,redirect
from django.http import HttpResponse, JsonResponse
import requests
from requests.auth import HTTPBasicAuth
import json
import time
from app.views import *
from . mpesa_credentials import MpesaAccessToken, LipanaMpesaPassword
from django.views.decorators.csrf import csrf_exempt
from .models import MpesaPayment
from app.views import loginRequired


def getAccessToken(request):
    consumer_key = '7RTRwuqalt1WXvy6LUEjozMCVKCyC4o8'
    consumer_secret = 'Xyi0iYyfgxLy1HcW'
    api_URL = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    r = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))
    mpesa_access_token = json.loads(r.text)
    validated_mpesa_access_token = mpesa_access_token['access_token']
    return HttpResponse(validated_mpesa_access_token)

@csrf_exempt
def register_urls(request):
    access_token = MpesaAccessToken.validated_mpesa_access_token
    api_url = "https://sandbox.safaricom.co.ke/mpesa/c2b/v1/registerurl"
    headers = {"Authorization": "Bearer %s" % access_token}
    options = {"ShortCode": "600220",
               "ResponseType": "Completed",
               "ConfirmationURL": "https://3512c82a.ngrok.io/api/v1/c2b/confirmation",
               "ValidationURL": "https://3512c82a.ngrok.io/api/v1/c2b/validation"}
    response = requests.post(api_url, json=options, headers=headers)
    return HttpResponse(response.text)

@loginRequired
def lipa_na_mpesa_online(request):
    paybill = LipanaMpesaPassword.Business_short_code
    if request.method == 'POST'and request.POST['mpesa_number']:
        booking_id = request.POST['booking_id']
        mpesa_number = request.POST['mpesa_number']
        amount = request.POST['amount']
        if len(mpesa_number) == 12 and int(mpesa_number[0:3]) == 254:
            access_token = MpesaAccessToken.validated_mpesa_access_token
            api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
            headers = {"Authorization": "Bearer %s" % access_token}
            request = {
                "BusinessShortCode": paybill,
                "Password": LipanaMpesaPassword.decode_password,
                "Timestamp": LipanaMpesaPassword.lipa_time,
                "TransactionType": "CustomerPayBillOnline",
                "Amount": int(amount),
                "PartyA": int(mpesa_number),  # replace with your phone number to get stk push
                "PartyB": paybill,
                "PhoneNumber": int(mpesa_number),  # replace with your phone number to get stk push
                "CallBackURL": "https://sandbox.safaricom.co.ke/mpesa/",
                "AccountReference": booking_id,
                "TransactionDesc": "Testing stk push"
            }
            response = requests.post(api_url, json=request, headers=headers)
            return redirect('payment', booking_id=booking_id)
        else:
            return render(request,'app/index.html',{'alert_message':'invalid Phone number'})

    return redirect('booking')

@csrf_exempt
def call_back(request):
    pass


@csrf_exempt
def validation(request):
    context = {
        "ResultCode": 0,
        "ResultDesc": "Accepted"
    }
    return JsonResponse(dict(context))


@csrf_exempt
def confirmation(request):
    mpesa_body =request.body.decode('utf-8')
    mpesa_payment = json.loads(mpesa_body)
    payment = MpesaPayment(
        first_name=mpesa_payment['FirstName'],
        last_name=mpesa_payment['LastName'],
        middle_name=mpesa_payment['MiddleName'],
        description=mpesa_payment['TransID'],
        phone_number=mpesa_payment['MSISDN'],
        amount=mpesa_payment['TransAmount'],
        reference=mpesa_payment['BillRefNumber'],
        organization_balance=mpesa_payment['OrgAccountBalance'],
        type=mpesa_payment['TransactionType'],
    )
    payment.save()
    booking = Booking.objects.get(id=int(mpesa_payment['BillRefNumber']))
    booking.paid = True
    booking.save()

@loginRequired
def simulate_payment(request):
    if request.method == 'POST':
        phone = int(request.POST['phone'])
        amount = int(request.POST['amount'])
        account_number = request.POST['account_number']
        access_token = MpesaAccessToken.validated_mpesa_access_token
        api_url = "https://sandbox.safaricom.co.ke/mpesa/c2b/v1/simulate"
        headers = {"Authorization": "Bearer %s" % access_token}
        request = {"ShortCode":"600220",
                   "CommandID": "CustomerPayBillOnline",
                   "Amount": amount,
                   "Msisdn": 254708374149,
                   "BillRefNumber": account_number}

        requests.post(api_url, json=request, headers=headers)
        countdown = 10
        while countdown > 0:
            time.sleep(1)
            countdown -= 1
        booking = Booking.objects.get(id=int(account_number))
        if booking.paid is True:
            return HttpResponse("payment received")
        return HttpResponse("payment has not been received!")













