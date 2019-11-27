from django.shortcuts import render,redirect
from django.http import HttpResponse, JsonResponse
import requests
from requests.auth import HTTPBasicAuth
import json
from . mpesa_credentials import MpesaAccessToken, LipanaMpesaPpassword
from django.views.decorators.csrf import csrf_exempt
from .models import MpesaPayment


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
    options = {"ShortCode": "600247",
               "ResponseType": "Completed",
               "ConfirmationURL": "https://559c31a5.ngrok.io/api/v1/c2b/confirmation",
               "ValidationURL": "https://559c31a5.ngrok.io/api/v1/c2b/validation"}
    response = requests.post(api_url, json=options, headers=headers)
    return HttpResponse(response.text)


def lipa_na_mpesa_online(request):
    if request.user.is_authenticated:
        if request.method == 'POST'and request.POST['mpesa_number']:
            mpesa_number = request.POST['mpesa_number']
            if len(mpesa_number) == 12 and int(mpesa_number[0:3]) == 254:
                access_token = MpesaAccessToken.validated_mpesa_access_token
                api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
                headers = {"Authorization": "Bearer %s" % access_token}
                request = {
                    "BusinessShortCode": LipanaMpesaPpassword.Business_short_code,
                    "Password": LipanaMpesaPpassword.decode_password,
                    "Timestamp": LipanaMpesaPpassword.lipa_time,
                    "TransactionType": "CustomerPayBillOnline",
                    "Amount": int(request.POST['amount']),
                    "PartyA": int(mpesa_number),  # replace with your phone number to get stk push
                    "PartyB": LipanaMpesaPpassword.Business_short_code,
                    "PhoneNumber": int(mpesa_number),  # replace with your phone number to get stk push
                    "CallBackURL": "https://sandbox.safaricom.co.ke/mpesa/",
                    "AccountReference": "JohnG",
                    "TransactionDesc": "Testing stk push"
                }
                response = requests.post(api_url, json=request, headers=headers)
                return HttpResponse('Checkout the mpesa pop up on your phone')
            else:
                return render(request,'app/index.html',{'alert_message':'invalid Phone number'})

        return render(request, 'app/index.html', {'alert_message': 'phone number is required!'})

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
    context = {
        "ResultCode": 0,
        "ResultDesc": "Accepted"
    }
    return JsonResponse(dict(context))