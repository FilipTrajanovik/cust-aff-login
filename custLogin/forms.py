# custLogin/forms.py
from django import forms
from .models import Customer, CryptoTransfer, Cryptocurrency, CryptoConvert
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
        fields = ['username', 'email', 'phone', 'balance', 'address', 'raw_password', 'can_cashout']


class CustomerCashOutForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['credit_card_number', 'credit_card_expiry', 'credit_card_cvc']


class CryptoTransferForm(forms.ModelForm):
    receiver_username = forms.CharField(label="Send to (username)")

    class Meta:
        model = CryptoTransfer
        fields = ['cryptocurrency', 'amount']


    def __init__(self, sender, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sender = sender


    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('receiver_username')
        if not username:
            raise forms.ValidationError("Receiver username is required.")

        try:
            receiver = Customer.objects.get(username=username)
        except Customer.DoesNotExist:
            raise forms.ValidationError("Username does not exist.")

        if receiver == self.sender:
            raise forms.ValidationError("You can't transfer money to yourself.")

        cleaned_data['receiver'] = receiver  # ✅ ADD this
        return cleaned_data



    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.sender = self.sender
        instance.receiver = self.cleaned_data['receiver']
        if commit:
            instance.save()
        return instance


class ConversionForm(forms.ModelForm):
    class Meta:
        model = CryptoConvert
        fields = ['from_crypto', 'to_crypto', 'amount']
        labels = {
            'from_crypto': 'From Cryptocurrency',
            'to_crypto': 'To Cryptocurrency',
            'amount': 'Amount to Convert',
        }

    def __init__(self, customer,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.customer = customer
        self.fields['from_crypto'].queryset = Cryptocurrency.objects.filter(
            id__in=self._get_customer_wallet_crypto_ids()
        )
        self.fields['to_crypto'].queryset = Cryptocurrency.objects.all()

    def _get_customer_wallet_crypto_ids(self):
        return self.customer.wallets.values_list('cryptocurrency_id', flat=True)