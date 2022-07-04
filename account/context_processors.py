from django.utils.text import slugify

from .models import *
from app.models import *
from order.models import *
from customer.models import *

def a_staff_store_store(request):
    if request.user.is_authenticated:
        if request.user.store_staff == True:
            store = store_staff.objects.get(user=request.user).store
            return {"a_staff_store_store": store}
        if request.user.store_creator == True:
            return {"a_staff_store_store": request.user.store_name}
    return {"a_staff_store_store": None}


def a_staff_store_store_slugified(request):
    if request.user.is_authenticated:
        if request.user.store_creator == True:
            return {"a_staff_store_store_slugified": slugify(request.user.store_name)}

        if request.user.store_staff == True:
            store = store_staff.objects.get(user=request.user).store
            return {"a_staff_store_store_slugified": slugify(store)}

    return {"a_staff_store_store_slugified": None}


def multiple_store_staff(request):
    if request.user.is_authenticated:
        if request.user.store_staff == True:
            if Store.objects.filter(staffs=request.user):
                stores = Store.objects.filter(staffs=request.user)
                if stores:
                    if stores.count() > 1:
                        return {"multiple_store_staff": True}
                    else:
                        return {"multiple_store_staff": None}
                else:
                    return {"multiple_store_staff": None}
            else:
                return {"multiple_store_staff": None}
        return {"multiple_store_staff": None}
    else:
        return {"multiple_store_staff": None}


def owner_store(request):
    if request.user.is_authenticated:
        if request.user.store_creator == True:
            if Store.objects.filter(owner=request.user).exists():
                store = Store.objects.get(owner=request.user)
                return {"owner_store": store}
            else:
                return {"owner_store": None}
        else:
            return {"owner_store": None}
    return {"owner_store": None}

def user_profile(request):
    if request.user.is_authenticated:
        if User.objects.filter(email=request.user.email):
            user = User.objects.get(email=request.user.email)
            return {"user_profile": user}
        else:
            return {"user_profile": None}
    else:
        return {"user_profile": None}

def store_products(request): 
    if request.user.is_authenticated:
        if request.user.store_creator == True:
            store = Store.objects.get(owner=request.user)
        else:
            store = store_staff.objects.get(user=request.user).store
        products = Product.objects.filter(store=store)
        return {"store_products": products}
    else:
        return {"store_products": None}

def store_orders(request): 
    if request.user.is_authenticated:
        if request.user.store_creator == True:
            store = Store.objects.get(owner=request.user)
        else:
            store = store_staff.objects.get(user=request.user).store
        orders = Order.objects.filter(store=store)
        return {"store_orders": orders}
    else:
        return {"store_orders": None}

def store_customers(request):
    if request.user.is_authenticated:
        if request.user.store_creator == True:
            store = Store.objects.get(owner=request.user)
        else:
            store = store_staff.objects.get(user=request.user).store
        customers = Customer.objects.filter(store=store)
        return {"store_customers": customers}
    else:
        return {"store_customers": None}


