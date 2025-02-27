from rest_framework.permissions import BasePermission

class IsWorker(BasePermission):

    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and request.user.groups.first().name == 'worker')

class IsManager(BasePermission):
    
    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and request.user.groups.first().name == 'manager')
    
class IsClient(BasePermission):
    
    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and request.user.groups.first().name == 'client')
    
    


    