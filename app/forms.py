from django import forms
import re
from .models import *
from datetime import date
class ApplicationForm(forms.ModelForm):
    class Meta:
        model=Applications
        fields=['first_name','surname','gender','date_of_birth','mobile_no','email','state','district','address','constituency','aadhaar_no','document_proof']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
    def clean_mobile_no(self):
        m=self.cleaned_data.get('mobile_no')
        if re.match(r'^\d{10}$',m):
            return m
        else:
            raise forms.ValidationError("Enter valid mobile number")
    def clean_aadhaar_no(self):
        m=self.cleaned_data.get('aadhaar_no')
        if re.match(r'^\d{12}$',m):
            return m
        else:
            raise forms.ValidationError("Enter valid aadhaar number")
    def clean_date_of_birth(self):
        m=self.cleaned_data.get('date_of_birth')
        today=date.today()
        age=today.year-m.year - ((today.month,today.day)<(m.month,m.day))
        if age>=18:
            return m
        else:
            raise forms.ValidationError("Age is less than qualifying date")
class UpdateForm(forms.ModelForm):
    class Meta:
        model=Applications
        fields=['status']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
   
