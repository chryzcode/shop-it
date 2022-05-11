from django.shortcuts import get_object_or_404, redirect, render
from .models import *
from account.models import *
from app.models import *
from .forms import *
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
# Create your views here.

def customer_register(request, slugified_store_name):
    form = CustomerForm
    store = Store.objects.get(slugified_store_name=slugified_store_name)
    slugified_store_name = store.slugified_store_name
    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.store = store
            email= form.cleaned_data["email"]
            check_email = User.objects.filter(email = email)
            if check_email:
                return redirect("customer:existing_user_customer_register", slugified_store_name)
            else:
                user = User.objects.create(
                    email= form.cleaned_data["email"],
                    full_name=form.cleaned_data["full_name"],
                    is_active = True,
                    is_staff = False,
                    store_creator = False,
                )
                user.set_password(form.cleaned_data["password"])
                user.save()
                customer.save()
                return redirect("customer:customer_login", slugified_store_name)
    return render(request, "customer/register.html", {"store": store, "slugified_store_name": slugified_store_name, "form": form})

def customer_login(request, slugified_store_name):
    context = {}
    store = Store.objects.get(slugified_store_name=slugified_store_name)
    slugified_store_name = store.slugified_store_name
    if request.user.is_authenticated:
        logout(request)
        return redirect("customer:customer_login", slugified_store_name=slugified_store_name)
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        try:
            user = get_object_or_404(User, email=email)
            if user:
                user = authenticate(request, email=email, password=password)
                if user:
                    if user in store.customers.all():
                        login(request, user)
                        return redirect("/")
                    else:
                        messages.error(request, "You are not a customer of this store.")
                else:
                    messages.error(request, "Password is incorrect")            
            else:
                messages.error(request, "User does not exist")
        except:
            messages.error(request, "User does not exist")
    return render(request, "customer/login.html", {"store": store, "slugified_store_name": slugified_store_name})

def existing_user_customer_register(request, slugified_store_name):
    form = ExistingUserCustomerForm
    store = Store.objects.get(slugified_store_name=slugified_store_name)
    slugified_store_name = store.slugified_store_name
    if request.method == "POST":
        form = ExistingUserCustomerForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            user = User.objects.get(email=email)
            if user not in store.customers.all():
                form.save(commit=False)
                customer = Customer.objects.create(
                    full_name = user.full_name,
                    email = user.email,
                    password = user.password,
                    password2 = user.password,
                    store = store.store_name,
                )
                customer.save()
                store.customers.add(user)
                return redirect("customer:customer_login", slugified_store_name=slugified_store_name)
            else:
                messages.error(request, "You are already a customer of this store.")

    return render(request, "customer/existing-user-register.html", {"store": store, "slugified_store_name": slugified_store_name, "form": form})

def customer_logout(request):
    logout(request)
    return redirect("/")

def customer_product_detail(request, slugified_store_name, slug):
        store = Store.objects.get(slugified_store_name=slugified_store_name)
        product = get_object_or_404(Product, created_by=store.store_name, slug=slug).order_by("-created_at")
        category_product = Product.objects.filter(
            category=product.category, created_by= store.store_name
        ).exclude(id=product.id)[:6]
        return render(
            request,
            "product/product-detail.html",
            {"product": product, "category_product": category_product},
        )


        

