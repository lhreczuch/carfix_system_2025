from django.shortcuts import render,redirect, get_object_or_404
from .forms import LoginForm, RepairForm, CarForm, ClientForm, RepairFormWorkersUpdator, ClientEditForm, SpecificCarRepairForm, WorkLogForm, RepairCommentForm, RepairStatusForm, UserEditForm, SpecificClientCarForm, RepairImageForm, RepairEditForm, CarEditForm, CarSearchForm,RepairSearchForm,ClientSearchForm
from django.contrib.auth import authenticate, login as auth_login, logout 
from .models import Client, Car,Repair, Manager, Worker,  WorkLog, RepairComment, RepairActivityLog, RepairImage
from django.contrib.auth.models import User, Group
from datetime import date
import copy
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from .decorators import allowed_groups, unauthenticated_user
from django.http import HttpResponse
from django.contrib.auth import logout,update_session_auth_hash
from django.db.models import Q
from datetime import datetime
from django.utils import timezone
from django.contrib.auth.decorators import user_passes_test
import pytz

import random
import string
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages

# api imports below
from rest_framework import viewsets,status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import CarSerializer, RepairSerializer, CommentSerializer,WorkLogSerializer,RepairActivityLogSerializer, ClientSerializer, WorkerSerializer, ManagerSerializer,RepairImageSerializer
from rest_framework import generics
from rest_framework.exceptions import PermissionDenied
# authentication
from rest_framework.permissions import IsAuthenticated, BasePermission, IsAdminUser
from .permissions import IsClient, IsManager, IsWorker
from rest_framework_simplejwt.authentication import JWTAuthentication


import csv
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle,Paragraph,Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch


from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont




# @user_passes_test(lambda u: u.is_superuser)
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required()
@allowed_groups(allowed_groups=['admin','manager','worker','client'])
def main(request):
    user = request.user
    if user.is_superuser:
        return redirect('/admin')

    user_role = request.user.groups.first().name if request.user.groups.exists() else None
    if user_role == 'worker':
        return redirect(f'/worker-panel')
    elif user_role == 'client':
        return redirect(f'/client-panel')
    elif user_role == 'manager':
        return redirect(f'/manager-panel')
    else:
        return HttpResponse('Błąd: użytkownik nie posiada roli w systemie. Skontaktuj się ze wsparciem technicznym.')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required()
def logout_view(request):
    logout(request)
    return redirect('/login/')
    
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required()
@allowed_groups(allowed_groups=['client'])
def client_panel(request):
        
    
    client = Client.objects.get(user=request.user)
    cars = Car.objects.filter(owner=client)

    client_repairs = Repair.objects.filter(car__in=cars)
    return render(request,'client_panel.html',{'client':client,'cars':cars,'client_repairs':client_repairs})
    
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required()
@allowed_groups(allowed_groups=['manager'])
def manager_panel(request):
        
    manager = Manager.objects.get(user=request.user)

    unassigned_repairs = Repair.objects.filter(workers=None)
    repairs_with_forms_list = []
        
    for repair in unassigned_repairs:

        form = RepairFormWorkersUpdator(instance=repair)
        repairs_with_forms_list.append((repair,form))
    
    return render(request,'manager_panel.html',{'manager':manager,'repairs_with_forms_list':repairs_with_forms_list})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required()
@allowed_groups(allowed_groups=['worker'])
def worker_panel(request):

    worker = Worker.objects.get(user=request.user)
    worker_repairs = Repair.objects.filter(workers=worker)
    # taski, które są w naprawach, w których w polu workers jest ten user
    
    return render(request,'worker_panel.html',{'worker':worker,'worker_repairs':worker_repairs})


@unauthenticated_user
def login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request,username=username,password=password)
            if user:
                auth_login(request,user)
                if user.is_superuser:
                    return redirect('/admin')

                user_role = request.user.groups.first().name if request.user.groups.exists() else None
                if user_role == 'worker':
                    return redirect(f'/worker-panel')
                elif user_role == 'client':
                    return redirect(f'/client-panel')
                elif user_role == 'manager':
                    return redirect(f'/manager-panel')
                else:
                    return HttpResponse('Błąd: użytkownik nie posiada roli w systemie. Skontaktuj się ze wsparciem technicznym.')
                
            return HttpResponse('Nieprawidłowe dane dostępowe')
        return redirect('/login/')
        
           
    else:
        form = LoginForm()
        return render(request, 'login.html',{'form':form})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required()
