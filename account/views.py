from xml import dom

import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from notifications.signals import notify

from app.forms import *
from app.models import *
from app.views import *
from customer.models import Customer
from payment.models import *
from subscriptions.models import Subscription_Timeline

from .forms import *
from .models import *
from .tokens import account_activation_token


def beta_tester_verification(request, email):
    if email in settings.BETA_TESTERS:
        return True
    else:
        return False


def account_login(request):
    context = {}
    if request.user.is_authenticated:
        return redirect("/")

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        if beta_tester_verification(request, email) == True:
            try:
                user = get_object_or_404(User, email=email)
                if user:
                    user = authenticate(request, email=email, password=password)
                    if user:
                        if user.store_creator == True:
                            login(request, user)
                            return redirect("/")

                        if user.store_staff == True:
                            login(request, user)
                            return redirect("account:staff_stores")

                        if user.store_creator == False and user.store_staff == False:
                            login(request, user)
                            return redirect("/")
                    else:
                        messages.error(request, "Password is incorrect")
                else:
                    messages.error(request, "Email is incorrect")
            except:
                messages.error(request, "Email is incorrect")
        else:
            messages.error(request, "You are not a beta tester")
            return redirect("account:login")

    return render(request, "account/registration/login.html", context)


@login_required(login_url="/account/login/")
def account_logout(request):
    logout(request)
    return redirect("/")


# delete user after 50 days using real time
@login_required(login_url="/account/login/")
def account_delete(request):
    user = User.objects.get(email=request.user.email)
    if request.user.store_creator == True:
        account_type = 'Store Creator'
        store = Store.objects.get(store_name=request.user.store_name)
        subject = f"Request for Your Shopit Account to be Deleted - {store.store_name}"
        store_staffs = store_staff.objects.filter(store=store)
        staff_email_list = []
        for staff in store_staffs:
            staff_email = staff.email
            staff_email_list.append(staff_email)
            to_email = [ staff_email, settings.EMAIL_HOST_USER ]
        to_email.append(store.owner.email)
        message = render_to_string(
        "account/user/account-delete-email.html",
        {"user": user,
        "account_type":account_type,
        "store_staffs":store_staffs,
        "domain": settings.DEFAULT_DOMAIN,
        }
    )
    elif request.user.store_staff == True:
        account_type = 'Store Staff'
        staff_stores = Store.objects.filter(staffs=request.user)
        subject = f"Request for Your Shopit Account to be Deleted - Store Staff"
        staff_stores_list = []
        for store in staff_stores:
            store_owner_email = store.owner.email
            staff_stores_list.append(
                store_owner_email
            )
            to_email = [settings.EMAIL_HOST_USER, store_owner_email]
        to_email.append(request.user.email)
        message = render_to_string(
        "account/user/account-delete-email.html",
        {"user": user,
        "account_type":account_type,
        "staff_stores":staff_stores,
        "domain": settings.DEFAULT_DOMAIN,
        }
    )
    else:
        account_type = 'Customer'
        subject = f"Request for Your Shopit Account to be Deleted - Customer"
        to_email = [settings.EMAIL_HOST_USER]

        message = render_to_string(
            "account/user/account-delete-email.html",
            {"user": user,
            "account_type":account_type,
            "domain": settings.DEFAULT_DOMAIN,
            }
        )

    user.is_active = False
    user.save()
    from_email = user.email 
    send_mail(subject, message, from_email, to_email, html_message=message)
    logout(request)
    return redirect("/")


