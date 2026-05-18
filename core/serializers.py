from rest_framework import serializers
from .models import User, LoanApplication, LoanOffer, MegaPayTransaction

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'openId']

class LoanApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanApplication
        fields = '__all__'

class LoanOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanOffer
        fields = '__all__'

class MegaPayTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MegaPayTransaction
        fields = '__all__'
