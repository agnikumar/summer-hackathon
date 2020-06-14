from django import forms
from dappx.models import UserProfileInfo
from django.contrib.auth.models import User


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta():
        model = User
        fields = ('username','password')
        help_texts = {
            'username': None,
            'password': None,
        }

class UserProfileInfoForm(forms.ModelForm):

    type_choices = [("CL", "Client"), ("CO", "Contractor")]

    user_type = forms.ChoiceField(widget=forms.RadioSelect, choices=type_choices)

    class Meta():
        model = UserProfileInfo
        fields = ("user_type",)