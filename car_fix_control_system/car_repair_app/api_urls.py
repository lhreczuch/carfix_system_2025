from django.urls import path
from . import views
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [

    path('schema',SpectacularAPIView.as_view(),name='schema'),
    path('docs',SpectacularSwaggerView.as_view(url_name='schema')),
    path('token', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    # cars
    path('cars',views.CarsListCreate.as_view(),name='api_cars'),
    path('cars/<str:pk>',views.CarRetrieve.as_view(),name='api_car'),
    # repairs
    path('repairs',views.RepairListCreate.as_view(),name='api_repairs'),
    path('repairs/<str:pk>',views.RepairRetrieve.as_view(),name='api_repair'),
    # comments
    path('repairs/<str:pk>/comments',views.CommentListCreate.as_view(),name='api_comments'),
    path('repairs/<str:pk>/comments/<str:pk2>',views.CommentRetrieveDestroy.as_view(),name='api_comment'),
    # worklogs
    path('repairs/<str:pk>/worklogs',views.WorklogListCreate.as_view(),name='worklogs'),
    # activitylog
    path('repairs/<str:pk>/activitylogs',views.ActivitylogList.as_view(),name='activitylogs'),
    #clients
    path('clients',views.ClientListCreate.as_view(),name='api_clients'),
    path('clients/<str:pk>',views.ClientRetrieve.as_view(),name='api_client'),
    #workers
    path('workers',views.WorkerListCreate.as_view(),name='api_workers'),
    path('workers/<str:pk>',views.WorkerRetrieve.as_view(),name='api_worker'),
    #managers
    path('managers',views.ManagerListCreate.as_view(),name='api_managers'),
    # path('managers/<str:pk>',views.ManagerRetrieve.as_view(),name='api_managers'),
    
    # images
    path('repairs/<str:pk>/images',views.ImageListCreate.as_view(),name='api_images'),
    path('repairs/<str:pk>/images/<str:pk2>',views.ImageRetrieve.as_view(),name='api_image'),
]