@allowed_groups(allowed_groups=['admin','manager','worker','client'])
def car(request,pk):

    user_role = request.user.groups.first().name if request.user.groups.exists() else None
    car = Car.objects.get(id=pk)
    repairs = Repair.objects.filter(car=car)

    is_staff = False

    context ={
        'car':car,
        'repairs':repairs,
        'is_staff':is_staff,
    }

    if user_role == "manager" or user_role == "worker" or user_role == "admin":
        context['is_staff'] = True

    elif user_role == "client":
        if request.user != car.owner.user:
            return HttpResponse("Brak uprawnień")
    
    return render(request,'car_panel.html',context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required()
@allowed_groups(allowed_groups=['manager', 'worker','admin'])
def car_delete(request,pk):
    car = Car.objects.get(id=pk)
    car.delete()
    return redirect('/cars')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required()
@allowed_groups(allowed_groups=['manager', 'worker','admin'])
def car_edit(request,pk):
    car = Car.objects.get(id=pk)

    if request.method == "POST":
        form = CarEditForm(request.POST,instance=car)
        if form.is_valid():
            form.save()
    else:
        form = CarEditForm(instance=car)
        return render(request,'car_edit.html',{'form':form})
    return redirect(f'/cars/{pk}')
    

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required()
@allowed_groups(allowed_groups=['manager','worker','client','admin'])
def repair_panel(request,pk):

    try:
        repair = Repair.objects.get(id=pk)
    except:
        return HttpResponse('Nie odnaleziono naprawy')

    user_role = request.user.groups.first().name if request.user.groups.exists() else None

    worklog_form = WorkLogForm()
    worklogs = WorkLog.objects.filter(repair=repair)
    image_form = RepairImageForm()
    workers_update_form = RepairFormWorkersUpdator(instance=repair)
    repair_images = RepairImage.objects.filter(repair=repair)
    
    is_client=False
    comment_form = RepairCommentForm()
    repair_comments = RepairComment.objects.filter(repair = repair)
    repair_comments_for_client = RepairComment.objects.filter(repair = repair,visible_for_client=True)
    repair_status_form = RepairStatusForm()
    activity_logs = RepairActivityLog.objects.filter(repair=repair)

        
    context = {
        'repair':repair,
        'is_client':is_client,
        'workers': repair.workers.all(),
        'worklog_form': worklog_form,
        'comment_form':comment_form,
        'repair_comments': repair_comments,
        'worklogs': worklogs,
        'repair_status_form': repair_status_form,
        'activity_logs':activity_logs,
        'image_form':image_form,
        'repair_images':repair_images,
        
    }
    print(repair_images)
        
    if user_role == 'client':
        if request.user.client == repair.car.owner:
                
            del context['workers']
            # del context['repair_comments']
            del context['worklog_form']
            del context['comment_form']
            del context['worklogs']
            del context['repair_status_form']
            del context['activity_logs']
            context['repair_comments'] = repair_comments_for_client
            del context['image_form']
            del context['repair_images']
            context['is_client'] = True
        else:
            return HttpResponse("Brak uprawnień do przeglądarnia treści")
            
    if user_role == "manager" or user_role == 'admin':
        del context['worklog_form']
        workers_update_form = RepairFormWorkersUpdator()
        context['workers_update_form'] = workers_update_form
    
    
    return render(request,'repair_panel.html',context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required()
@allowed_groups(allowed_groups=['manager', 'worker','admin'])
def repair_edit(request,pk):

    repair = Repair.objects.get(id=pk)
    form = RepairEditForm(instance=repair)
    initial_data = form.initial

    if request.method == "POST":
        form = RepairEditForm(request.POST,instance=repair)
        if form.is_valid():
            
            form.save()
            new_data = form.cleaned_data
    
            RepairActivityLog.objects.create(
                repair=repair,
                user = request.user,
                description = f'Użytkownik {request.user} zedytował naprawę. Dane przed edycją: {initial_data} Nowe dane: {new_data}',
                type = 'Edycja naprawy',
                )

        return redirect(f'/repairs/{pk}')
    else:
        
        return render(request,'repair_edit.html',{'form':form})
    




@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required()
@allowed_groups(allowed_groups=['manager','worker','admin'])
def add_client(request):
    if request.method == "POST":

        client_form = ClientForm(request.POST)
        user_form = UserEditForm(request.POST)
        
        if user_form.is_valid():
            user_email = user_form.cleaned_data['email']
            if User.objects.filter(email=user_email).exists():
                return HttpResponse("Użytkownik o takim mailu już istnieje! Wróć i ponów wysłanie formularza.")

            user = user_form.save(commit=False)
            user.username = user_email
            user.save()

        if client_form.is_valid():
            client = client_form.save(commit=False)
            client.user = user
            client.save()


            return redirect('/clients')
    else:
        client_form = ClientForm()
        user_form = UserEditForm()
    return render(request, 'add_client.html',{'client_form':client_form,'user_form':user_form})
    

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required()
@allowed_groups(allowed_groups=['manager','worker','admin'])
def add_car(request):
    if request.method == "POST":
        form = CarForm(request.POST)
        
        if form.is_valid():
            car = form.save(commit=False)
            car.registration_date = date.today()
            car.save()
            return redirect('/cars')
    else:
        form = CarForm()
    return render(request, 'add_car.html',{'form':form})



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required()
@allowed_groups(allowed_groups=['manager','worker','admin'])
def add_repair(request,pk=None):
    
    if request.method == "POST":

        
        if pk == None:
            form = RepairForm(request.POST,user=request.user)
        else:
            form = SpecificCarRepairForm(request.POST,user=request.user)
        
        
        if form.is_valid():

            if 'workers' in form.cleaned_data and not request.user.groups.filter(name='manager').exists():
                # Bezpiecznik na poziomie widoku
                return HttpResponse('Brak uprawnień')

            repair = form.save(commit=False)

            try:
                car = Car.objects.get(id=pk)
                repair.car = car
            except:
                pass
            
            # repair.registration_date = date.today()
            repair.save()
            form.save_m2m()

            repair_dict = copy.copy(repair.__dict__)
            print(repair_dict)

            keys_to_delete = ['registration_date','start_date','end_date','car_id']
            for key in keys_to_delete:
                del repair_dict[key]


            RepairActivityLog.objects.create(
            repair=repair,
            user = request.user,
            description = f'Użytkownik {request.user} utworzył naprawę. Dane: { {k: v for k, v in repair_dict.items() if k != "_state"}}',
            type = 'Utworzenie naprawy',
            )

            if repair.workers.all():
                RepairActivityLog.objects.create(
                repair=repair,
                user = request.user,
                description = f"Przypisani: {', '.join([f'{worker.user.first_name} {worker.user.last_name} (ID: {worker.id})' for worker in repair.workers.all()])}",
                type = 'Edycja przypisania',
                )

        if pk == None:
            return redirect(f'/repairs')
        else:
            return redirect(f'/cars/{repair.car.id}')

    else:
        if pk == None:
            form = RepairForm(user=request.user)
        else:
            form = SpecificCarRepairForm(user=request.user)

        context = {'form':form}

    return render(request, 'add_repair.html',context)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required()
@allowed_groups(allowed_groups=['manager','worker','admin'])
def cars(request):

    if len(request.GET.keys()) != 0:
        params_dict = request.GET.dict()
        filter_params = {k: v for k, v in params_dict.items() if v}

        
        query = Q()

        for key, value in filter_params.items():
            print(key,value)
            if key == 'owner':
                query &= Q(**{key: value})
            else:
                query &= Q(**{f"{key}__icontains": value})
        cars = Car.objects.filter(query)
    else:
        cars = Car.objects.all()
    search_form = CarSearchForm()
    return render(request,'cars.html',{'cars':cars,'search_form':search_form})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required()
@allowed_groups(allowed_groups=['manager','worker','admin'])
def clients(request):
    
    if len(request.GET.keys()) != 0:
        params_dict = request.GET.dict()
        filter_params = {k: v for k, v in params_dict.items() if v}
        query = Q()

        for key, value in filter_params.items():
            query &= Q(**{f"{key}__icontains": value})
        clients = Client.objects.filter(query)
    else:
        clients = Client.objects.all()
        
    search_form = ClientSearchForm()
    return render(request,'clients.html',{'clients':clients,'search_form':search_form})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required()
@allowed_groups(allowed_groups=['manager','admin'])
def workers(request):
    
    workers = Worker.objects.all()
    return render(request,'workers.html',{'workers':workers})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required()
@allowed_groups(allowed_groups=['manager','admin'])
def worker_view(request,pk):

    user_role = request.user.groups.first().name if request.user.groups.exists() else None
    if user_role == 'manager' or user_role == 'admin':
        is_manager_or_admin = True
    else:
        is_manager_or_admin = False

    worker = get_object_or_404(Worker, id=pk)
    repairs = Repair.objects.filter(workers=worker)
    return render(request,'worker.html',{'worker':worker,'repairs':repairs,'is_manager_or_admin':is_manager_or_admin})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required()
@allowed_groups(allowed_groups=['manager','admin'])
def worker_edit_view(request,pk):
    worker = get_object_or_404(Worker, id=pk)
    
    if request.method == 'POST':
        user_form = UserEditForm(request.POST,instance=worker.user)

        if user_form.is_valid():
            user_email = user_form.cleaned_data['email']
            user = user_form.save(commit=False)
            user.username = user_email
            user.save()
        return redirect(f'/workers/{worker.id}')

    else:
        repairs = Repair.objects.filter(workers=worker)

        user_form = UserEditForm(instance=worker.user)
        return render(request,'worker.html',{'worker':worker,'repairs':repairs,'user_form':user_form})
    
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required()
@allowed_groups(allowed_groups=['manager','admin'])
def worker_delete(request,pk):
    worker = Worker.objects.get(id=pk)
    worker.user.delete()
    return redirect('/workers')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required()
@allowed_groups(allowed_groups=['manager','worker','admin'])
def client_view(request,pk):
    client = get_object_or_404(Client, id=pk)
    client_cars = Car.objects.filter(owner=client)
    repairs = Repair.objects.filter(car__owner=client)
    return render(request,'client.html',{'client':client,'repairs':repairs,'cars':client_cars})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required()
@allowed_groups(allowed_groups=['manager', 'worker','admin'])
def client_edit_view(request,pk):
    client = get_object_or_404(Client, id=pk)
    client_cars = Car.objects.filter(owner=client)
    if request.method == 'POST':

        
        client_form = ClientEditForm(request.POST,instance=client)
        
        if client_form.is_valid():
            client_form.save()

        user_form = UserEditForm(request.POST,instance=client.user)

        if user_form.is_valid():
            user_email = user_form.cleaned_data['email']
            user = user_form.save(commit=False)

            user.username = user_email
            user.save()
            

        return redirect(f'/clients/{client.id}')

    else:
        repairs = Repair.objects.filter(car__owner=client)

        client_form = ClientEditForm(instance=client)
        user_form = UserEditForm(instance=client.user)
        return render(request,'client.html',{'client':client,'repairs':repairs,'cars':client_cars,'client_form':client_form,'user_form':user_form})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required()
@allowed_groups(allowed_groups=['manager', 'worker','admin'])
def client_delete(request,pk):
    
    client = Client.objects.get(id=pk)
    client.user.delete()
    return redirect('/clients')

    
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required()
@allowed_groups(allowed_groups=['manager','admin'])
def add_worker(request):
    if request.method == "POST":
        form = UserEditForm(request.POST)
        
        if form.is_valid():
            user_email = form.cleaned_data['email']

            if User.objects.filter(email=user_email).exists():
                return HttpResponse("Użytkownik o takim mailu już istnieje!")
            
            user = form.save(commit=False)
            user.username = user_email
            
            
            user.save()

            workers = Group.objects.get(name='worker') 
            user.groups.add(workers)
            user.save()

            
            return redirect('/workers')
    else:
        form = UserEditForm()
    return render(request, 'add_worker.html',{'form':form})

    

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required()
@allowed_groups(allowed_groups=['manager','worker','admin'])
def all_repairs(request):

    if len(request.GET.keys()) != 0:
        params_dict = request.GET.dict()
        filter_params = {k: v for k, v in params_dict.items() if v}

        
        query = Q()

        for key, value in filter_params.items():
            if key == 'workers' or key == "car":
                query &= Q(**{key: value})
            else:
                query &= Q(**{f"{key}__icontains": value})
        repairs = Repair.objects.filter(query)
    else:
        repairs = Repair.objects.all()
    search_form = RepairSearchForm()
    
    return render(request,'all_repairs.html',{'all_repairs':repairs,'search_form':search_form})
    

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required()
@allowed_groups(allowed_groups=['manager','worker','admin'])
def add_comment(request,pk):
    form = RepairCommentForm(request.POST)

    if form.is_valid():
        
        user = request.user
        repair = Repair.objects.get(id=pk)

        comment = form.save(commit=False)
        comment.creator = user
        comment.repair = repair
        comment.save()

        if comment.visible_for_client == True:
            visibility_type = "Komentarz publiczny"
        else:
            visibility_type = "Komentarz pracowniczy"

        RepairActivityLog.objects.create(
            repair=repair,
            user = request.user,
            description = f"Komentarz o ID {comment.id} o treści: '{comment.value}'",
            type = visibility_type
        )

    return redirect(f'/repairs/{pk}')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required()
@allowed_groups(allowed_groups=['manager', 'worker','admin'])
def comment_delete(request,pk,pk2):
    repair = Repair.objects.get(id=pk)
    comment = RepairComment.objects.get(id=pk2,repair=repair)

    if request.user == comment.creator or request.user.is_superuser:
        comment.delete()

        RepairActivityLog.objects.create(
            repair=repair,
            user = request.user,
            description = f"Usunięcie komentarza ID: '{pk2}'",
            type = "Usunięcie komentarza"
        )

    else:
        return HttpResponse("Brak uprawnień")
    return redirect(f'/repairs/{pk}')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required()
@allowed_groups(allowed_groups=['manager','worker','admin'])
def change_repair_status(request,pk):
    form = RepairStatusForm(request.POST)

    if form.is_valid():
        selected_status = form.cleaned_data['select_field']
        
        repair = Repair.objects.get(id=pk)
        repair.status = selected_status
        # if selected_status == "W trakcie" and repair.start_date == None:
        #     repair.start_date = timezone.now()
        # elif selected_status == "Wykonana":
        #     repair.end_date = timezone.now()

            # email notification to client:
            
            
        repair.save()

        RepairActivityLog.objects.create(
            repair=repair,
            user = request.user,
            description = f'Ustawienie statusu na: {selected_status}',
            type = 'Ustawienie statusu',
        )
        return redirect(f'/repairs/{pk}')
    


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required()
@allowed_groups(allowed_groups=['manager','worker','client'])
def password_edit(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Zapewnia, że użytkownik pozostanie zalogowany po zmianie hasła
            messages.success(request, 'Your password was successfully updated!')
            return redirect('/')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'password_reset.html', {'form': form})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required()
@allowed_groups(allowed_groups=['manager','worker','admin'])
def specific_client_add_car(request,pk):
    if request.method == "POST":
        form = SpecificClientCarForm(request.POST)
        client = Client.objects.get(id = pk)

        if form.is_valid():
            car = form.save(commit=False)
            car.owner = client
            car.registration_date = date.today()
            car.save()
            return redirect(f'/clients/{pk}')
    else:
        form = SpecificClientCarForm()
    return render(request, 'add_car.html',{'form':form})
        
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required()
@allowed_groups(allowed_groups=['manager','admin'])
def update_repair_workers(request,pk):
    if request.method == 'POST':
        
        repair = Repair.objects.get(id=pk)
        form = RepairFormWorkersUpdator(request.POST,instance=repair)
        request_path = request.POST.get('request_path')
        
        
        if form.is_valid():
            
            repair = form.save(commit=False)
            repair.save()
            form.save_m2m()

        RepairActivityLog.objects.create(
            repair=repair,
            user = request.user,
            description = f"Przypisani: {', '.join([f'{worker.user.first_name} {worker.user.last_name} (ID: {worker.id})' for worker in repair.workers.all()])}",

            type = 'Edycja przypisania',
        )

    return redirect(request_path)

def log_work(request,pk):
    if request.method == 'POST':
        repair = Repair.objects.get(id=pk)
        worker = Worker.objects.get(user=request.user)
        worklog_form = WorkLogForm(request.POST)
        worklog = worklog_form.save(commit=False)
        worklog.worker = worker
        worklog.repair = repair
        worklog.save()

        RepairActivityLog.objects.create(
            repair=repair,
            user = request.user,
            description = f'Użytkownik zalogował czasu: {worklog.duration()} \n Opis:\n{worklog.comment}',
            type = 'Zalogowanie czasu',
        )

    return redirect(f'/repairs/{pk}')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required()
@allowed_groups(allowed_groups=['manager','worker','admin'])
def repair_add_image(request,pk):
    if request.method == "POST":
        repair = Repair.objects.get(id=pk)
        form = RepairImageForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.save(commit=False)
            image.repair = repair
            image.user = request.user
            image.save()

            RepairActivityLog.objects.create(
            repair=repair,
            user = request.user,
            description = f'Użytkownik {request.user.first_name} {request.user.last_name} dodał zdjęcie ID: {image.id}',
            type = 'Dodanie zdjęcia',
            )
    return redirect(f'/repairs/{pk}')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required()
@allowed_groups(allowed_groups=['manager','worker','admin'])
def image_delete(request,pk,pk2):
    if request.method == "POST":
        repair = Repair.objects.get(id=pk)
        image = RepairImage.objects.get(pk=pk2)
        if image.user == request.user or request.user.is_superuser:
            image.delete()

            RepairActivityLog.objects.create(
            repair=repair,
            user = request.user,
            description = f'Użytkownik {request.user.first_name} {request.user.last_name} usunął zdjęcie ID: {pk2}',
            type = 'Usunięcie zdjęcia',
            )
    return redirect(f'/repairs/{pk}')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required()
@allowed_groups(allowed_groups=['manager','worker','admin'])
def image(request,pk,pk2):
    repair = Repair.objects.get(id=pk)
    image = RepairImage.objects.get(id=pk2)
    if image.repair == repair:
        return render(request,'image.html',{'image':image})
    else:
        return HttpResponse("Naprawa nie posiada takiego zdjęcia")
    
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required()
@allowed_groups(allowed_groups=['manager','worker','admin'])
def repair_csv(request,pk):
    repair = Repair.objects.get(id=pk)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename=repair_id_{repair.id}_report.csv'

    writer = csv.writer(response)

    activity_logs = RepairActivityLog.objects.filter(repair=repair)

    writer.writerow(['time','user','type','description'])
    
    for log in activity_logs:
        print(log.time)
        writer.writerow([log.time,log.user,log.type,log.description])

    return response

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required()
@allowed_groups(allowed_groups=['manager','worker','admin'])
def report_pdf(request, pk):
    # Pobranie danych
    repair = Repair.objects.get(id=pk)
    logs = RepairActivityLog.objects.filter(repair=repair)

    # Inicjalizacja odpowiedzi PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="repair_id_{repair.id}_report.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4, rightMargin=30, leftMargin=30)

    # 🔹 Rejestracja czcionki Arial z lokalnego katalogu Windows
    pdfmetrics.registerFont(TTFont('Arial', 'C:/Windows/Fonts/arial.ttf'))
    pdfmetrics.registerFont(TTFont('Arial-Bold', 'C:/Windows/Fonts/arialbd.ttf'))
    pdfmetrics.registerFont(TTFont('Arial-Italic', 'C:/Windows/Fonts/ariali.ttf'))
    pdfmetrics.registerFont(TTFont('Arial-BoldItalic', 'C:/Windows/Fonts/arialbi.ttf'))

    # 🔹 Style dla tekstu
    styles = getSampleStyleSheet()

    style_normal = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontName='Arial',
        fontSize=10
    )

    style_bold = ParagraphStyle(
        'Bold',
        parent=styles['Normal'],
        fontName='Arial-Bold',
        fontSize=10
    )

    title_style = ParagraphStyle(
        name='TitleStyle',
        fontName='Arial-Bold',
        fontSize=16,
        alignment=TA_CENTER,
        spaceAfter=14,
        textColor=colors.black
    )

    # 🔹 Nagłówek dokumentu
    title = Paragraph(f"Raport aktywności naprawy {repair} o ID {repair.id}", title_style)

    # 🔹 Dane tabeli
    data = [['Czas', 'Użytkownik', 'Typ', 'Opis']]  # Nagłówki tabeli

    # Przetwarzanie logów
    for log in logs:
        utc_time = datetime.fromisoformat(str(log.time)).replace(tzinfo=pytz.utc)
        warsaw_tz = pytz.timezone('Europe/Warsaw')
        local_time = utc_time.astimezone(warsaw_tz)
        log.time = local_time.strftime('%Y-%m-%d %H:%M:%S')

        row = [
            Paragraph(str(log.time), style_normal),
            Paragraph(str(log.user), style_bold),
            Paragraph(str(log.type), style_normal),
            Paragraph(str(log.description), style_normal)
        ]
        data.append(row)

    # 🔹 Tabela z danymi
    column_widths = [doc.width / len(data[0])] * len(data[0])
    table = Table(data, colWidths=column_widths)

    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONT', (0, 0), (-1, -1), 'Arial'),
        ('FONT', (0, 0), (-1, 0), 'Arial-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))

    # 🔹 Renderowanie dokumentu
    doc.build([title, Spacer(1, 0.5 * inch), table])

    return response

######
######
######
######
######
######
######
######
######
# api views below 






# cars

class CarsListCreate(generics.ListCreateAPIView):
    
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser|IsManager|IsWorker|IsClient]
    
    queryset = Car.objects.all()
    serializer_class = CarSerializer

    def get_queryset(self):
        if self.request.user.groups.first().name == 'client':
            client = Client.objects.get(user=self.request.user)
            cars = Car.objects.filter(owner=client)
            return cars
        else:
            return super().get_queryset()
        
    def post(self,request, *args, **kwargs):
        if request.user.groups.first().name == 'client':
            raise PermissionDenied('Brak dostępu')
        else:
            return super().post(request, *args, **kwargs)
        
    # def perform_create(self, serializer):
    #     user = self.request.user
    #     serializer.save(user=user)
    #     return super().perform_create(serializer)


class CarRetrieve(generics.RetrieveUpdateDestroyAPIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser|IsManager|IsWorker|IsClient]

    queryset = Car.objects.all()
    serializer_class = CarSerializer

    def get_object(self):
        if self.request.user.groups.first().name == 'client':

            car_id = self.kwargs["pk"]
            car = get_object_or_404(Car,id=car_id)

            client = get_object_or_404(Client,user=self.request.user)

            if car.owner == client:
                return car 
            else:
                raise PermissionDenied('Brak dostępu')
        else:
            return super().get_object()
        
    def put(self, request, *args, **kwargs):
        if request.user.groups.first().name == 'client':
            raise PermissionDenied('Brak dostępu')
        else:
            return super().put(request, *args, **kwargs)
        
    
    def patch(self, request, *args, **kwargs):
        if request.user.groups.first().name == 'client':
            raise PermissionDenied('Brak dostępu')
        else:
            return super().partial_update(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        if request.user.groups.first().name == 'client':
            raise PermissionDenied('Brak dostępu')
        else:
            return super().destroy(request, *args, **kwargs)
        



# repairs

class RepairListCreate(generics.ListCreateAPIView):


    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser|IsManager|IsWorker|IsClient]

    queryset = Repair.objects.all()
    serializer_class = RepairSerializer

    def get_queryset(self):
        user = self.request.user
        if user.groups.first().name == 'client':

            client = Client.objects.get(user=user)

            repairs = Repair.objects.filter(car__owner=client)
            
            return repairs
        else:
            return super().get_queryset()
        
    def post(self,request, *args, **kwargs):
        if request.user.groups.first().name == 'client':
            raise PermissionDenied('Brak dostępu')
        else:
            return super().post(request, *args, **kwargs)
        
            
    def perform_create(self, serializer):
        repair = serializer.save()
        repair_dict = copy.copy(repair.__dict__)

        keys_to_delete = ['registration_date','start_date','end_date','car_id']
        for key in keys_to_delete:
            del repair_dict[key]

        RepairActivityLog.objects.create(
            repair=repair,
            user = self.request.user,
            description = f'Użytkownik {self.request.user} utworzył naprawę. Dane: { {k: v for k, v in repair_dict.items()}}',
            type = 'Utworzenie naprawy',
            )
        if repair.workers.all():
                RepairActivityLog.objects.create(
                repair=repair,
                user = self.request.user,
                description = f"Przypisani: {', '.join([f'{worker.user.first_name} {worker.user.last_name} (ID: {worker.id})' for worker in repair.workers.all()])}",
                type = 'Edycja przypisania',
                )

        RepairActivityLog.objects.create(
            repair=repair,
            user = self.request.user,
            description = f'Ustawienie statusu na: {repair.status}',
            type = 'Ustawienie statusu',
        )



class RepairRetrieve(generics.RetrieveUpdateAPIView):


    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser|IsManager|IsWorker|IsClient]

    queryset = Repair.objects.all()
    serializer_class = RepairSerializer

    def get_object(self):
        if self.request.user.groups.first().name == 'client':

            user = self.request.user
            client = get_object_or_404(Client,user=user)

            repair_id = self.kwargs["pk"]
            repair = get_object_or_404(Repair,id=repair_id)

            if repair.car.owner == client:
                return repair 
            else:
                raise PermissionDenied('Brak dostępu')
        else:
            return super().get_object()
        
    def put(self, request, *args, **kwargs):
        if request.user.groups.first().name == 'client':
            raise PermissionDenied('Brak dostępu')
        else:
            return super().put(request, *args, **kwargs)
        
    
    def patch(self, request, *args, **kwargs):
        if request.user.groups.first().name == 'client':
            raise PermissionDenied('Brak dostępu')
        else:
            return super().partial_update(request, *args, **kwargs)
    
    # propably won't enable deleting repairs - it generates problems. 

    # def delete(self, request, *args, **kwargs):
    #     if request.user.groups.first().name == 'client':
    #         raise PermissionDenied('Brak dostępu')
    #     else:
    #         return super().destroy(request, *args, **kwargs)
        
    def perform_update(self, serializer):
        original_repair = self.get_object()
        original_repair_workers_copy = copy.copy(original_repair.workers.all())
        original_fields = copy.copy(original_repair.__dict__)

        repair = serializer.save()
        
        repair_dict = copy.copy(repair.__dict__)
        keys_to_delete = ['registration_date','start_date','end_date','car_id','_state']

        for key in keys_to_delete:
            del repair_dict[key]
            del original_fields[key]

        if original_fields['status'] != repair_dict['status']:
            RepairActivityLog.objects.create(
            repair=repair,
            user = self.request.user,
            description = f"Ustawienie statusu na: {repair_dict['status']}",
            type = 'Ustawienie statusu',
        )
            
        del original_fields['status']
        del repair_dict['status']
            
        if original_fields != repair_dict:
            RepairActivityLog.objects.create(
                repair=repair,
                user = self.request.user,
                description = f'Użytkownik {self.request.user} zedytował naprawę. Dane przed edycją: { {k: v for k, v in original_fields.items()}}. Nowe dane: { {k: v for k, v in repair_dict.items()} }',
                type = 'Edycja naprawy',
                )
            
        if list(original_repair_workers_copy) == list(repair.workers.all()): 
            pass
        else:
            
            RepairActivityLog.objects.create(
                repair=repair,
                user = self.request.user,
                description = f"Przypisani: {', '.join([f'{worker.user.first_name} {worker.user.last_name} (ID: {worker.id})' for worker in repair.workers.all()])}",
                type = 'Edycja przypisania',
                )
        

        

