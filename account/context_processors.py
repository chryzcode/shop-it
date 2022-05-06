from .models import *

def a_staff_store_store(request):
    if request.user.is_authenticated:
        if request.user.store_creator == True:
            return {"a_staff_store_store": request.user.store_name}
            
        else:
            store = store_staff.objects.get(user = request.user).store
            return {"a_staff_store_store": store}
    else:
        return {"a_staff_store_store": None}

def multiple_store_staff(request):
    if request.user.is_authenticated:
        stores = Store.objects.filter(staffs = request.user)
        if stores:
            print(stores)
            if stores.count() > 1:
                return {"multiple_store_staff": True}
            else:
                return {"multiple_store_staff": None}
        else:
            return {"multiple_store_staff": None}
    else:
        return {"multiple_store_staff": None}
