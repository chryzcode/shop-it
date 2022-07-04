import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from customer.models import Customer

from .forms import *
from .models import *
from app.models import *
from app.forms import *
from .tokens import account_activation_token


def account_login(request):
    context = {}
    if request.user.is_authenticated:
        return redirect("/")

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
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

    return render(request, "account/registration/login.html", context)


@login_required(login_url="/account/login/")
def account_logout(request):
    logout(request)
    return redirect("/")


@login_required(login_url="/account/login/")
def account_delete(request):
    request.user.delete()
    return redirect("/")


def account_register(request):
    if request.user.is_authenticated:
        return redirect("/")
    registerform = RegistrationForm
    if request.method == "POST":
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
            current_site = get_current_site(request)
            subject = "Activate your Shop!t Account"
            message = render_to_string(
                "account/registration/account_activation_email.html",
                {
                    "user": user,
                    "domain": current_site.domain,
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "token": account_activation_token.make_token(user),
                },
            )
            user.email_user(subject=subject, message=message)
            return render(request, "account/registration/registration-success.html")
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
        {"userprofileform": userprofileform, "account": account, "user_profile":user_profile},
    )


@login_required(login_url="/account/login/")
def store_account(
    request,
):
    if request.user.store_creator == True:
        currencies = Currency.objects.all()
        account = request.user
        store = Store.objects.get(owner=account)
        storeform = StoreForm(instance=store)
        if request.method == "POST":
            storeform = StoreForm(request.POST, request.FILES, instance=store)
            if storeform.is_valid():
                store_name = storeform.cleaned_data["store_name"]
                form = storeform.save(commit=False)
                form.owner = request.user
                form.slugified_store_name = slugify(store_name)
                form.save()
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
            },
        )
    else:
        return redirect("account:user_profile")

def accept_staff_invitation(request, pk, slugified_store_name):
    store = Store.objects.get(slugified_store_name=slugified_store_name)
    if store_staff.objects.filter(pk=pk, store=store).exists():
        staff = store_staff.objects.get(pk=pk)
        staff.is_active = True
        staff_store_user = User.objects.get(email=staff.email)
        store.staffs.add(staff_store_user)
        staff_store_user.store = store
        staff_store_user.save()
        staff.save()


def store_staff_register(request, slugified_store_name):
    if Store.objects.filter(slugified_store_name=slugified_store_name).exists():
        store = Store.objects.get(slugified_store_name=slugified_store_name)
        form = StoreStaffForm
        if request.method == "POST":
            form = StoreStaffForm(request.POST, request.FILES)
            if form.is_valid():
                staff_user = form.save(commit=False)
                staff_user.store = store
                user = User.objects.create(
                    email=form.cleaned_data["email"],
                    full_name=form.cleaned_data["full_name"],
                    phone_number=form.cleaned_data["phone_number"],
                    is_active=False,
                    is_staff=False,
                    store_creator=False,
                    store_staff=True,
                )
                user.set_password(form.cleaned_data["password"])
                user.save()
                staff_user.user = user
                staff_user.save()
                store.staffs.add(user)
                current_site = get_current_site(request)
                subject = "Activate your Shop!t Account"
                message = render_to_string(
                    "account/registration/account_activation_email.html",
                    {
                        "user": user,
                        "domain": current_site.domain,
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "token": account_activation_token.make_token(user),
                        "staff": True,
                        "store": store,
                    },
                )
                user.email_user(subject=subject, message=message)
                return render(request, "account/registration/registration-success.html")
    else:
        messages.error(request, "Store not found")
    return render(
        request, "account/registration/store-staff-register.html", {"form": form}
    )


@login_required(login_url="/account/login/")
def add_store_staff(request):
    form = ExistingStoreStaffForm
    if request.user.store_creator != True:
        error = "You are not authorized"
        return render(request, "store/store-staff-page.html", {"error": error})

    if request.user.store_creator == True:
        store = Store.objects.get(owner=request.user)
        if request.method == "POST":
            email = request.POST.get("email")
            if User.objects.filter(email=email).exists():
                user = User.objects.get(email=email)
                if user.store_creator == False:
                    if user not in store.staffs.all():
                        staff_store_user = User.objects.get(email=user.email)
                        if staff_store_user:
                            store = Store.objects.get(owner=request.user)
                            staff = store_staff.objects.create(
                                store=store,
                                user=staff_store_user,
                                full_name=staff_store_user.full_name,
                                email=staff_store_user.email,
                                phone_number=staff_store_user.phone_number,
                                avatar=staff_store_user.avatar,
                                password=staff_store_user.password,
                                is_active = False
                            )
                            current_site = get_current_site(request)
                            subject = f"{store.store_name} - Staff Permission Activation"
                            message = render_to_string(
                                "account/registration/store_staff_email.html", 
                                {
                                    "user": staff_store_user,
                                    "store": store,
                                    "domain": current_site.domain,
                                    "existing_user": True,
                                    "staff": staff
                                }
                            )
                            staff_store_user.email_user(subject=subject, message=message) 
                            return redirect("account:store_staff_page")
                        else:
                            error = "User is not eligible to be a staff yet"
                            return render(
                                request,
                                "account/registration/add-store-staff-exist.html",
                                {"form": form, "error": error},
                            )
                    error = "User is already a staff"
                    return render(
                        request,
                        "account/registration/add-store-staff-exist.html",
                        {"form": form, "error": error},
                    )
                error = "Store creator can't be a staff"
                return render(
                    request,
                    "account/registration/add-store-staff-exist.html",
                    {"form": form, "error": error},
                )
            else:
                subject = f"{store.store_name} - Staff Permission Activation"
                message = render_to_string(
                    "account/registration/store_staff_email.html", 
                    {
                        "user": staff_store_user,
                        "store": store,
                        "domain": current_site.domain,
                        "existing_user": False
                    }
                )
                store_staff_register(request, store.slugified_store_name)
            return redirect("account:staff_stores")
    return render(
        request, "account/registration/add-store-staff-exist.html", {"form": form}
    )


