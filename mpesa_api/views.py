from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
import requests
from requests.auth import HTTPBasicAuth
import json
import time
from app.views import *
from .mpesa_credentials import MpesaAccessToken, LipanaMpesaPassword
from django.views.decorators.csrf import csrf_exempt
from .models import MpesaPayment
from app.views import loginRequired
from projectdir.utils import accountNumberToPk


def getAccessToken(request):
    pass


@csrf_exempt
def register_urls(request):
    access_token = MpesaAccessToken.validated_mpesa_access_token
    api_url = "https://sandbox.safaricom.co.ke/mpesa/c2b/v1/registerurl"
    headers = {"Authorization": "Bearer %s" % access_token}
    options = {"ShortCode": "601481",
               "ResponseType": "Completed",
               "ConfirmationURL": "https://bookweb-app.herokuapp.com/api/c2b/confirmation/",
               "ValidationURL": "https://bookweb-app.herokuapp.com/api/c2b/validation/"}
    response = requests.post(api_url, json=options, headers=headers)
    return HttpResponse(response.text)


@loginRequired
def lipa_na_mpesa_online(request):
    paybill = LipanaMpesaPassword.Business_short_code
    if request.method == 'POST' and request.POST['mpesa_number']:
        booking_id = request.POST['booking_id']
        mpesa_number = request.POST['mpesa_number']
        amount = request.POST['amount']
        if len(mpesa_number) == 12 and int(mpesa_number[0:3]) == 254:
            access_token = MpesaAccessToken.validated_mpesa_access_token
            api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
            headers = {"Authorization": "Bearer %s" % access_token}
            request = {
                "BusinessShortCode": 174379,
                "Password": LipanaMpesaPassword.decode_password,
                "Timestamp": LipanaMpesaPassword.lipa_time,
                "TransactionType": "CustomerPayBillOnline",
                "Amount": 1,
                "PartyA": 254708374149,
                "PartyB": 174379,
                "PhoneNumber": int(mpesa_number),
                "CallBackURL": "https://bookweb-app.herokuapp.com/api/c2b/callback/",
                "AccountReference": "Ref01",
                "TransactionDesc": "Testing STK Push"
            }
            response = requests.post(api_url, json=request, headers=headers)
            print(response.json())
            return redirect('payment', booking_id=booking_id)
        else:
            booking = get_object_or_404(Booking, id=booking_id)
            return render(request, 'app/summary.html', {'booking': booking, 'alert_message': 'invalid Phone number', })

    return redirect('booking')


@csrf_exempt
def call_back(request):
    json_data = request.body.decode('utf-8')
    loaded_data = json.loads(json_data)
    return JsonResponse(loaded_data)


@csrf_exempt
def validation(request):
    context = {
        "ResultCode": 0,
        "ResultDesc": "Accepted"
    }
    print(re)
    return JsonResponse(dict(context))


@csrf_exempt
def confirmation(request):
    mpesa_body = request.body.decode('utf-8')
    mpesa_payment = json.loads(mpesa_body)
    try:
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
    except IntegrityError:
        print("integrity error")
    acc = mpesa_payment['BillRefNumber']
    booking = get_object_or_404(Booking, id=accountNumberToPk(acc))
    booking.paid = True
    booking.save()


@csrf_exempt
@loginRequired
def simulate_payment(request):
    if request.is_ajax():
        booking = get_object_or_404(Booking, id=request.POST['booking_id'])
        access_token = MpesaAccessToken.validated_mpesa_access_token
        api_url = "https://sandbox.safaricom.co.ke/mpesa/c2b/v1/simulate"
        headers = {"Authorization": "Bearer %s" % access_token}
        request = {"ShortCode": "601481",
                   "CommandID": "CustomerPayBillOnline",
                   "Amount": booking.amount,
                   "Msisdn": 254708374149,
                   "BillRefNumber": booking.account_number()
                   }

        requests.post(api_url, json=request, headers=headers)
        # countdown = 7
        # while countdown > 0:
        #     time.sleep(1)
        #     countdown -= 1
        if booking.paid is True:
            return JsonResponse({'message': 'Payment was successful', 'code': 0})
        return JsonResponse({'message': 'We could not verify your payment', 'code': 1})

    raise Http404('Page not found')


@csrf_exempt
def result_view(request):
    mpesa_body = request.body.decode('utf-8')
    print(mpesa_body)
    return HttpResponse(mpesa_body)


@csrf_exempt
def timeout_view(request):
    mpesa_body = request.body.decode('utf-8')
    return HttpResponse(mpesa_body)
