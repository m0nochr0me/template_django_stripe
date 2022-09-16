from django import forms


class AddToOrder(forms.Form):
    qty = forms.IntegerField(min_value=1)