# repair comments

class CommentListCreate(generics.ListCreateAPIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser|IsManager|IsWorker|IsClient]

    queryset = RepairComment.objects.all()
    serializer_class = CommentSerializer


    # metoda get_queryset w klasie nadrzędnej zwraca zbiór obiektów w odpowiedzi do zapytania api
    def get_queryset(self):

        user = self.request.user
    
        repair_id = self.kwargs['pk']
        repair = Repair.objects.get(id=repair_id)

        if user.groups.first().name == 'client':
            client = Client.objects.get(user=user)

            if repair.car.owner == client:
                comments = RepairComment.objects.filter(repair=repair,visible_for_client=True)
                return comments
            else:
                raise PermissionDenied('Brak dostępu')
        else:
            comments = RepairComment.objects.filter(repair=repair)
            return comments
        
    def post(self,request, *args, **kwargs):
        if request.user.groups.first().name == 'client':
            raise PermissionDenied('Brak dostępu')
        else:
            return super().post(request, *args, **kwargs)
        
    def perform_create(self, serializer):
        repair_id = self.kwargs['pk']
        repair = Repair.objects.get(id=repair_id)

        comment = serializer.save(creator=self.request.user,repair=repair)

        if comment.visible_for_client:
            comment_type = 'Komentarz publiczny'
        else:
            comment_type = "Komentarz niepubliczny"

        RepairActivityLog.objects.create(
            repair=repair,
            user = self.request.user,
            description = f"Komentarz o ID {comment.id} o treści: '{comment.value}'",
            type = comment_type
        )



