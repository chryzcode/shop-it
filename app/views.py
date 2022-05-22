from django.shortcuts import get_object_or_404, redirect, render
# from django.contrib.auth import authenticate, login, logout
# from .forms import *
# from .models import *
# from account.models import *
# from datetime import datetime, timedelta
# from cart.cart import *
# from django.http import JsonResponse
# from decimal import Decimal
# from django.utils.text import slugify
# # Create your views here.


def custom_error_404(request, exception):
    return render(request, "error-pages/404-page.html")


def custom_error_500(request):
    return render(request, "error-pages/500-page.html")


# def home_page(request):
#     return render(request, "base/index.html")


# def a_store_all_products(request):
#     if request.user.store_creator == True:
#         all_products = Product.objects.filter(created_by= request.user.store_name)
#     else:
#         all_products = Product.objects.filter(created_by= store_staff.objects.get(user = request.user).store)
#     return render(
#         request,
#         "store/products.html",
#         {"all_products": all_products},
#     )


# def product_detail(request, slug, slugified_store_name):
#     page = "product_detail"
#     if request.user.is_authenticated:
#         product = get_object_or_404(Product, slug=slug)
#         if request.user.store_creator == True:
#             store_name = product.created_by
#         else:
#             store_name = store_staff.objects.get(user = request.user).store
#         category_product = Product.objects.filter(
#             category=product.category, created_by=store_name
#         ).exclude(id=product.id)[:6]
#     else:
#         product = get_object_or_404(Product, slug=slug)
#         category_product = Product.objects.filter(
#             category=product.category, created_by=product.created_by
#         ).exclude(id=product.id)[:6]
#     store = Store.objects.get(store_name=product.created_by)
#     return render(
#         request,
#         "product/product-detail.html",
#         {"product": product, "category_product": category_product, "store": store, "page":page},
#     )


# def create_product(request):
    
#     form = ProductForm
#     product_units = ProductUnit.objects.all()
#     if request.user.store_creator == True:
#         store = request.user.store_name
#     else:
#         store = store_staff.objects.get(user = request.user).store
    
#     if request.method == "POST":
#         form = ProductForm(request.POST, request.FILES)
#         if form.is_valid():
#             product = form.save(commit=False)
#             product.created_by = store
#             product.save()
#             return redirect(
#                 "app:product_detail",
#                 slug=product.slug,
#             )
#     categories = Category.objects.all().filter(created_by=store)
#     context = {"form": form, "categories": categories, "product_units": product_units}
#     return render(request, "store/create-product.html", context)


# def edit_product(request, slug):
#     if request.user.store_creator == True:
#         store = request.user.store_name
#     else:
#         store = store_staff.objects.get(user = request.user).store
#     product = get_object_or_404(Product, slug=slug, created_by=store)
#     form = ProductForm(instance=product)
#     categories = Category.objects.filter(created_by=store)
#     product_units = ProductUnit.objects.all()
#     if request.method == "POST":
#         form = ProductForm(request.POST, request.FILES, instance=product)
#         if form.is_valid():
#             product = form.save(commit=False)
#             product.created_by = store
#             product.save()
#             return redirect(
#                 "app:product_detail",
#                 slug=product.slug,
#             )
#     context = {
#         "form": form,
#         "categories": categories,
#         "product_units": product_units,
#         "product": product,
#     }
#     return render(request, "store/create-product.html", context)


# def delete_product(request, slug):
#     if request.user.store_creator == True:
#         product = get_object_or_404(Product, slug=slug, created_by=request.user.store_name)
#         product.delete()
#         return redirect("app:store_products")
#     else:
#        return redirect("app:store_products")

# def store_admin(request):
#     return render(request, "store/store-admin.html")

# def store(request, slugified_store_name):
#     store = get_object_or_404(Store, slugified_store_name=slugified_store_name)
#     products = Product.objects.filter(created_by=store).order_by("-created")
#     return render(request, "store/store.html", {"store": store, "products": products})


# def store_customers(request, slugified_store_name):
#     store = get_object_or_404(Store, slugified_store_name=slugified_store_name)
#     customers = store.customers.all()
#     return render(request, "store/store-customers.html", {"store": store, "customers": customers})


# def add_wishlist(request, slug):
#     user = request.user
#     product = get_object_or_404(Product, slug=slug)
#     product.wishlist.add(user)
#     return redirect("app:wishlist")


# def remove_wishlist(request, slug):
#     user = request.user
#     product = get_object_or_404(Product, slug=slug)
#     store = get_object_or_404(Store, store_name= product.created_by)
#     product.wishlist.remove(user)
#     return redirect("app:product_detail", slug=product.slug, slugified_store_name=slugify(store))


# def wishlist(request):
#     user = request.user
#     wishlist = Product.objects.filter(wishlist=user)
#     return render(request, "store/wishlist.html", {"wishlist": wishlist})

