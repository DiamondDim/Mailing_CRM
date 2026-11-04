from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

from mailings.views import RegisterView, ProfileView, ProfileUpdateView, ActivateAccountView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('mailings.urls')),

    # Профиль пользователя
    path('accounts/profile/', ProfileView.as_view(), name='profile'),
    path('accounts/profile/edit/', ProfileUpdateView.as_view(), name='profile_edit'),

    # Активация аккаунта (НОВОЕ)
    path('accounts/activate/<uidb64>/<token>/', ActivateAccountView.as_view(), name='activate_account'),

    # Стандартные URL-ы аутентификации Django
    path('accounts/login/', auth_views.LoginView.as_view(
        template_name='mailings/login.html',
        redirect_authenticated_user=True,
    ), name='login'),

    path('accounts/logout/', auth_views.LogoutView.as_view(
        next_page='login',
    ), name='logout'),

    path('accounts/password-reset/', auth_views.PasswordResetView.as_view(
        template_name='mailings/password_reset.html',
        email_template_name='mailings/password_reset_email.html',
        success_url='/accounts/password-reset/done/',
    ), name='password_reset'),

    path('accounts/password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='mailings/password_reset_done.html',
    ), name='password_reset_done'),

    path('accounts/password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='mailings/password_reset_confirm.html',
        success_url='/accounts/password-reset-complete/',
    ), name='password_reset_confirm'),

    path('accounts/password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='mailings/password_reset_complete.html',
    ), name='password_reset_complete'),

    # Кастомная регистрация
    path('accounts/register/', RegisterView.as_view(), name='register'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