def account_register(request):
    if request.user.is_authenticated:
        return redirect("/")
    registerform = RegistrationForm
    if request.method == "POST":
        email = request.POST.get("email")
        if beta_tester_verification(request, email) == True:
            registerform = RegistrationForm(request.POST)
            if registerform.is_valid():
                user = registerform.save(commit=False)
                user.email = registerform.cleaned_data["email"]
                user.full_name = registerform.cleaned_data["full_name"]
                user.store_name = registerform.cleaned_data["store_name"]
                user.set_password(registerform.cleaned_data["password"])
                user.is_active = False
                user.store_staff = False
                user.save()
                store = Store.objects.create(
                    owner=user,
                    store_name=registerform.cleaned_data["store_name"],
                )
                subject = "Activate your Shopit Account"
                message = render_to_string(
                    "account/registration/account_activation_email.html",
                    {
                        "user": user,
                        "domain": settings.DEFAULT_DOMAIN,
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "token": account_activation_token.make_token(user),
                    },
                )
                user.email_user(subject=subject, message=message)
                notify.send(
                    store.owner,
                    recipient=user,
                    verb="Set your store bank account details",
                    bank_details_url=reverse("account:bank_details"),
                )
                notify.send(
                    store.owner,
                    recipient=user,
                    verb=f"Set at least a shipping method for logistics funds",
                    shipping_method_url=reverse("app:add_shipping_method"),
                    
                )
                notify.send(
                    store.owner,
                    recipient=user,
                    verb=f"Set your store default currency ",
                    currency_url=reverse("account:store_account"),
                )
                return render(request, "account/registration/registration-success.html")
        else:
            messages.error(request, "You are not a beta tester")
            return redirect("account:register")
    return render(request, "account/registration/register.html", {"form": registerform})


def account_activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = get_object_or_404(User, pk=uid)
    except:
        return render(request, "error-pages/404-page.html")

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect("/")
    else:
        return render(request, "error-pages/404-page.html")


@login_required(login_url="/account/login/")
def user_profile(request):
    account = request.user
    userprofileform = UserProfileForm(instance=account)
    user_profile = User.objects.get(email=account.email)
    if request.method == "POST":
        userprofileform = UserProfileForm(request.POST, request.FILES, instance=account)
        if userprofileform.is_valid():
            userprofileform.save()
            return redirect("/")

    return render(
        request,
        "account/user/user-profile.html",
        {
            "userprofileform": userprofileform,
            "account": account,
            "user_profile": user_profile,
        },
    )


def country_details(request, country_code):
    url = f"https://api.countrystatecity.in/v1/countries/{country_code}"
    headers = {"X-CSCAPI-KEY": settings.COUNTRY_STATE_CITY_API_KEY}
    response = requests.get(url, headers=headers)
    data = response.json()
    country_name = data["name"]
    return country_name


def state_details(request, country_code, state_code):
    url = f"https://api.countrystatecity.in/v1/countries/{country_code}/states/{state_code}"
    headers = {"X-CSCAPI-KEY": settings.COUNTRY_STATE_CITY_API_KEY}
    response = requests.request("GET", url, headers=headers)
    data = response.json()
    state_name = data["name"]
    return state_name


@login_required(login_url="/account/login/")
def store_account(
    request,
):
    if request.user.store_creator == True:
        currencies = Currency.objects.all()
        account = request.user
        store = Store.objects.get(owner=account)
        storeform = StoreForm(instance=store)
        url = "https://api.countrystatecity.in/v1/countries"

        headers = {"X-CSCAPI-KEY": settings.COUNTRY_STATE_CITY_API_KEY}

        response = requests.request("GET", url, headers=headers)
        data = response.json()
        country_names = {}
        for a_country in data:
            country_names[a_country["name"]] = a_country["iso2"]
        country_names = sorted(country_names.items(), key=lambda x: x[0])
        if request.method == "POST":
            storeform = StoreForm(request.POST, request.FILES, instance=store)
            if storeform.is_valid():
                store_name = storeform.cleaned_data["store_name"]
                currency = storeform.cleaned_data["currency"]
                country_code = storeform.cleaned_data["country"]
                state_code = storeform.cleaned_data["state"]
                country = country_details(request, country_code)
                state = state_details(request, country_code, state_code)

                form = storeform.save(commit=False)
                form.owner = request.user
                form.country = country
                form.state = state
                form.slugified_store_name = slugify(store_name)
                form.save()
                currency = Currency.objects.get(name=currency)
                if not Wallet.objects.filter(store=store, currency=currency).exists():
                    Wallet.objects.create(
                        currency=currency,
                        store=store,
                    )
                request.user.store_name = store_name
                request.user.save()
                return redirect("account:store_account")

        return render(
            request,
            "account/user/store-account.html",
            {
                "storeform": storeform,
                "account": account,
                "store": store,
                "currencies": currencies,
                "country_names": country_names,
            },
        )
    else:
        return redirect("account:user_profile")


