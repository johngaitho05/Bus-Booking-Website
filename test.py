from django.utils import timezone

print(timezone.now())

























# api_url = "https://sandbox.safaricom.co.ke/mpesa/accountbalance/v1/query"
# headers = {"Authorization": "Bearer %s" % access_token}
# request = {"Initiator": "apitest481",
#            "SecurityCredential": "Safaricom111!",
#            "CommandID": "AccountBalance",
#            "PartyA": "601481",
#            "IdentifierType": "4",
#            "Remarks": "Remarks",
#            "QueueTimeOutURL": "https://efce4a14.ngrok.io/api/timeout/",
#            "ResultURL": "https://efce4a14.ngrok.io/api/b2c/result/",
#            }
#
# response = requests.post(api_url, json=request, headers=headers)
# print(response.status_code)
# print(response.text)



# api_url = "https://sandbox.safaricom.co.ke/mpesa/b2c/v1/paymentrequest"
# headers = {"Authorization": "Bearer %s" % access_token}
# request = {
#     "InitiatorName": "apitest481",
#     "SecurityCredential": "Safaricom111!",
#     "CommandID": "BusinessPayment",
#     "Amount": 100,
#     "PartyA": "601481",
#     "PartyB": 254708374149,
#     "Remarks": "Allowance Payment",
#     "QueueTimeOutURL": "https://efce4a14.ngrok.io/api/timeout/",
#     "ResultURL": "https://efce4a14.ngrok.io/api/b2c/result/",
# }
#
# response = requests.post(api_url, json=request, headers=headers)
# print(response.status_code)
# print(response.text)

# def trigger_stk():
#     shortcode = LipanaMpesaPassword.Business_short_code
#     access_token = MpesaAccessToken.validated_mpesa_access_token
#     api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
#     headers = {"Authorization": "Bearer %s" % access_token}
#     request = {
#         "BusinessShortCode": shortcode,
#         "Password": LipanaMpesaPassword.decode_password,
#         "Timestamp": LipanaMpesaPassword.lipa_time,
#         "TransactionType": "CustomerPayBillOnline",
#         "Amount": 1,
#         "PartyA": 254796008376,  # replace with your phone number to get stk push
#         "PartyB": shortcode,
#         "PhoneNumber": 254796008376,  # replace with your phone number to get stk push
#         "CallBackURL": "https://sandbox.safaricom.co.ke/mpesa/",
#         "AccountReference": booking_id,
#         "TransactionDesc": "Testing stk push"
#     }
#     response = requests.post(api_url, json=request, headers=headers)
#     return response.json()
#
#
# booking_id = random.randint(1, 10000)
#
#
# print(trigger_stk())


import requests


# api_url = "https://sandbox.safaricom.co.ke/mpesa/b2b/v1/paymentrequest"
# headers = {"Authorization": "Bearer %s" % access_token}
# request = {
#     "Initiator": "Solar4 School",
#     "SecurityCredential": "Safaricom111!",
#     "CommandID": "BusinessPayBill",
#     "SenderIdentifierType": "School",
#     "RecieverIdentifierType": "Supplier",
#     "Amount": 20000,
#     "PartyA": "601481",
#     "PartyB": "600000",
#     "AccountReference": "MXCPD",
#     "Remarks": "Purchase of raw mterials",
#     "QueueTimeOutURL": "https://efce4a14.ngrok.io/api/timeout",
#     "ResultURL": "https://efce4a14.ngrok.io/api/b2c/result",
# }
#
# response = requests.post(api_url, json=request, headers=headers)
# print(response.json())