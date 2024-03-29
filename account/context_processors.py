from itertools import product
from unicodedata import category, name

from django.utils.text import slugify

from account.models import *
from app.models import *
from customer.models import *
from order.models import *
from subscriptions.models import *

from .models import *


def a_staff_store_store(request):
    if request.user.is_authenticated:
        if request.user.store_creator == True:
            store = Store.objects.get(owner=request.user)
            return {"a_staff_store_store": store}
        elif request.user.store_staff == True:
            store = store_staff.objects.get(email=request.user.email).store
            return {"a_staff_store_store": store}
        else:
            customer = Customer.objects.get(email=request.user.email)
            store = customer.store
            return {"a_staff_store_store": store}
    else:
        return {"a_staff_store_store": None}
  


def a_staff_store_store_slugified(request):
    if request.user.is_authenticated:
        if request.user.store_creator == True:
            return {"a_staff_store_store_slugified": slugify(request.user.store_name)}
        elif request.user.store_staff == True:
            store = store_staff.objects.get(email=request.user.email).store
            return {"a_staff_store_store_slugified": slugify(store)}
        else:
            customer = Customer.objects.get(email=request.user.email)
            store = customer.store
            return {"a_staff_store_store_slugified": slugify(store)}
    else:
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
        elif request.user.store_staff == True:
            store = store_staff.objects.get(email=request.user.email).store
        else:
            store = None
        products = Product.objects.filter(store=store)
        return {"store_products": products}
    else:
        return {"store_products": None}


def store_orders(request):
    if request.user.is_authenticated:
        if request.user.store_creator == True:
            store = Store.objects.get(owner=request.user)
        elif request.user.store_staff == True:
            store = store_staff.objects.get(email=request.user.email).store
        else:
            store = None
        orders = Order.objects.filter(store=store)
        return {"store_orders": orders}
    else:
        return {"store_orders": None}


def store_customers(request):
    if request.user.is_authenticated:
        if request.user.store_creator == True:
            store = Store.objects.get(owner=request.user)
        elif request.user.store_staff == True:
            store = store_staff.objects.get(email=request.user.email).store
        else:
            store = None
        customers = Customer.objects.filter(store=store)
        return {"store_customers": customers}
    else:
        return {"store_customers": None}


def get_store(request):
    url = request.path
    if "store" in url:
        if url.split("/")[2]:
            store_slug = url.split("/")[2]
            if Store.objects.filter(slugified_store_name=store_slug).exists():
                store = Store.objects.get(slugified_store_name=store_slug)
                if store:
                    return {"get_store": store}
                else:
                    return {"get_store": None}
            else:
                return {"get_store": None}
        else:
            return {"get_store": None}
    else:
        return {"get_store": None}


def get_store_products(request):
    url = request.path
    if "store" in url:
        if url.split("/")[2]:
            store_slug = url.split("/")[2]
            if Store.objects.filter(slugified_store_name=store_slug).exists():
                store = Store.objects.get(slugified_store_name=store_slug)
                if store:
                    if Product.objects.filter(store=store).exists():
                        products = Product.objects.filter(store=store)
                        return {"get_store_products": products}
                    else:
                        return {"get_store_products": None}
                else:
                    return {"get_store_products": None}
            else:
                return {"get_store_products": None}
        else:
            return {"get_store_products": None}
    else:
        return {"get_store_products": None}


def get_store_category_products(request):
    url = request.path
    if "store" and "category" in url:
        if url.split("/")[2] and url.split("/")[4]:
            store_slug = url.split("/")[2]
            product_category = url.split("/")[4]
            if Store.objects.filter(slugified_store_name=store_slug).exists():
                store = Store.objects.get(slugified_store_name=store_slug)
                if store:
                    if Category.objects.filter(
                        created_by=store, slug=product_category
                    ).exists():
                        category = Category.objects.get(
                            created_by=store, slug=product_category
                        )
                        if Product.objects.filter(
                            store=store, category=category.id
                        ).exists():
                            products = Product.objects.filter(
                                store=store, category=category.id
                            )
                            return {"get_store_category_products": products}
                        else:
                            return {"get_store_category_products": None}
                    else:
                        return {"get_store_category_products": None}
                else:
                    return {"get_store_category_products": None}
            else:
                return {"get_store_category_products": None}
        else:
            return {"get_store_category_products": None}
    else:
        return {"get_store_category_products": None}


def get_store_category(request):
    url = request.path
    if "store" and "category" in url:
        if url.split("/")[2] and url.split("/")[4]:
            store_slug = url.split("/")[2]
            product_category = url.split("/")[4]
            if Store.objects.filter(slugified_store_name=store_slug).exists():
                store = Store.objects.get(slugified_store_name=store_slug)
                if store:
                    if Category.objects.filter(
                        created_by=store, slug=product_category
                    ).exists():
                        category = Category.objects.get(
                            created_by=store, slug=product_category
                        )
                        return {"get_store_category": category}
                    else:
                        return {"get_store_category": None}
                else:
                    return {"get_store_category": None}
            else:
                return {"get_store_category": None}
        else:
            return {"get_store_category": None}
    else:
        return {"get_store_category": None}


def get_customer_orders(request):
    url = request.path
    if "customer" and "orders" in url:
        store_slug = url.split("/")[2]
        if Store.objects.filter(slugified_store_name=store_slug).exists():
            store = Store.objects.get(slugified_store_name=store_slug)
            if store:
                if Customer.objects.filter(
                    store=store, email=request.user.email
                ).exists():
                    customer = Customer.objects.get(
                        store=store, email=request.user.email
                    )
                    user_customer = User.objects.get(email=customer.email)
                    if customer:
                        if Order.objects.filter(
                            user=user_customer, store=store
                        ).exists():
                            orders = Order.objects.filter(
                                user=user_customer, store=store
                            )
                            return {"get_customer_orders": orders}
                        else:
                            return {"get_customer_orders": None}
                    else:
                        return {"get_customer_orders": None}
                else:
                    return {"get_customer_orders": None}
            else:
                return {"get_customer_orders": None}
        else:
            return {"get_customer_orders": None}
    else:
        return {"get_customer_orders": None}


def get_customer_reviews(request):
    url = request.path
    if "customer" and "reviews" in url:
        store_slug = url.split("/")[2]
        if Store.objects.filter(slugified_store_name=store_slug).exists():
            store = Store.objects.get(slugified_store_name=store_slug)
            if store:
                if Customer.objects.filter(
                    store=store, email=request.user.email
                ).exists():
                    customer = Customer.objects.get(
                        store=store, email=request.user.email
                    )
                    user_customer = User.objects.get(email=customer.email)
                    if customer:
                        if Review.objects.filter(
                            email=user_customer.email, store=store
                        ).exists():
                            reviews = Review.objects.filter(
                                email=user_customer.email, store=store
                            )
                            return {"get_customer_reviews": reviews}
                        else:
                            return {"get_customer_reviews": None}
                    else:
                        return {"get_customer_reviews": None}
                else:
                    return {"get_customer_reviews": None}
            else:
                return {"get_customer_reviews": None}
        else:
            return {"get_customer_reviews": None}
    else:
        return {"get_customer_reviews": None}


def get_newsletter_id(request):
    url = request.path
    if "edit" and "newsletter" and "draft" in url:
        if url.split("/")[4]:
            newsletter_id = url.split("/")[4]
            return {"get_newsletter_id": newsletter_id}
        else:
            return {"get_newsletter_id": None}
    else:
        return {"get_newsletter_id": None}