def accept_staff_invitation(request, slugified_store_name, email, uidb64, token):
    store = Store.objects.get(slugified_store_name=slugified_store_name)
    if store_staff.objects.filter(store=store, email=email).exists():
        messages.error(request, f"You are already a staff of {store.store_name} store")
        return redirect("/")
    else:
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = get_object_or_404(User, pk=uid)
        except:
            return render(request, "error-pages/404-page.html")

        if user is not None and account_activation_token.check_token(user, token):
            if User.objects.filter(email=email).exists():
                user = User.objects.get(email=email)
                staff = store_staff.objects.create(
                    store=store,
                    full_name=user.full_name,
                    email=user.email,
                    phone_number=user.phone_number,
                    avatar=user.avatar,
                    password=user.password,
                )
                staff.save()
                store.staffs.add(user)
                store.save()
                staffs = store_staff.objects.filter(store=store)
                for staff in staffs:
                    staff_user = User.objects.get(email=staff.email)
                    notify.send(
                        store.owner,
                        recipient=staff_user,
                        verb="An additional staff has been added to the store",
                    )
                notify.send(
                    store.owner,
                    recipient=store.owner,
                    verb="You have been added as a staff member of your store",
                )
                return redirect("/")
            else:
                return render(request, "error-pages/404-page.html")
        else:
            return render(request, "error-pages/404-page.html")


def store_staff_register(request, slugified_store_name):
    if Store.objects.filter(slugified_store_name=slugified_store_name).exists():
        store = Store.objects.get(slugified_store_name=slugified_store_name)
        form = StoreStaffForm
        if request.method == "POST":
            form = StoreStaffForm(request.POST, request.FILES)
            if form.is_valid():
                user = User.objects.create(
                    email=form.cleaned_data["email"],
                    full_name=form.cleaned_data["full_name"],
                    phone_number=form.cleaned_data["phone_number"],
                    is_active=True,
                    is_staff=False,
                    store_creator=False,
                    store_staff=True,
                )
                user.set_password(form.cleaned_data["password"])
                user.save()
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = account_activation_token.make_token(user)
                try:
                    uid = force_str(urlsafe_base64_decode(uid))
                    user = get_object_or_404(User, pk=uid)
                except:
                    return render(request, "error-pages/404-page.html")

                if user is not None and account_activation_token.check_token(user, token):
                    user.is_active = True
                    user.save()
                    if user.is_active == True:
                        staff_user = form.save(commit=False)    
                        staff_user.store = store
                        staff_user.save()
                        store.staffs.add(user)
                        staffs = store_staff.objects.filter(store=store)
                        for staff in staffs:
                            staff_user = User.objects.get(email=staff.email)
                            notify.send(
                                store.owner,
                                recipient=staff_user,
                                verb="An additional staff has been added to the store",
                            )
                        notify.send(
                            store.owner,
                            recipient=store.owner,
                            verb="You have been added as a staff member of your store",
                        )
                        return redirect("/")
            else:
                return render(request, "error-pages/404-page.html")
    else:
        messages.error(request, "Store not found")
    return render(
        request, "account/registration/store-staff-register.html", {"form": form}
    )


