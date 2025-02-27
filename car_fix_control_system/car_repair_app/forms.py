from django import forms 
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ModelForm
from .models import Repair, Car, Client, Worker, WorkLog, RepairComment, RepairImage

class UserEditForm(ModelForm):
    class Meta:
        model = User
        fields = ['email','first_name','last_name']

        labels = {"email": 'Adres email', "first_name": 'Imię',"last_name": "Nazwisko"}

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class RepairForm(ModelForm):
    class Meta:
        model = Repair
        fields = ["name","car","description","workers"]

        widgets = {
            'workers': forms.CheckboxSelectMultiple,
            
        }

    # Przy inicjalizacji formularza usuwamy pole workers jesli dodający naprawę nie jest managerem
    def __init__(self, *args, **kwargs):
        
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs) 

        if self.user and not self.user.groups.filter(name='manager').exists():
            self.fields.pop('workers')

class RepairSearchForm(forms.Form):
    cars= Car.objects.all()
    workers = Worker.objects.all()

    choices={'':'-----','Oczekująca':'Oczekująca','W trakcie':'W trakcie', "Wykonana":'Wykonana'}

    name = forms.CharField(max_length=50,required=False)
    car = forms.ModelChoiceField(cars,required=False)
    description = forms.CharField(max_length=1000,required=False)
    workers = forms.ModelChoiceField(workers,widget=forms.Select,required=False) # docelowo to pole powinno byc multichoice field
    registration_date = forms.DateTimeField(required=False,widget=forms.TextInput(attrs={'type':'datetime-local'}))
    start_date = forms.DateTimeField(required=False,widget=forms.TextInput(attrs={'type':'datetime-local'}))
    end_date = forms.DateTimeField(required=False,widget=forms.TextInput(attrs={'type':'datetime-local'}))
    status = forms.ChoiceField(choices=choices,required=False)



class RepairEditForm(ModelForm):
    class Meta:
        model = Repair
        fields = ['name','description']
                    
# form to edit repair workers (for manager use)
class RepairFormWorkersUpdator(ModelForm):
    class Meta:
        model = Repair
        fields = ["workers"]
        widgets = {
            'workers': forms.CheckboxSelectMultiple,
            
        }


class CarForm(ModelForm):
    class Meta:
        model = Car
        fields = ["owner","vin_number","production_date","producer","model","version","generation","horsepowers","color","displacement_in_litres","mileage"]

        labels = {
            "owner": "Właściciel",
            "vin_number": "Numer VIN",
            "production_date": "Data produkcji",
            "producer": "Producent",
            "model": "Model",
            "version": "Wersja",
            "generation": "Generacja",
            "horsepowers": "Konie mechaniczne",
            "color": "Kolor",
            "displacement_in_litres": "Pojemność silnika",
            "mileage": "Przebieg (km)"
        }

        widgets = {
            'production_date':forms.TextInput(attrs={'type':'date'})
        }

class SpecificClientCarForm(ModelForm):
    class Meta:
        model = Car
        fields = ["vin_number","production_date","producer","model","version","generation","horsepowers","color","displacement_in_litres","mileage"]

        widgets = {
            'production_date':forms.TextInput(attrs={'type':'date'})
        }
class CarEditForm(ModelForm):
    class Meta:
        model = Car
        fields = '__all__'
        exclude = ['registration_date']

        widgets = {
            'production_date':forms.TextInput(attrs={'type':'date'})
        }


class CarSearchForm(forms.ModelForm):
     
     class Meta:
        model = Car
        fields = ["owner","vin_number","production_date","producer","model","version","horsepowers","color"]

        widgets = {
            'production_date':forms.TextInput(attrs={'type':'date'})
        }

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields['owner'].required = False
        


class ClientForm(ModelForm):
    
    class Meta:
        model = Client
        fields = ["company_name","company_id","postal_code","city","street","street_number"]

        
        labels = {
            "company_name": 'Nazwa firmy',"company_id": 'NIP',"postal_code":'Kod pocztowy',"city":'Miasto',"street":'Ulica',"street_number":'Numer ulicy'
        }



class ClientEditForm(ModelForm):

    class Meta:
        model = Client
        fields = ["company_name","company_id","postal_code","city","street","street_number"]


class ClientSearchForm(forms.Form):
     
     company_name = forms.CharField(max_length=100,required=False)
     company_id = forms.CharField(max_length=100,required=False)
     postal_code = forms.CharField(max_length=100,required=False)
     city = forms.CharField(max_length=100,required=False)
     street = forms.CharField(max_length=100,required=False)
     street_number = forms.CharField(max_length=15,required=False)
     registration_date = forms.DateTimeField(required=False,widget=forms.TextInput(attrs={'type':'date'}))

class SpecificCarRepairForm(ModelForm):
    class Meta:
        model = Repair
        fields = ["name","description","workers"]
        widgets = {
            'workers': forms.CheckboxSelectMultiple,
            
        }

    def __init__(self, *args, **kwargs):
        
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs) 

        if self.user and not self.user.groups.filter(name='manager').exists():
            self.fields.pop('workers')

class WorkLogForm(ModelForm):
    class Meta:
        model = WorkLog
        fields = ['start_date','end_date','comment']

        widgets = {
            'start_date':forms.TextInput(attrs={'type':'datetime-local'}),
            'end_date':forms.TextInput(attrs={'type':'datetime-local'}),
        }

class RepairCommentForm(ModelForm):
    class Meta:
        model = RepairComment
        fields = ['value','visible_for_client']

        labels = {'value':'Wartość','visible_for_client':'Widoczny dla klienta'}
        


class RepairStatusForm(forms.Form):
    OPTIONS = [
        ('Oczekująca', 'Oczekująca'),
        ('W trakcie', 'W trakcie'),
        ('Wykonana', 'Wykonana'),
    ]
    select_field = forms.ChoiceField(choices=OPTIONS, label='Wybierz status')

class RepairImageForm(ModelForm):
    class Meta:
        model = RepairImage
        fields = ['image','description']

        labels = {'image':'Zdjęcie','description':'opis'}

