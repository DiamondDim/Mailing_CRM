from django import forms
from django.utils import timezone
from .models import Client, Message, Mailing


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

    def clean(self):
        """Валидация дат по ТЗ: start_time не в прошлом и раньше end_time."""
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if start_time and end_time:
            # Проверка: start_time не может быть в прошлом
            if start_time < timezone.now():
                raise forms.ValidationError(
                    "Дата и время начала не могут быть в прошлом."
                )

            # Проверка: start_time должен быть раньше end_time
            if start_time >= end_time:
                raise forms.ValidationError(
                    "Дата начала должна быть строго раньше даты окончания."
                )

        return cleaned_data