@login_required(login_url="/account/login/")
def add_store_staff(request):
    form = ExistingStoreStaffForm
    store = Store.objects.get(owner=request.user)
    if Subscription_Timeline.objects.filter(store=store).exists():
        if request.user.store_creator == True:
            store_staffs = store_staff.objects.filter(store=store)
            store_subscription = Subscription_Timeline.objects.get(store=store)
            if store_subscription.subscription.name == "Professional":
                store_staffs_limit = 10
            elif store_subscription.subscription.name == "Standard":
                store_staffs_limit = 3
            else:
                store_staffs_limit = 0
            if store_staffs.count() <= store_staffs_limit:
                if request.method == "POST":
                    email = request.POST.get("email")
                    if User.objects.filter(email=email).exists():
                        user = User.objects.get(email=email)
                        if user.store_creator == False:
                            if user not in store.staffs.all():
                                user = User.objects.get(email=email)
                                subject = (
                                    f"{store.store_name} - Staff Permission Activation"
                                )
                                message = render_to_string(
                                    "account/registration/store_staff_email.html",
                                    {
                                        "user": user,
                                        "store": store,
                                        "existing_user": True,
                                        "email": user.email,
                                        "domain": settings.DEFAULT_DOMAIN,
                                        "slugified_store_name": store.slugified_store_name,
                                        "uidb64": urlsafe_base64_encode(
                                            force_bytes(user.pk)
                                        ),
                                        "token": account_activation_token.make_token(
                                            user
                                        ),
                                        "domain": settings.DEFAULT_DOMAIN,
                                    },
                                )
                                user.email_user(subject=subject, message=message)
                                staffs = store_staff.objects.filter(store=store)
                                for staff in staffs:
                                    staff_user = User.objects.get(email=staff.email)
                                    notify.send(
                                        store.owner,
                                        recipient=staff_user,
                                        verb="Permission to add a staff member sent",
                                    )
                                notify.send(
                                    store.owner,
                                    recipient=store.owner,
                                    verb="Permission to add a staff member sent",
                                )
                                return redirect("app:store_staff_page")
                            else:
                                messages.error(request, "User is already a staff")
                        else:
                            messages.error(request, "Store creator can't be a staff")

                    else:
                        subject = f"{store.store_name} - Staff Permission Activation"
                        message = render_to_string(
                            "account/registration/store_staff_email.html",
                            {
                                "store": store,
                                "existing_user": False,
                                "domain": settings.DEFAULT_DOMAIN,
                            },
                        )
                        email = request.POST.get("email")
                        if "@" in email and "." in email:
                            send_mail(
                                subject, message, settings.EMAIL_HOST_USER, [email], html_message=message
                            )
                            staffs = store_staff.objects.filter(store=store)
                            for staff in staffs:
                                staff_user = User.objects.get(email=staff.email)
                                notify.send(
                                    store.owner,
                                    recipient=staff_user,
                                    verb="Permission to add a staff member sent",
                                )
                            notify.send(
                                store.owner,
                                recipient=store.owner,
                                verb="Permission to add a staff member sent",
                            )
                            return redirect("app:store_staff_page")
                        else:
                            messages.error(
                                request, "Please enter a valid email address"
                            )
            else:
                messages.error(request, "You have reached the limit of staff members")
        else:
            messages.error(request, "You are not authorized")
    else:
        messages.error(request, "You are to subscribe to a plan to add staff")
    return render(
        request, "account/registration/add-store-staff-exist.html", {"form": form}
    )


@login_required(login_url="/account/login/")
def delete_store_staff(request, pk):
    if request.user.store_creator == True:
        store = Store.objects.get(owner=request.user)
        if store_staff.objects.filter(pk=pk, store=store).exists():
            staff = store_staff.objects.get(pk=pk, store=store)
            staff_user = User.objects.get(email=staff.email)
            store.staffs.remove(staff_user)
            staff.delete()
            staffs = store_staff.objects.filter(store=store)
            for staff in staffs:
                staff_user = User.objects.get(email=staff.email)
                notify.send(
                    store.owner,
                    recipient=staff_user,
                    verb=f"{staff_user.full_name} has been removed from the {store.store_name} store",
                )
            notify.send(
                store.owner,
                recipient=store.owner,
                verb=f"{staff_user.full_name} has been removed from the {store.store_name} store",
            )
            return redirect("app:store_staff_page")
        else:
            messages.error(request, "staff not found")
            return redirect("app:store_staff_page")
    else:
        error = "You are not authorized"
        return render(request, "store/store-staff-page.html", {"error": error})


@login_required(login_url="/account/login/")
def staff_stores(request):
    stores = Store.objects.filter(staffs=request.user)
    if stores:
        if stores.count() > 1:
            return render(
                request, "account/user/staff-stores-page.html", {"stores": stores}
            )
        else:
            return redirect("account:select_store", stores.first().slugified_store_name)
    logout(request)
    error = "You are not a staff of any store"
    return render(request, "account/registration/login.html", {"error": error})


@login_required(login_url="/account/login/")
def select_store(request, slugified_store_name):
    store = get_object_or_404(Store, slugified_store_name=slugified_store_name)
    if request.user in store.staffs.all():
        store_staff.objects.filter(email=request.user.email).update(
            store=store
        )
        return redirect("/")


