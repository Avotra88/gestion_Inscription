from django.contrib import admin
from django.urls import path
from inscriptions import views as inscriptions_views  # Import des vues du module inscriptions

urlpatterns = [
    path('admin/', admin.site.urls),  # Accès à l'interface d'administration Django

    # Connexion et déconnexion
    path('login/', inscriptions_views.login_view, name='login'),
    path('logout/', inscriptions_views.logout_view, name='logout'),

    # Page d'accueil
    path('', inscriptions_views.home, name='home'),

    # Tableau de bord
    path('dashboard/', inscriptions_views.dashboard, name='dashboard'),
    path('dashboard_admin/', inscriptions_views.dashboard_admin, name='dashboard_admin'),
    path('dashboard_user/', inscriptions_views.dashboard_user, name='dashboard_user'),

    # Gestion des inscriptions
    path('inscriptions/ajouter/', inscriptions_views.ajouter_inscription, name='ajouter_inscription'),
    path('inscriptions/modifier/<int:id>/', inscriptions_views.modifier_inscription, name='modifier_inscription'),
    path('inscriptions/supprimer/<int:id>/', inscriptions_views.delete_action, name='delete_action'),

    # Audit des inscriptions
    path('audit/inscription/<int:id>/', inscriptions_views.audit_action, name='audit_action'),
    path('audit/statistiques/', inscriptions_views.statistiques_inscriptions, name='statistiques_inscriptions'),

    # Gestion des utilisateurs (administration personnalisée)
    path('users/create/', inscriptions_views.create_user, name='create_user'),  # Correction ici
    path('users/modify/<int:user_id>/', inscriptions_views.modify_user, name='modify_user'),
    path('users/delete/<int:user_id>/', inscriptions_views.delete_user, name='delete_user'),
]
