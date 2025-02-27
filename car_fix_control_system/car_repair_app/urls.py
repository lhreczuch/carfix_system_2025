from django.urls import path,include
from . import views

urlpatterns = [

    # nocategory
    # path('test',views.test,name='test'),
    path('',views.main,name='main'),
    path('login/',views.login,name='login'),
    path('logout/',views.logout_view,name='logout'),
    path('password-edit',views.password_edit,name='password-edit'),


    # car
    path('cars/<str:pk>',views.car,name='car'),
    path('cars/<str:pk>/delete',views.car_delete,name='car-delete'),
    path('cars/<str:pk>/edit',views.car_edit,name='car-edit'),
    path('cars',views.cars,name='cars'),
    path('add-car',views.add_car,name='add-car'),
    path('cars/<str:pk>/add-repair',views.add_repair,name='specific-car-add-repair'),

    # repair
    path('repairs/<str:pk>',views.repair_panel,name='repair-panel'),

    # propably won't enable deleting repairs - it generates problems. 
    # path('repairs/<str:pk>/delete',views.repair_delete,name='repair-delete'),
    path('add-repair',views.add_repair,name='add-repair'),
    path('repairs',views.all_repairs,name='all-repairs'),
    path('repairs/<str:pk>/change-status',views.change_repair_status,name='change-repair-status'),
    path('repairs/<str:pk>/workers_update',views.update_repair_workers,name='update-repair-workers'),
    path('repairs/<str:pk>/log_work',views.log_work,name='log-work'),
    path('repairs/<str:pk>/add-comment',views.add_comment,name='add-comment'),
    path('repairs/<str:pk>/add-image',views.repair_add_image,name='add_image'),
    path('repairs/<str:pk>/image/<str:pk2>/delete',views.image_delete,name='image-delete'),
    path('repairs/<str:pk>/image/<str:pk2>',views.image,name='image'),
    path('repairs/<str:pk>/comments/<str:pk2>/delete',views.comment_delete,name='comment-delete'),
    path('repairs/<str:pk>/csv',views.repair_csv,name='repair-raport-csv'),
    path('repairs/<str:pk>/pdf',views.report_pdf,name='repair-raport-pdf'),
    path('repairs/<str:pk>/edit',views.repair_edit,name='repair-edit'),

    # client
    path('client-panel',views.client_panel,name='client-panel'),
    path('add-client',views.add_client,name='add-client'),
    path('clients',views.clients,name='clients'),
    path('clients/<str:pk>',views.client_view,name='client'),
    path('clients/<str:pk>/edit',views.client_edit_view,name='client-edit'),
    path('clients/<str:pk>/delete',views.client_delete,name='client-delete'),
    path('clients/<str:pk>/add-car',views.specific_client_add_car,name='specific-client-add-car'),

    # manager
    path('manager-panel',views.manager_panel,name='manager-panel'),
    
    # worker
    path('worker-panel',views.worker_panel,name='worker-panel'),
    path('workers',views.workers,name='workers'),
    path('workers/<str:pk>',views.worker_view,name='worker'),
    path('workers/<str:pk>/edit',views.worker_edit_view,name='worker-edit'),
    path('workers/<str:pk>/delete',views.worker_delete,name='worker-delete'),
    path('add-worker',views.add_worker,name='add-worker'),
    



]