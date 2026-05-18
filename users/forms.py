from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re
from store.models import Customer

class RegisterForm(UserCreationForm):
    full_name = forms.CharField(label='ФИО', max_length=150, required=True)
    phone = forms.CharField(label='Телефон', max_length=16, required=True)
    email = forms.EmailField(label='Email', required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        labels = {'username': 'Логин'}

    def clean_full_name(self):
        full_name = self.cleaned_data.get('full_name')
        if not re.fullmatch(r'[А-Яа-яЁё\s]+', full_name):
            raise ValidationError('ФИО должно содержать только кириллицу и пробелы')
        return full_name

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        # Удаляем все нецифровые символы (скобки, дефисы, пробелы)
        cleaned_phone = re.sub(r'\D', '', phone)
        # Проверяем, что получилось 11 цифр и начинается с 8 или 7
        if not re.fullmatch(r'[87]\d{10}', cleaned_phone):
            raise ValidationError('Телефон должен содержать 11 цифр и начинаться с 8 или 7')
        # Приводим к единому формату (например, 8XXXXXXXXXX)
        return cleaned_phone

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            # Создаём запись Customer, связанную с пользователем
            full_name = self.cleaned_data['full_name']
            name_parts = full_name.split()
            last_name = name_parts[-1] if name_parts else ''
            first_name = name_parts[0] if name_parts else ''
            Customer.objects.create(
                user=user,
                last_name=last_name,
                first_name=first_name,
                email=user.email,
                phone=self.cleaned_data['phone']
            )
        return user

class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Логин', max_length=150)
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)