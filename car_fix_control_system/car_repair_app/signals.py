from django.db.models.signals import post_save, m2m_changed, post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import User, Group
from .models import Worker, Client, Manager
from django.apps import apps
from django.contrib.contenttypes.models import ContentType


@receiver(post_save, sender=User)
def add_admin_to_group(instance,created, *args, **kwargs):
    if instance.groups.exists():
        return None
    
    if created and instance.is_superuser:
        group = Group.objects.get(name='admin')
        instance.groups.add(group)
        instance.save()

@receiver(post_save, sender=Worker)
def add_worker_to_group(instance,created, *args, **kwargs):
    if instance.user.groups.exists():
        return None
    
    if created:
        group = Group.objects.get(name='worker')
        instance.user.groups.add(group)
        instance.user.save()

@receiver(post_save, sender=Client)
def add_client_to_group(instance,created, *args, **kwargs):
    
    if instance.user.groups.exists():
        return None
    if created:
        group = Group.objects.get(name='client')
        instance.user.groups.add(group)
        instance.user.save()
        

@receiver(post_save, sender=Manager)
def add_manager_to_group(instance,created, *args, **kwargs):
    if instance.user.groups.exists():
        
        return None
    if created:
        group = Group.objects.get(name='manager')
        instance.user.first_name = instance.first_name
        instance.user.last_name = instance.last_name
        
        instance.user.groups.add(group)
        instance.user.save()
        


# Sygnał stworzony po to by tworzył się aktor systemu gdy od strony admina stworzymy usera z określoną grupą. WAŻNE - user musi mieć grupę, inaczej nic się nie wydarzy.
@receiver(m2m_changed, sender=User.groups.through)
def create_user_role_model(sender, instance, action, **kwargs):
    if not instance.is_superuser:
        if instance.groups.exists():

            if action == 'post_add':
                group = instance.groups.first()
                model_name = group.name[0].upper() + group.name[1:]

                Model = apps.get_model(app_label='car_repair_app', model_name=model_name)

                if not Model.objects.filter(user=instance).exists():
                    Model.objects.create(user=instance)

@receiver(post_migrate)
def create_groups(sender, **kwargs):
    groups = ['admin','manager','client','worker']
    for group in groups:
        if not Group.objects.filter(name=group).exists():
            Group.objects.get_or_create(name=group)