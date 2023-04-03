from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('register', views.register, name='register'),
    path('add/<str:pk>', views.add, name='add'),
    path('edit/<str:pk>', views.edit, name='edit'),
    path('delete/<str:pk>', views.delete, name='delete'),
    path('add/<str:pk>/dodaj', views.dodaj, name='dodaj'),
    path('add/<str:pk>/dodaj/confirm', views.confirm, name='confirm'),
    path('statystyki/<str:pk>', views.statystyki, name='statystyki'),
    ]