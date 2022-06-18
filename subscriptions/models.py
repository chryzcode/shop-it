from django.db import models

# Create your models here.

class Subscription(models.Model):
    name = models.CharField(max_length=100)
    price = models.PositiveIntegerField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    monthly = models.BooleanField(default=False)
    yearly = models.BooleanField(default=False)

    def __str__(self):
        return self.name