class CommentRetrieveDestroy(generics.RetrieveDestroyAPIView):


    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser|IsManager|IsWorker]

    queryset = RepairComment.objects.all()
    serializer_class = CommentSerializer

    # metoda get_object w klasie nadrzędnej zwraca obiekt w odpowiedzi do zapytania api
    def get_object(self):
        comment_id = self.kwargs['pk2']
        repair_id = self.kwargs['pk']
        repair = get_object_or_404(Repair,id=repair_id)
        
        comment = get_object_or_404(RepairComment,repair=repair,id=comment_id)
        
        return comment
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if self.request.user == instance.creator:
            self.perform_destroy(instance)
        else:
            raise PermissionDenied('Brak dostępu')
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def perform_destroy(self, instance):
        instance_id_copy = copy.copy(instance.id)
        super().perform_destroy(instance)
  
        repair_id = self.kwargs['pk']
        repair = Repair.objects.get(id=repair_id)

        RepairActivityLog.objects.create(
            repair=repair,
            user = self.request.user,
            description = f"Usunięcie komentarza o ID {instance_id_copy} o treści: '{instance.value}'",
            type = "Usunięcie komentarza"
        )
        



class WorklogListCreate(generics.ListCreateAPIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser|IsManager|IsWorker]

    queryset = WorkLog.objects.all()
    serializer_class = WorkLogSerializer

    def get_queryset(self):
        repair_id = self.kwargs['pk']
        repair = get_object_or_404(Repair,id=repair_id)
        worklogs = WorkLog.objects.filter(repair=repair)
        return worklogs

    def post(self,request, *args, **kwargs):
        if request.user.groups.first().name == 'staff':
            raise PermissionDenied('Brak dostępu')
        if request.user.groups.first().name == 'manager':
            raise PermissionDenied('Brak dostępu')
        else:
            return super().post(request, *args, **kwargs)
        
    def perform_create(self, serializer):
        repair_id = self.kwargs['pk']
        repair = get_object_or_404(Repair,id=repair_id)
        worker = get_object_or_404(Worker,user=self.request.user)
        worklog = serializer.save(worker=worker,repair=repair)

        RepairActivityLog.objects.create(
            repair=repair,
            user = self.request.user,
            description = f'Użytkownik zalogował czasu: {worklog.duration()} \n Opis:\n{worklog.comment}',
            type = 'Zalogowanie czasu',
        )


