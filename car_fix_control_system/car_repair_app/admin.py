from django.contrib import admin
from .models import Client, Worker, Car, Repair, WorkLog, Manager, RepairComment,RepairActivityLog, RepairImage

# Register your models here.


admin.site.register(Client)
admin.site.register(Worker)
admin.site.register(Car)
admin.site.register(Repair)
admin.site.register(WorkLog)
admin.site.register(Manager)
admin.site.register(RepairComment)
admin.site.register(RepairActivityLog)

admin.site.register(RepairImage)
