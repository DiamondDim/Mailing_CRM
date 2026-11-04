from django.shortcuts import redirect, get_object_or_404, render
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.core.cache import cache
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str

from .models import Client, Message, Mailing, MailingAttempt, Profile
from .forms import ClientForm, MessageForm, MailingForm, RegisterForm, ProfileForm
from .mixins import OwnerRequiredMixin


# ==========================================
# ГЛАВНАЯ СТРАНИЦА (Кеширование на 15 минут)
# ==========================================
@method_decorator(cache_page(60 * 15), name='dispatch')
class HomeView(TemplateView):
    template_name = 'mailings/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # 1. Если это менеджер (is_staff) - видит всё
        if user.is_staff:
            context['total_mailings'] = Mailing.objects.count()
            context['total_clients'] = Client.objects.count()
            context['active_mailings'] = Mailing.objects.filter(status='started').count()
            context['mailings'] = Mailing.objects.all()[:5]

        # 2. Если пользователь АВТОРИЗОВАН (но не менеджер) - видит только своё
        elif user.is_authenticated:  # <--- ВОТ ЭТА СТРОКА СПАСАЕТ ОТ ОШИБКИ!
            context['total_mailings'] = Mailing.objects.filter(owner=user).count()
            context['total_clients'] = Client.objects.filter(owner=user).count()
            context['active_mailings'] = Mailing.objects.filter(status='started', owner=user).count()
            context['mailings'] = Mailing.objects.filter(owner=user)[:5]

        # 3. Если это ГОСТЬ (неавторизованный) - показываем нули
        else:
            context['total_mailings'] = 0
            context['total_clients'] = 0
            context['active_mailings'] = 0
            context['mailings'] = []

        return context


# ==========================================
# CRUD ДЛЯ КЛИЕНТОВ
# ==========================================
class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = 'mailings/client_list.html'
    context_object_name = 'clients'

    def get_queryset(self):
        if self.request.user.is_staff:
            return Client.objects.all()
        return Client.objects.filter(owner=self.request.user)