# def add_category(request):
#     form = CategoryForm
#     if request.method == "POST":
#         form = CategoryForm(request.POST, request.FILES)
#         if form.is_valid():
#             category = form.save(commit=False)
#             if request.user.store_creator == True:
#                 category.created_by = request.user.store_name
#                 category.save()
#                 return redirect(
#                     "app:all_category"           
#                 )
#             else:
#                 #get staff store name 
#                 staff = store_staff.objects.get(user = request.user)
#                 category.created_by = staff.store
#                 category.save()
#                 return redirect(
#                     "app:all_category"           
#                 )
#     context = {"form": form}
#     return render(request, "store/create-category.html", context)


# def edit_category(request, slug):
#     if request.user.store_creator == True:
#         category = get_object_or_404(Category, slug=slug, created_by= request.user.store_name)
    
#     else:
#         category = get_object_or_404(Category, slug=slug, created_by= store_staff.objects.get(user = request.user).store)

#     form = CategoryForm(instance=category)
#     if request.method == "POST":
#         form = CategoryForm(request.POST, request.FILES, instance=category)
#         if form.is_valid():
#             category = form.save(commit=False)
#             if request.user.store_creator == True:
#                 category.created_by = request.user.store_name 
#             else:
#                 category.created_by = store_staff.objects.get(user = request.user).store
#             category.save()
#             return redirect(
#                 "app:all_category"
#             )
#     context = {
#         "form": form,
#     }
#     return render(request, "store/create-category.html", context)

# def delete_category(request, slug):
#     if request.user.store_creator == True:
#         category = get_object_or_404(Category, slug=slug, created_by= request.user.store_name) 
#     else:
#         category = get_object_or_404(Category, slug=slug, created_by= store_staff.objects.get(user = request.user).store)
#     category.delete()
#     return redirect("app:all_category")


# def all_category(request):
#     if request.user.store_creator == True:
#         categories = Category.objects.filter(created_by=request.user.store_name)
#         context = {"categories":categories}
#         return render(request, "store/category.html", context)
#     else:
#         store = store_staff.objects.get(user = request.user).store
#         categories = Category.objects.filter(created_by= store)
#         context = {"categories":categories}
#         return render(request, "store/category.html", context)

# def a_store_all_categories(request, slugified_store_name):
#     store = get_object_or_404(Store, slugified_store_name=slugified_store_name)
#     all_categories = Category.objects.filter(created_by=store.store_name)
#     return render(
#         request,
#         "store/a-store-categories.html",
#         {"all_categories": all_categories},
#     )

# def a_store_category_products(request, slugified_store_name, slug):
#     store = get_object_or_404(Store, slugified_store_name=slugified_store_name)
#     category = get_object_or_404(Category, slug=slug, created_by=store.store_name)
#     category_products = Product.objects.filter(
#         category=category, created_by=store.store_name, in_stock=True
#     )
#     return render(
#         request,
#         "product/category-products.html",
#         {"category_products": category_products, "category": category},
#     )

# def discount_products(request):
#     if request.user.store_creator == True:
#         products = Product.objects.filter(created_by=request.user.store_name, discount_percentage__gt=0)  
#     else:
#         products = Product.objects.filter(created_by=store_staff.objects.get(user = request.user).store, discount_percentage__gt=0)
#     return render(
#         request,
#         "product/discount-products.html",
#         {"products": products},
#     )

# def create_coupon(request):
#     if request.user.store_creator == False:
#         error = 'You are not authorized to create coupons'
#         return render(request, "store/coupon.html", {"error": error})

#     else:
#         form = CouponForm
#         if request.method == "POST":
#             form = CouponForm(request.POST, request.FILES)
#             if form.is_valid():
#                 coupon = form.save(commit=False)
#                 coupon.created_by = request.user.store_name
#                 coupon.save()
#                 return redirect(
#                     "app:all_coupons"
#                 )
#         context = {"form": form}
#         return render(request, "store/create-coupon.html", context)

# def all_coupons(request):
#     if request.user.store_creator == True:
#         coupons = Coupon.objects.filter(created_by=request.user.store_name)
#     else:
#         coupons = Coupon.objects.filter(created_by=store_staff.objects.get(user = request.user).store)
#     for coupon in coupons:
#         expiry_date = (datetime.now().astimezone() - coupon.created_at)
#         expiry_date_seconds = expiry_date.total_seconds()
#         minutes = expiry_date_seconds/60
#         if int(minutes) > coupon.expiry_date:
#             coupon.delete()
#     return render(
#         request,
#         "store/coupon.html",
#         {"coupons": coupons},
#     )

# def delete_coupon(request, pk):
#     if request.user.store_creator == True:
#         coupon = get_object_or_404(Coupon, pk=pk, created_by=request.user.store_name, active=True)
#         coupon.delete()
#         return redirect("app:all_coupons")
#     else:
#         return redirect("app:all_coupons")

# def all_customers(request):
#     if request.user.store_creator == True:
#         store = request.user.store_name
#     if request.user.store_staff == True:
#         store = store_staff.objects.get(user = request.user).store
    
#     customers = Store.objects.get(store_name=store).customers.all()
#     return render(request, "store/customers.html", {"customers":customers})
               

