from multiprocessing import context
from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from .models import *
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import numpy as np
import cv2
from pyocr import pyocr
from pyocr import builders
from PIL import Image
from time import sleep
import imutils
from imutils.perspective import four_point_transform
import os
import glob
import datetime
import chartjs
# Create your views here


@login_required(login_url='login')
def index(request):
    user_objects = User.objects.get(username=request.user.username)             
    user_profile = Profile.objects.get(user=user_objects)                      
    car_profile = auto.objects.all().filter(connection = user_profile)          
    if request.method == 'POST':
        marka = request.POST['marka']
        model = request.POST['model']
        new_car = auto(marka=marka, model=model, connection=user_profile)
        new_car.save()
        return redirect('index')
    context = {'auta':car_profile, 'user':user_profile}
    return render(request, 'index.html', context)

@login_required(login_url='login')
def add(request, pk):

    users_car = auto.objects.get(id_auto=pk)            # users_car to CAŁY OBIEKT!!!!!
    cena_old = getattr(users_car, 'cena')               #Wyciągasz atrybut z obiektu users_cars
    litry_old = getattr(users_car, 'litry')

    if request.method=='POST':
        #przypisane z zmiennych w html
        cena = request.POST['cena']
        litry = request.POST['litry']
        lcena = request.POST['lcena']

        new_cena = float(cena_old) + float(cena)
        new_litry = float(litry_old) + float(litry)
        auto.objects.filter(id_auto=pk).update( cena=new_cena, litry=new_litry, lcena=lcena)
        new_history = history(cena_h = cena, litry_h = litry ,lcena_h = lcena,data = datetime.datetime.now(), connection_h = users_car)
        new_history.save()
        return redirect('/')

    context={'car':users_car}
    return render(request,'add.html',context )


@login_required(login_url='login') #funkcja edycji GOTOWA
def edit(request, pk):
    users_car = auto.objects.get(id_auto=pk)

    if request.method=='POST':
        marka = request.POST['marka']
        model = request.POST['model']
        cena = request.POST['cena']
        litry = request.POST['litry']
        lcena = request.POST['lcena']
        auto.objects.filter(id_auto=pk).update( marka=marka, model=model, cena=cena, litry=litry, lcena=lcena)
        return redirect('/')

    context={'car':users_car}
    return render(request,'edit.html',context )


@login_required(login_url='login') #funkcja usuwania GOTOWE
def delete(request, pk):

    users_car = auto.objects.get(id_auto=pk)
    if request.method=='POST':
        users_car.delete()
        return redirect('/')
    context={'car':users_car}
    return render(request,'delete.html', context)

#funkcja logowania GOTOWE
def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Niepoprawny login lub hasło')
            return redirect('login')
    else:
        return render(request, 'login.html')


#funckcja wylogowania GOTOWE
@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    return redirect('login')


#funkcja rejestracji GOTOWE
def register(request):

    if request.method =='POST':
        username = request.POST['username'] 
        email = request.POST['email']
        password = request.POST['password']
        repassword = request.POST['repassword']

        if password == repassword:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email istnieje')
                return redirect('register')
            elif User.objects.filter(username=username).exists(): 
                messages.info(request, 'Login już istnieje') 
                return redirect('register') 
            else:
                user = User.objects.create_user(username=username, email=email, password=password) 
                user.save() 
                user_model = User.objects.get(username=username)
                new_profile = Profile.objects.create(user=user_model, id_user=user_model.id)
                new_profile.save()
                return redirect('login')

        else:
            messages.info(request, 'Hasła się różnią!')
            return redirect('register')

    else:
        return render(request, 'register.html')



