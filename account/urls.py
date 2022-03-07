from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import PasswordResetForm

app_name = "account"

urlpatterns = [
    path('activate/<slug:uidb64>/<slug:token>)/', views.account_activate, name='activate_account'),
    path('register/', views.account_register, name='register'),
    path('login/', views.account_login, name='login'),
    path('logout/', views.account_logout, name='logout'),
    path('<slugified_store_name>/edit/', views.edit_account, name='edit_account'),
    path('delete/', views.account_delete, name='delete_account'),
    path('password-reset/', auth_views.PasswordResetView(template_name='account/user/password-reset-form.html', success_url='password-reset-mail-confirm', email_template_name='account/user/password-reset-reset-email.html', form_class=PasswordResetForm, name='password_reset'))
]
