from django import forms
from .models import Order

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('address', 'comment')
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'comment': forms.Textarea(attrs={'rows': 2}),
        }