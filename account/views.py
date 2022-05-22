# from django.contrib import messages
# from django.contrib.auth import authenticate, login, logout
# from django.contrib.auth.decorators import login_required
# from django.contrib.sites.shortcuts import get_current_site
# from django.shortcuts import get_object_or_404, redirect, render
# from django.template.loader import render_to_string
# from django.utils.encoding import force_bytes, force_str
# from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

# from .forms import *
# from .models import User, store_staff, Store
# from .tokens import account_activation_token


# def account_login(request):
#     context = {}
#     if request.user.is_authenticated:
#         return redirect("/")

#     if request.method == "POST":
#         email = request.POST.get("email")
#         password = request.POST.get("password")
#         try:
#             user = get_object_or_404(User, email=email)
#             if user:
#                 user = authenticate(request, email=email, password=password)
#                 if user:
#                     if user.store_creator == True:
#                         login(request, user)
#                         return redirect("/")

#                     if user.store_staff == True:
#                         login(request, user)
#                         return redirect("account:staff_stores")

#                     if user.store_creator == False and user.store_staff == False:
#                         login(request, user)
#                         return redirect("/")
#                         # messages.error(request, "You are not a store staff or store creator")  

#                 else:
#                     messages.error(request, "Password is incorrect")
#             else:
#                 messages.error(request, "Email is incorrect")
#         except:
#             messages.error(request, "Email is incorrect")

#     return render(request, "account/registration/login.html", context)


# def account_logout(request):
#     logout(request)
#     return redirect("/")


# def account_delete(request):
#     request.user.delete()
#     return redirect("/")


# def account_register(request):
#     if request.user.is_authenticated:
#         return redirect("/")
#     registerform = RegistrationForm
#     if request.method == "POST":
#         registerform = RegistrationForm(request.POST)
#         if registerform.is_valid():
#             user = registerform.save(commit=False)
#             user.email = registerform.cleaned_data["email"]
#             user.full_name = registerform.cleaned_data["full_name"]
#             user.store_name = registerform.cleaned_data["store_name"]
#             user.set_password(registerform.cleaned_data["password"])
#             user.is_active = False
#             user.store_staff = False
#             user.save()
#             store = Store.objects.create(
#                 owner = user,
#                 store_name = registerform.cleaned_data["store_name"],
#             )
#             current_site = get_current_site(request)
#             subject = "Activate your Shop!t Account"
#             message = render_to_string(
#                 "account/registration/account_activation_email.html",
#                 {
#                     "user": user,
#                     "domain": current_site.domain,
#                     "uid": urlsafe_base64_encode(force_bytes(user.pk)),
#                     "token": account_activation_token.make_token(user),
#                 },
#             )
#             user.email_user(subject=subject, message=message)
#             return render(request, "account/registration/registration-success.html")
#     return render(request, "account/registration/register.html", {"form": registerform})


# def account_activate(request, uidb64, token):
#     try:
#         uid = force_str(urlsafe_base64_decode(uidb64))
#         user = get_object_or_404(User, pk=uid)
#     except:
#         return render(request, "app/404-page.html")

#     if user is not None and account_activation_token.check_token(user, token):
#         user.is_active = True
#         user.save()
#         login(request, user)
#         return redirect("/")
#     else:
#         return render(request, "error-pages/404-page.html")


# def user_profile(request):
#     account = request.user
#     userprofileform = UserProfileForm(instance=account)
#     if request.method == "POST":
#         userprofileform = UserProfileForm(request.POST, request.FILES, instance=account)
#         if userprofileform.is_valid():
#             userprofileform.save()
#             return redirect("/")

#     return render(
#         request,
#         "account/user/user-profile.html",
#         {"userprofileform": userprofileform, "account": account},
#     )

# def store_account(request):
#     if request.user.store_creator == True:
#         account = request.user
#         storeform = StoreForm(instance=account)
#         if request.method == "POST":
#             storeform = StoreForm(request.POST, request.FILES, instance=account)
#             if storeform.is_valid():
#                 storeform.save()
#                 return redirect("/")

#         return render(
#             request, 
#             "account/user/store-account.html",
#             {"storeform": storeform, "account": account}
#         )
#     else:
#         return redirect("account:user_profile")