@login_required(login_url="/account/login/")
def delete_store_staff(request, pk):
    if request.user.store_creator == True:
        store = Store.objects.get(owner=request.user)
        staff = store_staff.objects.get(pk=pk)
        staff_stores = Store.objects.filter(staffs=staff.user)
        customer_stores = Customer.objects.filter(user=staff.user)
        if staff:
            staff.delete()
            store.staffs.remove(staff.user)
            if staff_stores or customer_stores or staff.user.store_creator == True:
                return redirect("account:store_staff_page")
            else:
                staff.user.delete()
                return redirect("/")
        else:
            return redirect("account:store_staff_page")
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
            store=store.store_name
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
                return redirect("/")
    return render(request, "account/registration/add-store.html", {"form": form})


@login_required(login_url="/account/login/")
def shipping_method_list(request):
    if request.user.store_creator == True:
        store = Store.objects.get(owner=request.user)
    else:
        store = store_staff.objects.get(user=request.user).store
    shipping_methods = Shipping_Method.objects.filter(store=store)
    return render(
        request,
        "store/all-shipping-method.html",
        {"shipping_methods": shipping_methods, "store": store},
    )


@login_required(login_url="/account/login/")
def add_shipping_method(request):
    if request.user.store_creator == True:
        store = Store.objects.get(owner=request.user)
        form = ShippingMethodForm
        if request.method == "POST":
            form = ShippingMethodForm(request.POST)
            if form.is_valid():
                location = form.cleaned_data["location"]
                shipping_method = form.save(commit=False)
                shipping_method.store = store
                if Shipping_Method.objects.filter(
                    location=location, store=store
                ).exists():
                    error = "Shipping Method already exists"
                    return render(
                        request,
                        "store/shipping-method.html",
                        {"form": form, "error": error},
                    )
                if not store.currency:
                    error = "Please select a currency in your store settings"
                    return render(
                        request,
                        "store/shipping-method.html",
                        {"form": form, "error": error},
                    )
                shipping_method.save()
                return redirect("account:shipping_method_list")
        return render(request, "store/shipping-method.html", {"form": form})
    else:
        error = "You are not authorized"
        return render(
            request, "store/shipping-method.html", {"error": error, "form": form}
        )


@login_required(login_url="/account/login/")
def edit_shipping_method(request, pk):
    if request.user.store_creator == True:
        store = Store.objects.get(owner=request.user)
        shipping_method = get_object_or_404(Shipping_Method, pk=pk)
        form = ShippingMethodForm(instance=shipping_method)
        if request.method == "POST":
            form = ShippingMethodForm(request.POST, instance=shipping_method)
            if form.is_valid():
                shipping_method = form.save(commit=False)
                shipping_method.store = store
                if Shipping_Method.objects.filter(
                    location=shipping_method.location, store=store
                ).exists():
                    error = "Shipping Method already exists"
                    return render(
                        request,
                        "store/shipping-method.html",
                        {"form": form, "error": error},
                    )
                shipping_method.save()
                return redirect("account:shipping_method_list")
        return render(request, "store/shipping-method.html", {"form": form})
    else:
        error = "You are not authorized"
        return render(
            request, "store/shipping-method.html", {"error": error, "form": form}
        )


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
        else:
            form = BankForm()
            error = "Please select a currency in your store settings"
            return render(
                request, "store/bank-details.html", {"error": error, "form": form}
            )
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
                    if resolve_account_details(request, bank_info.account_number, bank_info.bank_code): 
                        response = resolve_account_details(request, bank_info.account_number, bank_info.bank_code)
                        account_name = response.get("data").get("account_name")
                        bank_info.account_name = account_name
                        bank_info.save()
                        Bank_Info.objects.exclude(pk=bank_info.pk).filter(store=store).delete()
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
                    Bank_Info.objects.exclude(pk=bank_info.pk).filter(store=store).delete()
                    return redirect("account:bank_details")
        return render(
            request,
            "store/bank-details.html",
            {"form": form, "all_banks": all_banks, "bank_info": bank_info},
        )
