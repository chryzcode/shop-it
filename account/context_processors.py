from .models import *
from django.utils.text import slugify

def a_staff_store_store(request):
    if request.user.is_authenticated:
        if request.user.store_creator == True:
            return {"a_staff_store_store": request.user.store_name}
            
        else:
            store = store_staff.objects.get(user = request.user).store
            return {"a_staff_store_store": store}
    else:
        return {"a_staff_store_store": None}

def a_staff_store_store_slugified(request):
    if request.user.is_authenticated:
        if request.user.store_creator == True:
            return {"a_staff_store_store_slugified": slugify(request.user.store_name)}
            
        else:
            store = store_staff.objects.get(user = request.user).store
            return {"a_staff_store_store_slugified": slugify(store)}
    else:
        return {"a_staff_store_store": None}

def multiple_store_staff(request):
    if request.user.is_authenticated:
        stores = Store.objects.filter(staffs = request.user)
        if stores:
            if stores.count() > 1:
                return {"multiple_store_staff": True}
            else:
                return {"multiple_store_staff": None}
        else:
            return {"multiple_store_staff": None}
    else:
        return {"multiple_store_staff": None}
