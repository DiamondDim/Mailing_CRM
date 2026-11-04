from django import forms
from django.utils import timezone
from .models import Client, Message, Mailing
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['email', 'full_name', 'comment']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'example@mail.ru',
                'style': 'font-family: Montserrat, sans-serif;'
            }),
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Иванов Иван Иванович',
                'style': 'font-family: Montserrat, sans-serif;'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Комментарий (необязательно)',
                'style': 'font-family: Montserrat, sans-serif;'
            }),
        }


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['subject', 'body']
        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Тема письма',
                'style': 'font-family: Montserrat, sans-serif;'
            }),
            'body': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Текст письма',
                'style': 'font-family: Montserrat, sans-serif;'
            }),
        }


class MailingForm(forms.ModelForm):
    class Meta:
        model = Mailing
        fields = ['start_time', 'end_time', 'message', 'recipients']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
                'style': 'font-family: Montserrat, sans-serif;'
            }),
            'end_time': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
                'style': 'font-family: Montserrat, sans-serif;'
            }),
            'message': forms.Select(attrs={
                'class': 'form-select',
                'style': 'font-family: Montserrat, sans-serif;'
            }),
            'recipients': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'size': 5,
                'style': 'font-family: Montserrat, sans-serif;'
            }),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields['message'].queryset = Message.objects.filter(owner=user)
            self.fields['recipients'].queryset = Client.objects.filter(owner=user)

    def clean(self):
        """Валидация дат по ТЗ: start_time не в прошлом и раньше end_time."""
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if start_time and end_time:
            if start_time < timezone.now():
                raise forms.ValidationError("Дата и время начала не могут быть в прошлом.")
            if start_time >= end_time:
                raise forms.ValidationError("Дата начала должна быть строго раньше даты окончания.")

        return cleaned_data


class RegisterForm(UserCreationForm):
    """Кастомная форма регистрации с email и стилями Bootstrap"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'example@mail.ru',
            'style': 'font-family: Montserrat, sans-serif;'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Применяем Bootstrap-стили ко всем полям
        for field_name in self.fields:
            field = self.fields[field_name]
            if field_name in ['password1', 'password2']:
                field.widget = forms.PasswordInput(attrs={
                    'class': 'form-control',
                    'placeholder': 'Пароль' if field_name == 'password1' else 'Подтвердите пароль',
                    'style': 'font-family: Montserrat, sans-serif;'
                })
            elif field_name == 'username':
                field.widget.attrs.update({
                    'class': 'form-control',
                    'placeholder': 'Имя пользователя',
                    'style': 'font-family: Montserrat, sans-serif;'
                })


class ProfileForm(forms.ModelForm):
    """Форма редактирования профиля (аватар + дата рождения)"""
    first_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Имя',
            'style': 'font-family: Montserrat, sans-serif;'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Фамилия',
            'style': 'font-family: Montserrat, sans-serif;'
        })
    )

    class Meta:
        model = Profile
        fields = ['avatar', 'date_of_birth']
        widgets = {
            'avatar': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'style': 'font-family: Montserrat, sans-serif;'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'style': 'font-family: Montserrat, sans-serif;'
            }),
        }
