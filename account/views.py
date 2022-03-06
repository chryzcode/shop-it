import email
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from .forms import RegistrationForm
from .models import User
from .tokens import account_activation_token

# Create your views here.

def account_login(request):
    context = {}
    if request.user.is_authenticated:
        return redirect('/')
    if request.method == "POST":
        email_or_store_name = request.POST['email_or_store_name']
        password = request.POST['password']

        try:
            user = User.objects.get(email=email_or_store_name) or User.objects.get(store_name=email_or_store_name)
        except:
            messages.error(request, 'Invalid email or store name')

        user = authenticate(request, email=user.email, password=password) or authenticate(request, store_name=user.store_name, password=password)

        if user is not None:
            login(request, user)
            return redirect('/')

    return render(request, 'account/registration/login.html', context)

def logoutPage(request):
    logout(request)
    return redirect("home")

def account_register(request):
    if request.user.is_authenticated:
        return redirect('/')
    registerform = RegistrationForm
    if request.method == "POST":
        registerform = RegistrationForm(request.POST)
        if registerform.is_valid():
            user = registerform.save(commit=False)
            user.email = registerform.cleaned_data['email']
            user.full_name = registerform.cleaned_data['full_name']
            user.store_name = registerform.cleaned_data['store_name']
            user.set_password(registerform.cleaned_data['password'])
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            subject = 'Activate your Shop!t Account'
            message = render_to_string('account/registration/account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            user.email_user(subject=subject, message=message)
            return render(request, 'account/registration/success-page.html')
    return render(request, 'account/registration/register.html', {'form':registerform})

def account_activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = get_object_or_404(User, pk=uid)
    except:
        return render(request, 'app/404-page.html')

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect('/')
    else:
        return render(request, 'app/404-page.html')

        
