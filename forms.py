from django import forms

class AddressForm(forms.Form):
    address = forms.CharField(max_length=100)
