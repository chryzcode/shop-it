from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import PasswordResetForm, PasswordResetConfirmForm

app_name = "account"

urlpatterns = [
    path('activate/<slug:uidb64>/<slug:token>)/', views.account_activate, name='activate_account'),
    path('register/', views.account_register, name='register'),
    path('login/', views.account_login, name='login'),
    path('logout/', views.account_logout, name='logout'),
    path('<slugified_store_name>/edit/', views.edit_account, name='edit_account'),
    path('delete/', views.account_delete, name='delete_account'),

    path('password-reset/psddword-reset-email-confirm/', TemplateView.as_view(template_name='account/user/password-reset-success.html'), name='password-reset-email-confirm'),

    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='account/user/password-reset-form.html', success_url='password-reset-email-confirm', email_template_name='account/user/password-reset-email.html', form_class=PasswordResetForm),name='password_reset'),

    path('password-reset-confirm/<uidb64>/<token>)/', auth_views.PasswordResetConfirmView.as_view(template_name='account/user/password-reset-confirm.html', success_url='password_reset_complete', form_class=PasswordResetConfirmForm), name='password_reset_confirm'),
]
