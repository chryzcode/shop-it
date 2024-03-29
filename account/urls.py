from django.contrib.auth import views as auth_views
from django.urls import path
from django.views.generic import TemplateView

from . import views
from .forms import PasswordResetConfirmForm, PasswordResetForm

app_name = "account"

urlpatterns = [
    path(
        "activate/<slug:uidb64>/<slug:token>)/",
        views.account_activate,
        name="activate_account",
    ),
    path("register/", views.account_register, name="register"),
    path("login/", views.account_login, name="login"),
    path("logout/", views.account_logout, name="logout"),
    path("settings/profile/", views.user_profile, name="user_profile"),
    path("settings/store-account/", views.store_account, name="store_account"),
    path("delete/", views.account_delete, name="delete_account"),
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="account/user/password-reset-form.html",
            success_url="password-reset-email-confirm",
            email_template_name="account/user/password-reset-email.html",
            form_class=PasswordResetForm,
        ),
        name="password_reset",
    ),
    path(
        "password-reset-confirm/<uidb64>/<token>",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="account/user/password-reset-confirm.html",
            success_url="/account/password-reset-complete/",
            form_class=PasswordResetConfirmForm,
        ),
        name="password_reset_confirm",
    ),
    path(
        "password-reset/password-reset-email-confirm/",
        TemplateView.as_view(template_name="account/user/password-reset-success.html"),
        name="password_reset_done",
    ),
    path(
        "password-reset-complete/",
        TemplateView.as_view(template_name="account/user/password-reset-success.html"),
        name="password_reset_complete",
    ),
    path(
        "change-password/",
        auth_views.PasswordChangeView.as_view(
            template_name="account/user/forgot-password.html", success_url="/"
        ),
        name="change_password",
    ),
    path(
        "store/<slugified_store_name>/add-store-staff/",
        views.store_staff_register,
        name="store_staff_register",
    ),
    path("delete-staff/<str:pk>", views.delete_store_staff, name="delete_store_staff"),
    path("staff-stores/", views.staff_stores, name="staff_stores"),
    path("store/<slugified_store_name>/", views.select_store, name="select_store"),
    path("add-staff/user/", views.add_store_staff, name="add_store_staff"),
    path("create-store/", views.create_store, name="create_store"),
    path("bank-details/", views.bank_details, name="bank_details"),
    path(
        "store/<slug:slugified_store_name>/accept-invitation/<str:email>/<slug:uidb64>/<slug:token>/",
        views.accept_staff_invitation,
        name="accept_staff_invitation",
    ),
    path("bank-auth/<slug:uidb64>/<slug:token>/<account_number>/<account_name>/<bank_name>/<bank_code>/", views.bank_auth, name="bank_auth"),
]