class ActivitylogList(generics.ListAPIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser|IsManager|IsWorker]

    queryset = RepairActivityLog.objects.all()
    serializer_class = RepairActivityLogSerializer

    def get_queryset(self):
        repair_id = self.kwargs['pk']
        repair = Repair.objects.get(id=repair_id)
        activitylogs = RepairActivityLog.objects.filter(repair=repair)
        return activitylogs



class ClientListCreate(generics.ListCreateAPIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser|IsManager|IsWorker]

    queryset = Client.objects.all()
    serializer_class = ClientSerializer


class ClientRetrieve(generics.RetrieveUpdateDestroyAPIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser|IsManager|IsWorker]

    queryset = Client.objects.all()
    serializer_class = ClientSerializer


    


# worker_api

class WorkerListCreate(generics.ListCreateAPIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser|IsManager]

    queryset = Worker.objects.all()
    serializer_class = WorkerSerializer

class WorkerRetrieve(generics.RetrieveUpdateDestroyAPIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser|IsManager]

    queryset = Worker.objects.all()
    serializer_class = WorkerSerializer

    

# manager_api


class ManagerListCreate(generics.ListCreateAPIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]

    queryset = Manager.objects.all()
    serializer_class = ManagerSerializer

class ManagerRetrieve(generics.RetrieveUpdateDestroyAPIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]

    queryset = Manager.objects.all()
    serializer_class = ManagerSerializer