@login_required(login_url="/account/login/")
def create_store(request):
    if request.user.store_creator == False and request.user.store_staff == False:
        form = AddStoreForm
        user = request.user
        if request.method == "POST":
            form = AddStoreForm(request.POST, request.FILES)
            if form.is_valid():
                store_name = form.cleaned_data["store_name"]
                user.store_name = store_name
                user.store_creator = True
                user.save()
                store = Store.objects.create(
                    store_name=store_name,
                    owner=user,
                    slugified_store_name=slugify(store_name),
                )
                notify.send(
                    store.owner,
                    recipient=user,
                    verb="Set your store bank account details",
                    bank_details_url=reverse("account:bank_details"),
                )
                notify.send(
                    store.owner,
                    recipient=user,
                    verb=f"Set at least a shipping method for logistics funds",
                    shipping_method_url=reverse("app:add_shipping_method"),
                )
                notify.send(
                    store.owner,
                    recipient=user,
                    verb=f"Set your store default currency",
                    currency_url=reverse("account:store_account"),
                )
                return redirect("/")
    return render(request, "account/registration/add-store.html", {"form": form})


@login_required(login_url="/account/login/")
def delete_shipping_method(request, pk):
    if request.user.store_creator == True:
        store = Store.objects.get(owner=request.user)
        shipping_method = get_object_or_404(Shipping_Method, pk=pk)
        if shipping_method:
            shipping_method.delete()
            return redirect("account:shipping_method_list")
    else:
        error = "You are not authorized"
        return render(request, "store/shipping-method.html", {"error": error})


def resolve_account_details(request, account_number, account_bank):
    url = "https://api.flutterwave.com/v3/accounts/resolve"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + settings.FLUTTERWAVE_SECRET_KEY,
    }
    data = {
        "account_number": account_number,
        "account_bank": account_bank,
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()
    else:
        return False


@login_required(login_url="/account/login/")
def bank_details(request):
    if request.user.store_creator == True:
        store = Store.objects.get(owner=request.user)
        bank_info = ""
        if store.currency:
            flutterwave_currency_code = store.currency.flutterwave_code
            url = f"https://api.flutterwave.com/v3/banks/{flutterwave_currency_code}"
            headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + settings.FLUTTERWAVE_SECRET_KEY,
            }
            response = requests.get(url, headers=headers)
            result = response.json().get("data")
            all_banks = {}
            for bank in result:
                all_banks[bank.get("name")] = bank.get("code")
            if Bank_Info.objects.filter(store=store).exists():
                bank_info = Bank_Info.objects.get(store=store)
                form = BankForm(instance=bank_info)
            else:
                form = BankForm()
            if request.method == "POST":
                form = BankForm(request.POST)
                bank_name = request.POST.get("bank_name")
                if form.is_valid():
                    bank_info = form.save(commit=False)
                    bank_name = form.cleaned_data["bank_name"]
                    bank_info.store = store
                    bank_info.bank_code = all_banks[bank_name]
                    bank_info.account_number = form.cleaned_data["account_number"]
                    if flutterwave_currency_code == "NG":
                        if resolve_account_details(
                            request, bank_info.account_number, bank_info.bank_code
                        ):
                            response = resolve_account_details(
                                request, bank_info.account_number, bank_info.bank_code
                            )
                            account_name = response.get("data").get("account_name")
                            bank_info.account_name = account_name
                            bank_info.save()
                            Bank_Info.objects.exclude(pk=bank_info.pk).filter(
                                store=store
                            ).delete()
                            return redirect("account:bank_details")
                        else:
                            error = "Account details are invalid"
                            return render(
                                request,
                                "store/bank-details.html",
                                {"error": error, "form": form, "all_banks": all_banks},
                            )
                    else:
                        bank_info.save()
                        Bank_Info.objects.exclude(pk=bank_info.pk).filter(
                            store=store
                        ).delete()
                        return redirect("account:bank_details")
        else:
            messages.error(request, "Please select a currency in your store settings")
            return redirect("account:store_account")
        return render(
            request,
            "store/bank-details.html",
            {"form": form, "all_banks": all_banks, "bank_info": bank_info},
        )
    else:
        messages.error(request, "You are not authorized")
        return redirect("account:store_account")
