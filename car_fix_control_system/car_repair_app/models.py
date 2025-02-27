from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
import random
import string
from django.core.mail import send_mail



class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client')
    company_name = models.CharField(max_length=100,blank=True,null=True)
    company_id = models.CharField(max_length=15,blank=True,null=True)
    postal_code = models.CharField(max_length=6,blank=True,null=True)
    city = models.CharField(max_length=50,blank=True,null=True)
    street = models.CharField(max_length=50,blank=True,null=True)
    street_number = models.CharField(max_length=10,blank=True,null=True)
    registration_date = models.DateTimeField(auto_now_add=True,editable=False)
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"
    
    def save(self,*args,**kwargs):
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        
        self.user.set_password(password)
        self.user.username = self.user.email

        # send_mail(
        #         'Twoje konto klienta!',
        #           f'Witamy,\n\nPoniżej przekazujemy dane dostępowe do panelu klienta w CarFix: \n\nLOGIN: {self.user.email}\nHASŁO: {password}',
        #             'CarFix', [self.user.email]
        #     )
        
        super().save(*args,**kwargs)
        

class Worker(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name='worker')

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"
    

    def save(self,*args,**kwargs):
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        
        print(password)
            
        # send_mail(
        #     'Twoje konto pracownika!',
        #         f'Witamy,\n\nPoniżej twoje dane do panelu pracowniczego w CarFix: \n\nLOGIN: {self.user.email}\nHASŁO: {password}',
        #             'CarFix', [self.user.email]
        #     )
        self.user.set_password(password)
        super().save(*args,**kwargs)

class Manager(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name='manager')

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

class Car(models.Model):
    owner = models.ForeignKey(Client, on_delete=models.CASCADE, blank=True, null=True)
    vin_number = models.CharField(max_length=17,blank=True,null=True)
    production_date = models.DateField(blank=True,null=True)
    producer = models.CharField(max_length=40,blank=True,null=True)
    model = models.CharField(max_length=30,blank=True,null=True)
    version = models.CharField(max_length=30,blank=True,null=True)
    generation = models.CharField(max_length=30,blank=True,null=True)
    horsepowers = models.CharField(max_length=15,blank=True,null=True)
    color = models.CharField(max_length=30,blank=True,null=True)
    registration_date = models.DateTimeField(auto_now_add=True,blank=True,null=True,editable=False)
    displacement_in_litres = models.CharField(max_length=5,blank=True,null=True)
    mileage = models.CharField(max_length=10,blank=True,null=True)

    def __str__(self):
        return f"{self.producer} {self.model} ID: {self.id}"

class Repair(models.Model):

    STATUS_CHOICES = [
        ('Oczekująca', 'Oczekująca'),
        ('W trakcie', 'W trakcie'),
        ('Wykonana', 'Wykonana'),
    ]

    name = models.CharField(max_length=50,blank=True,null=True)
    car = models.ForeignKey(Car, on_delete=models.CASCADE, blank=True, null=True)
    description = models.TextField(blank=True,null=True)
    workers = models.ManyToManyField(Worker,symmetrical=False,blank=True) 
    registration_date = models.DateTimeField(auto_now_add=True,editable=False)
    start_date = models.DateTimeField(blank=True,null=True)
    end_date = models.DateTimeField(blank=True,null=True)
    status = models.CharField(max_length=10,choices=STATUS_CHOICES,blank=True,null=True)

    def save(self, *args, **kwargs):
        if self.status == 'Wykonana' and not self.end_date:
            self.end_date = timezone.now()

            # send_mail(
            #     'Twoje auto jest gotowe do odbioru!',
            #       f'Naprawa ID {self.id} dotycząca samochodu {self.car} została ukończona. \n\n Zapraszamy po odbiór samochodu.',
            #         'CarFix', [self.car.owner.user.email]
            # )

        elif self.status == 'W trakcie':
            self.start_date = timezone.now()
            self.end_date = None

        if self.status == None:
            self.status = "Oczekująca"

        super().save(*args, **kwargs)
        

    def __str__(self):
        return f"{self.name}"

class RepairComment(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    visible_for_client = models.BooleanField(default=False)
    repair = models.ForeignKey(Repair, on_delete=models.CASCADE)
    creation_date = models.DateTimeField(auto_now_add=True,editable=False)
    value = models.TextField()

    


class WorkLog(models.Model):
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE)
    repair = models.ForeignKey(Repair, on_delete=models.CASCADE)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    comment = models.TextField(blank=True, null=True)

    def duration(self):
        return self.end_date - self.start_date
    
    def __str__(self):
        return f"{self.worker} | Ilość czasu: {self.duration()}"
    
class RepairActivityLog(models.Model):
    time = models.DateTimeField(auto_now_add=True,editable=False)
    repair = models.ForeignKey(Repair, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField()
    type = models.CharField(max_length=13)
    
class RepairImage(models.Model):
    repair = models.ForeignKey(Repair, on_delete=models.CASCADE)
    image = models.ImageField(null=True,blank=True,upload_to='images/')
    description = models.CharField(max_length=100)
    creation_date = models.DateTimeField(auto_now_add=True,editable=False)
    user = models.ForeignKey(User,models.CASCADE,
        blank=True,
        null=True,)
    
    
    
    