class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = 'mailings/client_form.html'
    success_url = reverse_lazy('client_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class ClientUpdateView(LoginRequiredMixin, OwnerRequiredMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = 'mailings/client_form.html'
    success_url = reverse_lazy('client_list')


class ClientDeleteView(LoginRequiredMixin, OwnerRequiredMixin, DeleteView):
    model = Client
    template_name = 'mailings/client_confirm_delete.html'
    success_url = reverse_lazy('client_list')


# ==========================================
# CRUD ДЛЯ СООБЩЕНИЙ
# ==========================================
class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = 'mailings/message_list.html'
    context_object_name = 'messages'

    def get_queryset(self):
        if self.request.user.is_staff:
            return Message.objects.all()
        return Message.objects.filter(owner=self.request.user)


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = 'mailings/message_form.html'
    success_url = reverse_lazy('message_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MessageUpdateView(LoginRequiredMixin, OwnerRequiredMixin, UpdateView):
    model = Message
    form_class = MessageForm
    template_name = 'mailings/message_form.html'
    success_url = reverse_lazy('message_list')


class MessageDeleteView(LoginRequiredMixin, OwnerRequiredMixin, DeleteView):
    model = Message
    template_name = 'mailings/message_confirm_delete.html'
    success_url = reverse_lazy('message_list')


# ==========================================
# CRUD ДЛЯ РАССЫЛОК
# ==========================================
class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = 'mailings/mailing_list.html'
    context_object_name = 'mailings'

    def get_queryset(self):
        if self.request.user.is_staff:
            return Mailing.objects.all()
        return Mailing.objects.filter(owner=self.request.user)


class MailingDetailView(LoginRequiredMixin, DetailView):
    model = Mailing
    template_name = 'mailings/mailing_detail.html'
    context_object_name = 'mailing'

    def get_queryset(self):
        if self.request.user.is_staff:
            return Mailing.objects.all()
        return Mailing.objects.filter(owner=self.request.user)

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.update_status()
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Статистика доставок
        attempts = self.object.attempts.all()
        total = attempts.count()
        success_count = attempts.filter(status='success').count()

        context['total_attempts'] = total
        context['success_attempts'] = success_count
        context['success_rate'] = round((success_count / total) * 100, 1) if total > 0 else 0.0
        return context


class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailings/mailing_form.html'
    success_url = reverse_lazy('mailing_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MailingUpdateView(LoginRequiredMixin, OwnerRequiredMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailings/mailing_form.html'
    success_url = reverse_lazy('mailing_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class MailingDeleteView(LoginRequiredMixin, OwnerRequiredMixin, DeleteView):
    model = Mailing
    template_name = 'mailings/mailing_confirm_delete.html'
    success_url = reverse_lazy('mailing_list')


# ==========================================
# ОТПРАВКА РАССЫЛКИ
# ==========================================
class SendMailingView(LoginRequiredMixin, View):
    def post(self, request, pk):
        if request.user.is_superuser:
            queryset = Mailing.objects.all()
        else:
            queryset = Mailing.objects.filter(owner=request.user)

        mailing = get_object_or_404(Mailing, pk=pk)
        mailing.update_status()

        now = timezone.now()
        # Проверка временного окна
        if not (mailing.start_time <= now <= mailing.end_time):
            return redirect('mailing_detail', pk=mailing.pk)

        message = mailing.message
        recipients = mailing.recipients.all()

        attempts = []
        for client in recipients:
            try:
                send_mail(
                    subject=message.subject,
                    message=message.body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[client.email],
                    fail_silently=False,
                )
                attempts.append(
                    MailingAttempt(
                        mailing=mailing,
                        status='success',
                        server_response='Письмо отправлено успешно'
                    )
                )
            except Exception as e:
                attempts.append(
                    MailingAttempt(
                        mailing=mailing,
                        status='failed',
                        server_response=str(e)
                    )
                )

        # Массовое создание записей (требование ТЗ)
        MailingAttempt.objects.bulk_create(attempts)

        # Обновляем статус, если он был 'created'
        if mailing.status == 'created':
            mailing.status = 'started'
            mailing.save(update_fields=['status'])

        # Очищаем кэш для мгновенного обновления статистики
        cache.delete(f'mailings/mailing/{pk}/')
        cache.delete('/')
        cache.clear()

        return redirect('mailing_detail', pk=mailing.pk)


# ==========================================
# РЕГИСТРАЦИЯ ПОЛЬЗОВАТЕЛЯ (С подтверждением email)
# ==========================================
class RegisterView(View):
    def get(self, request):
        form = RegisterForm()
        return render(request, 'mailings/register.html', {'form': form})

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Блокируем аккаунт до подтверждения email
            user.save()

            # Генерируем токен и uid для ссылки активации
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            # Создаем ссылку активации
            activation_url = f"http://{request.get_host()}/accounts/activate/{uid}/{token}/"

            # 🔥 ЯВНЫЙ ВЫВОД В КОНСОЛЬ (чтобы не зависеть от base64 кодировки email)
            print("\n" + "=" * 80)
            print("🔗 ССЫЛКА ДЛЯ АКТИВАЦИИ АККАУНТА (скопируй и вставь в браузер):")
            print(activation_url)
            print("=" * 80 + "\n")

            # Отправляем письмо (оно всё равно придет в консоль, но теперь у нас есть чистая ссылка выше)
            send_mail(
                subject='Активация аккаунта на Mailing CRM',
                message=f'Здравствуйте!\n\nДля активации аккаунта перейдите по ссылке:\n{activation_url}\n\nЕсли вы не регистрировались, просто проигнорируйте это письмо.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )

            return render(request, 'mailings/register_success.html', {'email': user.email})
        return render(request, 'mailings/register.html', {'form': form})


# ==========================================
# АКТИВАЦИЯ АККАУНТА
# ==========================================
class ActivateAccountView(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            login(request, user)
            return render(request, 'mailings/activate_success.html', {'user': user})
        else:
            return render(request, 'mailings/activate_invalid.html')


# ==========================================
# ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ
# ==========================================
class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'mailings/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Определяем роль пользователя для отображения
        if user.is_superuser:
            context['role'] = 'Администратор'
        elif user.is_staff:
            context['role'] = 'Модератор'
        else:
            context['role'] = 'Пользователь'

        context['user_groups'] = user.groups.all()
        return context


# ==========================================
# РЕДАКТИРОВАНИЕ ПРОФИЛЯ
# ==========================================
class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = 'mailings/profile_edit.html'
    success_url = reverse_lazy('profile')

    def get_object(self, queryset=None):
        """Получаем профиль текущего пользователя или создаём, если его нет"""
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        return profile

    def get_initial(self):
        """Подставляем first_name и last_name из User"""
        initial = super().get_initial()
        initial['first_name'] = self.request.user.first_name
        initial['last_name'] = self.request.user.last_name
        return initial

    def form_valid(self, form):
        """Сохраняем first_name и last_name в User"""
        self.request.user.first_name = form.cleaned_data['first_name']
        self.request.user.last_name = form.cleaned_data['last_name']
        self.request.user.save()
        return super().form_valid(form)
