from django.db.models.signals import post_save, m2m_changed, post_migrate, pre_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User, Group
from .models import Worker, Client, Manager, Repair, RepairActivityLog, RepairComment, WorkLog, RepairImage
from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from crum import get_current_user
import copy


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



# Activity logs:




@receiver(post_save, sender=Repair)
def log_repair_creation(sender, instance, created, **kwargs):
    user = get_current_user()
    if not user or not created:
        return

    # Skopiuj dane obiektu
    repair_dict = copy.copy(instance.__dict__)
    keys_to_delete = ['registration_date', 'start_date', 'end_date', 'car_id']
    for key in keys_to_delete:
        repair_dict.pop(key, None)

    RepairActivityLog.objects.create(
        repair=instance,
        user=user,
        description=f'Użytkownik {user} utworzył naprawę. Dane: '
                    f'[{ {k: v for k, v in repair_dict.items() if k != "_state"} }]',
        type='Utworzenie naprawy',
    )

@receiver(m2m_changed, sender=Repair.workers.through)
def log_worker_assignment(sender, instance, action, **kwargs):
    user = get_current_user()
    if action in ['post_add', 'post_remove', 'post_clear'] and user:
        current_workers = instance.workers.all()

        if current_workers.exists():
            description = f"Ustawienie przypisanych do naprawy na: [{', '.join([f'{w.user.first_name} {w.user.last_name} (ID: {w.id})' for w in current_workers])}]"
        else:
            description = f"Ustawienie przypisanych do naprawy na: brak"

        RepairActivityLog.objects.create(
            repair=instance,
            user=user,
            description=description,
            type='Edycja przypisania',
        )


@receiver(pre_save, sender=Repair)
def log_repair_edit(sender, instance, **kwargs):
    user = get_current_user()

    if not instance.pk or not user:
        # nowy obiekt lub brak użytkownika (np. systemowe wywołanie) — pomijamy
        return

    try:
        previous = Repair.objects.get(pk=instance.pk)
    except Repair.DoesNotExist:
        return

    changes = {}
    status_changes = {}
    monitored_fields = ['name', 'description']  # lub wszystkie jeśli chcesz

    for field in monitored_fields:
        old = getattr(previous, field)
        new = getattr(instance, field)
        if old != new:
            changes[field] = {'before': old, 'after': new}

    old_status = getattr(previous,'status')
    new_status = getattr(instance,'status')

    if old_status != new_status:
        status_changes = {'before': old_status, 'after': new_status}

    if changes:
        RepairActivityLog.objects.create(
            repair=instance,
            user=user,
            description=f'Edycja naprawy: [{changes}]',
            type='Edycja naprawy',
        )

    if status_changes:
        RepairActivityLog.objects.create(
            repair=instance,
            user = user,
            description = f'Ustawienie statusu naprawy na: {status_changes}',
            type = 'Zmiana statusu',
        )



@receiver(post_save, sender=RepairComment)
def log_comment_creation(sender, instance, created, **kwargs):
    user = get_current_user()
    if not user or not created:
        return
    
    if instance.visible_for_client:
        comment_type = 'Komentarz publiczny'
    else:
        comment_type = "Komentarz niepubliczny"

    RepairActivityLog.objects.create(
        repair=instance.repair,
        user = user,
        description = f"Dodanie komentarza ID {instance.id} o treści: '{instance.value}'",
        type = comment_type
        )
    

@receiver(post_delete, sender=RepairComment)
def log_comment_delete(sender, instance, **kwargs):
    instance_id_copy = copy.copy(instance.id)
    user = get_current_user()
    if not user or not instance:
        return
    

    RepairActivityLog.objects.create(
            repair=instance.repair,
            user = user,
            description = f"Usunięcie komentarza o ID {instance_id_copy} o treści: '{instance.value}'",
            type = "Usunięcie komentarza"
        )
    

@receiver(post_save, sender=WorkLog)
def log_worklog_creation(sender, instance, created, **kwargs):
    user = get_current_user()
    if not user or not instance:
        return
    

    RepairActivityLog.objects.create(
            repair=instance.repair,
            user = user,
            description = f'Zalogowanie czasu {instance.duration()} \n Opis:\n{instance.comment}',
            type = 'Zalogowanie czasu',
        )

@receiver(post_save, sender=RepairImage)
def log_image_creation(sender, instance, created, **kwargs):
    user = get_current_user()
    if not user or not instance:
        return
    

    RepairActivityLog.objects.create(
        repair=instance.repair,
        user = user,
        description = f'Dodanie zdjęcia ID: {instance.id}',
        type = 'Dodanie zdjęcia',
        )

@receiver(post_delete, sender=RepairImage)
def log_image_delete(sender, instance, **kwargs):
    instance_id_copy = copy.copy(instance.id)
    user = get_current_user()
    if not user or not instance:
        return
    

    RepairActivityLog.objects.create(
        repair=instance.repair,
        user = user,
        description = f'Usunięcie zdjęcia ID: {instance_id_copy}',
        type = 'Usunięcie zdjęcia',
        )





