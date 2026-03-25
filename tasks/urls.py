from django.urls import path

from . import views

app_name = 'tasks'

urlpatterns = [
    path('', views.TaskListView.as_view(), name='list'),
    path('create/', views.TaskCreateView.as_view(), name='create'),
    path('<int:pk>/edit/', views.TaskUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.TaskDeleteView.as_view(), name='delete'),
    path('<int:pk>/toggle/', views.TaskToggleDoneView.as_view(), name='toggle_done'),
    path('users/', views.UserManageListView.as_view(), name='user_manage'),
    path('users/<int:pk>/toggle-admin/', views.UserToggleAdminView.as_view(), name='toggle_admin'),
]
