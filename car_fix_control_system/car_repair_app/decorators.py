from django.http import HttpResponse
from django.shortcuts import redirect
from django.contrib.auth import logout

# decorator to restrict going to certaing views, when request user is logged in allready
def unauthenticated_user(view_func):
    def decorator(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('/')
        else:
            return view_func(request, *args, **kwargs)
        
    return decorator

def allowed_groups(allowed_groups=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            
            group=None
            if request.user.groups.exists():
                group = request.user.groups.all()[0].name

            if group in allowed_groups:
                return view_func(request,*args,**kwargs)
            else:
                return redirect('/logout')
        return wrapper_func
    return decorator
            