# image _api

class ImageListCreate(generics.ListCreateAPIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser|IsManager|IsWorker]

    queryset = RepairImage.objects.all()
    serializer_class = RepairImageSerializer

    def get_queryset(self):
        repair_id = self.kwargs['pk']
        repair = Repair.objects.get(id=repair_id)
        images = RepairImage.objects.filter(repair=repair)
        return images
    

    def perform_create(self, serializer):
        repair_id = self.kwargs['pk']
        repair = get_object_or_404(Repair,id=repair_id)
        image = serializer.save(repair=repair,user=self.request.user)

        RepairActivityLog.objects.create(
            repair=repair,
            user = self.request.user,
            description = f'Użytkownik {self.request.user.first_name} {self.request.user.last_name} dodał zdjęcie ID: {image.id}',
            type = 'Dodanie zdjęcia',
            )

        


class ImageRetrieve(generics.RetrieveDestroyAPIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser|IsManager|IsWorker]

    queryset = RepairImage.objects.all()
    serializer_class = RepairImageSerializer

    def get_object(self):
        repair_id = self.kwargs['pk']
        image_id = self.kwargs['pk2']
        repair = get_object_or_404(Repair,id=repair_id)
        image = get_object_or_404(RepairImage,repair=repair,id=image_id)
        return image
    
    def perform_destroy(self, instance):
        
        if self.request.user == instance.user:
            super().perform_destroy(instance)

            repair_id = self.kwargs['pk']
            repair = get_object_or_404(Repair,id=repair_id)

            comment_id = self.kwargs['pk2']
            comment_id_copy = copy.copy(comment_id)


            RepairActivityLog.objects.create(
                repair=repair,
                user = self.request.user,
                description = f'Użytkownik {self.request.user.first_name} {self.request.user.last_name} usunął zdjęcie ID: {comment_id_copy}',
                type = 'Usunięcie zdjęcia',
                )
        else:
            raise PermissionDenied('Brak dostępu')

        



       

# function for tests
# def test(request):
#     send_mail('asdasd', 'asdasd', 'hreczix', ['hreczuch.lukasz@gmail.com'])
#     return render(request, 'test.html')

