# apps/contact/forms.py
from django import forms

class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=200, 
        widget=forms.TextInput(attrs={'placeholder': 'Tu Nombre'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'Tu Correo Electrónico'})
    )
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'placeholder': 'Tu Teléfono'})
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Tu Mensaje', 'rows': 4})
    )
