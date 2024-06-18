import random
import string
from django.http import JsonResponse
from django.shortcuts import render,redirect
from .forms import *
from django.contrib import messages

# Create your views here.
def home(r):
    return render(r,'index.html')
def apply(r):
    form=ApplicationForm()
    if r.method=="POST":
        form=ApplicationForm(data=r.POST,files=r.FILES)
        if form.is_valid():
            if Voter.objects.filter(aadhaar_no=r.POST['aadhaar_no']):
                return JsonResponse({'success': False, 'errors': "Already exists",'exists':True,'old':True})
            elif Applications.objects.filter(aadhaar_no=r.POST['aadhaar_no'],disable="no"):
                return JsonResponse({'success': False, 'errors': "Already exists",'exists':True,'old':False})
            else:
                form.save()
                messages.success(r,'Application sent')
                return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': dict(form.errors.items()),'exists':False})
    return render(r,'apply.html',{"form":form})
def update(r):
    form=ApplicationForm()
    if r.method=="POST":
        form=ApplicationForm(data=r.POST,files=r.FILES)
        if form.is_valid():
            if not Voter.objects.filter(aadhaar_no=r.POST['aadhaar_no']):
                return JsonResponse({'success': False, 'errors': "Already exists",'exists':True,'old':True})
            elif Applications.objects.filter(aadhaar_no=r.POST['aadhaar_no'],disable="no"):
                return JsonResponse({'success': False, 'errors': "Already exists",'exists':True,'old':False})
            else:
                application_instance = form.save(commit=False)
                application_instance.apptype = "update"
                application_instance.save()
                messages.success(r,'Application sent')
                return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': dict(form.errors.items()),'exists':False})
    return render(r,'update.html',{"form":form})
def status(r):
    data=""
    n=0
    if r.method=="POST":
        q=r.POST['query']
        if Applications.objects.filter(aadhaar_no=q):
            data=Applications.objects.filter(aadhaar_no=q)
        else:
            n="No records"
        
    return render(r,'status.html',{"data":data,"n":n})
def display(r):
    data=""
    n=0
    if r.method=="POST":
        q=r.POST['query']
        if Voter.objects.filter(aadhaar_no=q):
            data=Voter.objects.get(aadhaar_no=q)
        else:
            n="No records"
    return render(r,'voterid.html',{"data":data,"n":n})

def view(r,id):
    data=Applications.objects.get(id=id)
    return render(r,'view.html',{"data":data})

def applications(r):
    data=Applications.objects.filter(disable="no")
    return render(r,'admin/applications.html',{"data":data})
def viewapplication(r,id):
    data=Applications.objects.get(id=id)
    return render(r,'admin/view.html',{"data":data})

def generateid():
    prefix = ''.join(random.choices(string.ascii_uppercase, k=3))
    numeric_part = ''.join(random.choices(string.digits, k=7))
    
    # Combine prefix and numeric part
    voter_id = f'{prefix}{numeric_part}'
    
    return voter_id
def dashboard(r):
    return render(r,'admin/home.html')
def updateapplication(r,id):
    data=Applications.objects.get(id=id)
    
    form=UpdateForm(instance=data)
    if r.method=="POST":
        form=UpdateForm(r.POST,instance=data)
        if form.is_valid():
            
            if r.POST['status']=="Approved":
                if data.apptype=="apply":
                    Voter(voterid=generateid(),
                        first_name=data.first_name ,
                        surname=data.surname ,
                        gender=data.gender ,
                        date_of_birth=data.date_of_birth ,
                        mobile_no=data.mobile_no ,
                        email=data.email ,
                        state=data.state ,
                        district=data.district ,
                        address=data.address ,
                        constituency=data.constituency ,
                        aadhaar_no=data.aadhaar_no ,
                        
                    ).save()
                else:
                    old=Voter.objects.get(aadhaar_no=data.aadhaar_no)
                    old.first_name=data.first_name 
                    old.surname=data.surname 
                    old.gender=data.gender 
                    old.date_of_birth=data.date_of_birth 
                    old.mobile_no=data.mobile_no 
                    old.email=data.email 
                    old.state=data.state 
                    old.district=data.district 
                    old.address=data.address 
                    old.constituency=data.constituency 
                    old.save()
                    
                data.disable="yes"
                data.save()
                
            elif r.POST['status']=="Rejected":
                data.disable="yes"
                data.save()
                
            form.save()
            return redirect('/a/applications')
                
    return render(r,'admin/update.html',{"form":form})