# gestion_inscriptions/urls.py
from django.contrib import admin
from django.urls import path
from inscriptions import views  # Importer views, cela inclut logout_view
from inscriptions.views import logout_view  # Ajouter cet import pour logout_view

urlpatterns = [
    # Administration
    path('admin/', admin.site.urls),

    # Authentification
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Pages principales
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),

    

    path('ajouter_inscription/', views.ajouter_inscription, name='ajouter_inscription'),
    path('audit_inscription/<int:pk>/', views.AuditInscription, name='audit_inscription'),
    path('delete/<int:id>/', views.delete_action, name='delete_action'),
    path('audit/<int:id>/', views.audit_action, name='audit_action'),
    path('modifier_inscription/<int:id>/', views.modifier_inscription, name='modifier_inscription'),
    path('statistiques_inscriptions/', views.statistiques_inscriptions, name='statistiques_inscriptions'),
   
]  