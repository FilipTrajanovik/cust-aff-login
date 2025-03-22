# custLogin/forms.py
from django import forms
from .models import Customer
import uuid
from django.contrib.auth.hashers import make_password

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['email', 'phone', 'address', 'balance']

    def save(self, manager=None, commit=True):
        instance = super().save(commit=False)

        instance.username = self.generate_username(instance.email)
        raw_password = self.generate_password()


        instance.password = make_password(raw_password)
        instance.raw_password = raw_password
        if manager:
            instance.manager = manager

        if commit:
            instance.save()


        return instance, raw_password

    @staticmethod
    def generate_username(email):
        return email.split('@')[0] + uuid.uuid4().hex[:4]

    @staticmethod
    def generate_password():
        return uuid.uuid4().hex[:8]


class CustomerEditForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['username', 'email', 'phone', 'balance' ,'address', 'raw_password', 'can_cashout']

class CustomerCashOutForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['credit_card_number', 'credit_card_expiry', 'credit_card_cvc']