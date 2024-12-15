from django import forms
from movie_app.models import Comments, Profile, Viewing
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator
from django.contrib.auth import authenticate

from django.core.exceptions import ValidationError

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comments
        fields = ['comment']

class UserSignUpForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Пароль'}),
        min_length=8,
        help_text='Минимальная длина пароля - 8 символов'
    )

    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Имя пользователя'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email'})
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Пользователь с таким email уже существует.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Пользователь с таким именем уже существует.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError({"confirm_password": "Пароли не совпадают"})
        
        return cleaned_data

class UserLoginForm(forms.Form):
    username = forms.CharField(label="Имя пользователя", max_length=150, required=True)
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput, required=True)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user is None:
                raise forms.ValidationError("Неверное имя пользователя или пароль.")
        return cleaned_data


class ProfileUpdateForm(forms.ModelForm):
    instagram = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Please write your instagram username'}),required=False)
    twitter = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Please write your twitter username'}),required=False)

    class Meta:
        model = Profile
        fields = ['avatar', 'info', 'instagram', 'twitter',]

class ChangeUserPasswordForm(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput(), validators=[MinLengthValidator(5, 'Please use at least 5 character long password')])
    old_password_again = forms.CharField(widget=forms.PasswordInput(), validators=[MinLengthValidator(5, 'Please use at least 5 character long password')])
    new_password = forms.CharField(widget=forms.PasswordInput, validators=[MinLengthValidator(5, 'Please use at least 5 character long password')])

    def clean(self):
        password1 = self.cleaned_data.get('old_password')
        password2 = self.cleaned_data.get('old_password_again')

        if password1 and password2 and password1 != password2:
            raise ValidationError('Passwords are not identical! Please check and try again.')
        
        return self.cleaned_data
    

class DeleteAccountForm(forms.Form):
    number = forms.IntegerField()
    confirm_number = forms.IntegerField()

    def clean(self):
        number = self.cleaned_data.get('number')
        number2 = self.cleaned_data.get('confirm_number')

        if number and number2 and number != number2:
            raise ValidationError('Validation numbers are not identical')
        
        return self.cleaned_data

