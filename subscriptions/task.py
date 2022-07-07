from core.celery import app
from .models import *
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils import timezone
from datetime import datetime, timedelta

@app.task(name="subscription_check_mail_remainder")
def subscription_check_mail_remainder(request):
    try:
        for store in Store.objects.all():
            if Subscription_Timeline.objects.filter(store=store, mail_remainder=False).exists():
                subscription_timeline = Subscription_Timeline.objects.filter(store=store).first()
                yearly_duration = Duration.objects.get(name="yearly")
                monthly_duration = Duration.objects.get(name="monthly")
                current_site = get_current_site(request)
                if subscription_timeline.subscription.duration ==  monthly_duration:
                    if subscription_timeline.created_at < timezone.now() - timedelta(minutes=3): 
                        subject = "Your Shop!t Monthly Subscription is about to Expire"
                        store_owner =  store.owner
                        message = render_to_string( "subscriptions/subscription-mail-remainder.html", {
                            "store": store,
                            "duration": "monthly",
                        })
                        from_email = settings.EMAIL_HOST_USER
                        to_email = [store_owner.email]
                        send_mail(subject, message, from_email, to_email)
                        if store_staff.objects.filter(store=store).exists():
                            for staff in store_staff.objects.filter(store=store):
                                if staff.user.email:
                                    to_email = [staff.user.email]
                                    send_mail(subject, message, from_email, to_email)
                        subscription_timeline.mail_remainder = True
                        subscription_timeline.save()
                        
                if subscription_timeline.subscription.duration ==  yearly_duration:
                    if subscription_timeline.created_at < timezone.now() - timedelta(minutes=3): 
                        subject = "Your Shop!t Yearly Subscription is about to Expire"
                        store_owner =  store.owner
                        message = message = render_to_string( "subscriptions/subscription-mail-remainder.html", {
                            "store": store,
                            "duration": "yearly",
                        })
                        from_email = settings.EMAIL_HOST_USER
                        to_email = [request.user.email]
                        send_mail(subject, message, from_email, to_email)
                        if store_staff.objects.filter(store=store).exists():
                            for staff in store_staff.objects.filter(store=store):
                                if staff.user.email:
                                    to_email = [staff.user.email]
                                    send_mail(subject, message, from_email, to_email)
                        subscription_timeline.mail_remainder = True
                        subscription_timeline.save()
    except Exception as e:
        print(e)