# def store_staff_page(request):
#     if request.user.store_creator == True:
#         store_staffs = store_staff.objects.filter(store=request.user.store_name)
#         return render(request, "store/store-staff-page.html", {"store_staffs": store_staffs})
#     else:
#         store_name = store_staff.objects.get(user = request.user).store
#         store_staffs = store_staff.objects.filter(store=store_name)
#         return render(request, "store/store-staff-page.html", {"store_staffs": store_staffs})


# def store_staff_register(request):
#     error= ''
#     if request.user.store_creator == True:
#         form = StoreStaffForm   
#         if request.method == "POST":
#             form = StoreStaffForm(request.POST, request.FILES)
#             if form.is_valid():
#                 staff_user = form.save(commit=False)
#                 staff_user.store = request.user.store_name
#                 user = User.objects.create(
#                     email = form.cleaned_data["email"],
#                     full_name = form.cleaned_data["full_name"],
#                     phone_number = form.cleaned_data["phone_number"],
#                     is_active = True,
#                     is_staff = False,
#                     store_creator = False,
#                     store_staff = True,
#                 )
#                 user.set_password(form.cleaned_data["password"])
#                 user.save()
#                 staff_user.user = user
#                 staff_user.save()
#                 store = Store.objects.get(owner=request.user)
#                 store.staffs.add(user)       
#                 return redirect("account:store_staff_page")
#     else:
#         error = 'You are not authorized'
#         return render(request, "store/store-staff-page.html", {"error":error})

#     return render(request, "account/registration/store-staff-register.html", {"form": form})


# def existing_store_staff(request):
#     form = ExistingStoreStaffForm
#     if request.user.store_creator != True:
#         error = 'You are not authorized'
#         return render(request, "store/store-staff-page.html", {"error":error})

#     if request.user.store_creator == True:
#         store = Store.objects.get(owner=request.user)       
#         if request.method == "POST":
#             email = request.POST.get("email")
#             if User.objects.filter(email=email).exists():
#                 user = User.objects.get(email=email)
#                 if user.store_creator == False:
#                     if user not in store.staffs.all():                       
#                         staff_store_user = User.objects.get(email=user.email)
#                         if staff_store_user:
#                             store.staffs.add(user)
#                             staff_store_user.store = store.store_name
#                             staff_store_user.save()
#                             return redirect("account:store_staff_page")
#                         else:
#                             error = 'User is not eligible to be a staff yet'
#                             return render(request, "account/registration/add-store-staff-exist.html", {"form": form, "error": error})                         
#                     error = 'User is already a staff'
#                     return render(request, "account/registration/add-store-staff-exist.html", {"form": form, "error": error})
#                 error = 'Store creator can''t be a staff'
#                 return render(request, "account/registration/add-store-staff-exist.html", {"form": form, "error": error})
#             error = 'User does not exist'
#             return render(request, "account/registration/add-store-staff-exist.html", {"form": form, "error": error})
#     return render(request, "account/registration/add-store-staff-exist.html", {"form": form})



# def delete_store_staff(request, pk):
#     if request.user.store_creator == True:
#         store = Store.objects.get(owner=request.user)
#         user = get_object_or_404(User, pk=pk)
#         if user in store.staffs.all():
#             store.staffs.remove(user)      
#             return redirect("account:store_staff_page")
#     else:
#         error = 'You are not authorized'
#         return render(request, "store/store-staff-page.html", {"error":error})


# def staff_stores(request):
#     stores = Store.objects.filter(staffs = request.user)
#     if stores:
#         if stores.count() > 1:
#             return render(request, "account/user/staff-stores-page.html", {"stores":stores})
#         else:
#             # use select store function
#             return redirect("account:select_store", stores.first().slugified_store_name)
#     logout(request)
#     error = 'You are not a staff of any store'
#     return render(request, "account/registration/login.html", {"error": error})


# def select_store(request, slugified_store_name):
#     store = get_object_or_404(Store, slugified_store_name=slugified_store_name)
#     if request.user in store.staffs.all():
#         store_staff.objects.filter(email = request.user.email).update(store = store.store_name)
#         return redirect("/")

# def create_store(request):
#     if request.user.store_creator == False and request.user.store_staff == False:
#         form = AddStoreForm
#         user = request.user
#         if request.method == "POST":
#             form = AddStoreForm(request.POST, request.FILES)
#             if form.is_valid():
#                 store_name = form.cleaned_data["store_name"]
#                 user.store_name = store_name
#                 user.store_creator = True
#                 user.save()
#                 return redirect("/")
#     return render(request, "account/registration/add-store.html", {"form": form})
    


