from django.contrib import admin
from django.urls import path

from task_manager import views

urlpatterns = [
    path('', views.index, name='index'),
    path('users/create/', views.registration_user, name='registration_user'),
    path('login/', views.login_user, name='login'),
    path('users/', views.users, name='users'),
    path('logout/', views.logout, name='logout'),
    path('users/<int:pk>/update/', views.update_user, name='update'),
    path('users/<int:pk>/delete/', views.delete_user, name='delete'),
    path('statuses/', views.status, name='statuses'),
    path('statuses/create/', views.status_create, name='status_create'),
    path('statuses/<int:pk>/update/', views.update_status,
         name='status_update'),
    path('statuses/<int:pk>/delete/', views.delete_status,
         name='status_delete'),
    path('labels/', views.label,
         name='labels'),
    path('labels/create/', views.create_label, name='create_label'),
    path('labels/<int:pk>/update/', views.update_label, name='label_update'),
    path('labels/<int:pk>/delete/', views.delete_label, name='label_delete'),
    path('tasks/create', views.create_task, name='task_create'),
    path('tasks/', views.tasks_list, name='tasks'),
    path('tasks/<int:pk>/delete/', views.delete_task, name='task_delete'),
    path('tasks/<int:pk>/', views.task_detail, name='task_detail'),
    path('tasks/<int:pk>/update/', views.task_update, name='task_update'),
    path('admin', admin.site.urls),
    path('test-rollbar/', views.test_rollbar, name='test_rollbar'),
]