@login_required(login_url='login')
def dodaj(request, pk):
    car = auto.objects.get(id_auto=pk)
    context={'car':car}
    
    if request.method=='POST':
        
        if request.FILES.get('image') != None:
            image = request.FILES.get('image')
            car.image = image
            car.save()
        else:
            messages.info(request, 'Nie wprowadzono pliku')
            return redirect('/')

        
        
        def resize1():
            list_of_files = glob.glob('media/images/*')
            lastest_file = max(list_of_files, key=os.path.getctime)
            image = cv2.imread(os.path.join(lastest_file))
            image = imutils.resize(image, height=700)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            edged = cv2.Canny(blurred, 50, 200, 255)
            cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL,
	        cv2.CHAIN_APPROX_SIMPLE)
            cnts = imutils.grab_contours(cnts)
            cnts = sorted(cnts, key=cv2.contourArea, reverse=True)
            displayCnt = None
            for c in cnts:
                peri = cv2.arcLength(c, True)
                approx = cv2.approxPolyDP(c, 0.02 * peri, True)
                if len(approx) == 4:
                    displayCnt = approx
                    break
            output = four_point_transform(image, displayCnt.reshape(4, 2))
            height = output.shape[0]
            width = output.shape[1]
            cutoff = height // 2
            price = output[:cutoff, :]
            litres = output[cutoff:, :]
            return price, litres


        def processing(t):

            thresh, erosion_iters, most_common_filter = t, 2, 4
            price, litres = resize1()
            tab = [price, litres]
            tab2 = []

            for i in range(len(tab)):
                roi = tab[i]
                kernel = np.ones((5, 5), np.uint8)
                roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
                roi = cv2.threshold(roi, thresh, 255, cv2.THRESH_BINARY)[1]
                roi = cv2.erode(roi, kernel, iterations=erosion_iters)
                tool = pyocr.get_available_tools()[0]  
                lang = 'ssd'
                txt = str(tool.image_to_string(Image.fromarray(roi), lang=lang, builder=builders.TextBuilder()))
                if '.' in txt:
                    txt = txt.replace('.', '')
                else:
                    pass
                try:
                    x  = float(txt)/100
                    tab2.append(x)
                except:
                    tab2.append(None)
            return tab2
    
        price = []
        litres = []

        for t in range(25,80,1):
            tab = processing(t)
            price.append(tab[0]) 
            litres.append(tab[1])
            
        def exeptnone(list):
            res = []
            for val in list:
                if val != None :
                    res.append(val)
            return res

        def most_frequent(List):
            counter = 0
            num = List[0]
            
            for i in List:
                curr_frequency = List.count(i)
                if curr_frequency != None:
                    if(curr_frequency> counter):
                        counter = curr_frequency
                        num = i
        
            return num
        clear_l = []
        clear_p = []
        clear_l = exeptnone(litres)
        clear_p = exeptnone(price)
        l = most_frequent(clear_l)
        p = most_frequent(clear_p)
        if p > l:
            
            request.session['cena'] = p
            request.session['litry'] = l
            
            return redirect(confirm,pk)
        else:
            messages.info(request, 'Błędne zjdęcie')
            return redirect('/')


    return render(request, 'dodaj.html', context)

@login_required(login_url='login')
def confirm(request,pk):
    car = auto.objects.get(id_auto=pk)
    cena = request.session['cena']
    litry = request.session['litry']
    lcena = round(cena/litry,2)
    
    context={
        'car':car,
        'cena':cena,
        'litry':litry,
        'lcena':lcena
    }

    if request.method == 'POST':
        cena = request.POST['cena']
        litry = request.POST['litry']
        lcena = request.POST['lcena']
        cena_old = getattr(car, 'cena')
        litry_old = getattr(car, 'litry')
        price_new = float(cena_old) + float(cena)
        litres_new = float(litry_old) + float(litry)
        auto.objects.filter(id_auto=pk).update(cena=price_new, litry=litres_new, lcena = lcena)
        new_history = history(cena_h = cena, litry_h = litry, lcena_h = lcena ,data = datetime.datetime.now(), connection_h = car)
        new_history.save()
        return redirect('/')

    return render(request, 'confirm.html', context)

@login_required(login_url='login')
def statystyki(request, pk):
    users_car = auto.objects.get(id_auto=pk)
    
    users_hist = history.objects.all().filter(connection_h = users_car).order_by('data')

    data = []
    data2 = []
    data3 = []
    labels = []

    for x in users_hist:
        data3.append(x.lcena_h)
        data2.append(x.litry_h)
        data.append(x.cena_h)
        labels.append(str(x.data)[:16])

    context={
        'car':users_car,
        'labels':labels,
        'data':data,
        'data2':data2,
        'data3':data3
        }
    return render(request, 'statystyki.html', context)