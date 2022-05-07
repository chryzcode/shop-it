from django.shortcuts import get_object_or_404, redirect, render
from .models import *
from .forms import *
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
# Create your views here.

def customer_register(request, slugified_store_name):
    store = Store.objects.get(store_name=slugified_store_name)
    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.store = store
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
            return render(request, "customer/register_success.html")
    return render(request, "customer/register.html", {"store": store})

def customer_login(request, slugified_store_name):
    context = {}
    store = Store.objects.get(slugified_store_name=slugified_store_name)
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

        

