from django.db import models
from fileDeidentificationApp.models import User,Frequency,MyPhoto
User.objects.all()
Frequency.objects.all()
MyPhoto.objects.all()

class CapturedImage(models.Model):
    image = models.ImageField(upload_to='captured_images/')
    upload_date = models.DateTimeField(auto_now_add=True)