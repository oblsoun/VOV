# forms.py

from django import forms
from .models import UploadedImage

class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = UploadedImage
        fields = ['image']
        widgets = {
            'image': forms.FileInput(attrs={'id': 'fileInput'}),
        }