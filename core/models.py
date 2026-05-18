from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    openId = models.CharField(max_length=64, unique=True, null=True, blank=True)
    loginMethod = models.CharField(max_length=64, null=True, blank=True)
    role = models.CharField(max_length=10, choices=[('user', 'user'), ('admin', 'admin')], default='user')
    lastSignedIn = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username

class LoanApplication(models.Model):
    LOAN_TYPES = [
        ('business', 'Business'),
        ('personal', 'Personal'),
        ('emergency', 'Emergency'),
        ('education', 'Education'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    fullName = models.CharField(max_length=255)
    phoneNumber = models.CharField(max_length=20)
    nationalId = models.CharField(max_length=20)
    loanType = models.CharField(max_length=20, choices=LOAN_TYPES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.fullName} - {self.loanType}"

class LoanOffer(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    application = models.ForeignKey(LoanApplication, on_delete=models.CASCADE, related_name='offers')
    loanAmount = models.IntegerField()  # in KES
    interestRate = models.IntegerField(default=10)  # 10%
    taxRevenue = models.IntegerField()  # in KES
    totalRepayment = models.IntegerField()  # loan + tax + interest
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Offer for {self.application.fullName} - {self.loanAmount} KES"

class MegaPayTransaction(models.Model):
    STATUS_CHOICES = [
        ('initiated', 'Initiated'),
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    offer = models.ForeignKey(LoanOffer, on_delete=models.CASCADE, related_name='transactions')
    transactionId = models.CharField(max_length=255, unique=True)
    msisdn = models.CharField(max_length=20)
    amount = models.IntegerField()  # in KES
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='initiated')
    responseCode = models.IntegerField(null=True, blank=True)
    responseDescription = models.TextField(null=True, blank=True)
    transactionReceipt = models.CharField(max_length=255, null=True, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Transaction {self.transactionId} - {self.status}"
