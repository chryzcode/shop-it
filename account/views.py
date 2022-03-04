from atexit import register
from base64 import urlsafe_b64encode
from email import message
from django.shortcuts import render, redirect
from .forms import RegistrationForm

# Create your views here.

def account_register(request):
    if request.user.is_authenteticated:
        return redirect('/')

    if request.method == "POST":
        registerform = RegistrationForm(request.POST, request.FILES)
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
                'uid': urlsafe_b64encode((force_bytes(user.pk)))
                'token': account_activation_token.make_token(user),
            })
            user.email_user(subject=subject, message=message)