from django.contrib.auth.forms import AuthenticationForm 
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect, get_object_or_404
from inscriptions.models import Inscription, AuditInscription
from django.contrib.auth.decorators import login_required
import logging
from django.contrib import messages
from inscriptions.models import Audit  
from .forms import InscriptionForm, AuditForm,  AuditActionForm 
from .models import StatistiqueInscription, Inscription, AuditInscription, AuditAction  # Ajoutez StatistiqueInscription ici


# Configuration du logger
logger = logging.getLogger(__name__)

# Vue de la page d'accueil
def home(request):
    return redirect('login')

# Vue pour le tableau de bord
@login_required
def dashboard(request):
    inscriptions = Inscription.objects.all()
    audits = AuditInscription.objects.all()
    stats = {
        'ajouts': audits.filter(type_action='ajout').count(),
        'modifications': audits.filter(type_action='modification').count(),
        'suppressions': audits.filter(type_action='suppression').count(),
    }
    return render(request, 'dashboard.html', {'inscriptions': inscriptions, 'audits': audits, 'stats': stats})

# Vue pour ajouter une inscription
@login_required
def ajouter_inscription(request):
    if request.method == 'POST':
        matricule = request.POST.get('matricule', '').strip()
        nom = request.POST.get('nom', '').strip()
        prenom = request.POST.get('prenom', '').strip()
        date_naissance = request.POST.get('date_naissance', '').strip()
        adresse = request.POST.get('adresse', '').strip()
        droit_inscription = request.POST.get('droit_inscription') == "on"

        if not (matricule and nom and prenom and date_naissance and adresse):
            messages.error(request, "Tous les champs sont obligatoires.")
            return render(request, 'ajouter_inscription.html')

        Inscription.objects.create(
            matricule=matricule,
            nom=nom,
            prenom=prenom,
            date_naissance=date_naissance,
            adresse=adresse,
            droit_inscription=droit_inscription
        )
        messages.success(request, "Inscription ajoutée avec succès.")
        return redirect('dashboard')
    
    return render(request, 'ajouter_inscription.html')

# Vue de la connexion (login)
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            logger.info(f"Connexion réussie pour {user.username}.")
            messages.success(request, "Connexion réussie !")
            return redirect('dashboard')
        else:
            logger.warning("Échec de la connexion, formulaire invalide.")
            messages.error(request, "Identifiants invalides.")
    
    form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

# Vue de la déconnexion
@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "Vous avez été déconnecté.")
    return redirect('login')

# Vue d'audit d'une inscription spécifique
@login_required
def audit_inscription(request, pk):
    inscription = get_object_or_404(Inscription, id=pk)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'ajouter':
            AuditInscription.objects.create(
                inscription=inscription,
                matricule=inscription.matricule,
                nom=inscription.nom,
                prenom=inscription.prenom,
                date_naissance=inscription.date_naissance,
                adresse=inscription.adresse,
                droit_inscription=inscription.droit_inscription,
                type_action='ajout',
                utilisateur=request.user.username
            )
            messages.success(request, "Audit d'ajout enregistré.")

        elif action == 'modifier':
            AuditInscription.objects.create(
                inscription=inscription,
                matricule=inscription.matricule,
                nom=inscription.nom,
                prenom=inscription.prenom,
                date_naissance=inscription.date_naissance,
                adresse=inscription.adresse,
                droit_inscription=inscription.droit_inscription,
                type_action='modification',
                utilisateur=request.user.username
            )
            messages.success(request, "Audit de modification enregistré.")

        elif action == 'supprimer':
            AuditInscription.objects.create(
                inscription=inscription,
                matricule=inscription.matricule,
                nom=inscription.nom,
                prenom=inscription.prenom,
                date_naissance=inscription.date_naissance,
                adresse=inscription.adresse,
                droit_inscription=inscription.droit_inscription,
                type_action='suppression',
                utilisateur=request.user.username
            )
            inscription.delete()
            messages.success(request, "Inscription supprimée avec succès.")
            return redirect('dashboard')

    return render(request, 'audit_inscription_detail.html', {'inscription': inscription})

# Vue pour modifier une inscription
@login_required
def modifier_inscription(request, id):
    inscription = get_object_or_404(Inscription, pk=id)
    if request.method == 'POST':
        form = InscriptionForm(request.POST, instance=inscription)
        if form.is_valid():
            form.save()
            messages.success(request, 'Les modifications ont été sauvegardées avec succès.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Il y a eu une erreur lors de la sauvegarde.')
    else:
        form = InscriptionForm(instance=inscription)
    return render(request, 'modifier_inscription.html', {'form': form})

# Vue pour auditer une action sur une inscription
@login_required
def audit_action(request, id):
    inscription = get_object_or_404(Inscription, id=id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'modifier':
            inscription.nom = request.POST.get('nom', inscription.nom)
            inscription.prenom = request.POST.get('prenom', inscription.prenom)
            inscription.date_naissance = request.POST.get('date_naissance', inscription.date_naissance)
            inscription.adresse = request.POST.get('adresse', inscription.adresse)
            inscription.droit_inscription = request.POST.get('droit_inscription') == "on"
            inscription.save()
            AuditInscription.objects.create(
                inscription=inscription,
                matricule=inscription.matricule,
                nom=inscription.nom,
                prenom=inscription.prenom,
                date_naissance=inscription.date_naissance,
                adresse=inscription.adresse,
                droit_inscription=inscription.droit_inscription,
                type_action='modification',
                utilisateur=request.user.username
            )
            messages.success(request, "Inscription modifiée avec succès.")
        elif action == 'supprimer':
            inscription.delete()
            AuditInscription.objects.create(
                inscription=inscription,
                matricule=inscription.matricule,
                nom=inscription.nom,
                prenom=inscription.prenom,
                date_naissance=inscription.date_naissance,
                adresse=inscription.adresse,
                droit_inscription=inscription.droit_inscription,
                type_action='suppression',
                utilisateur=request.user.username
            )
            messages.success(request, "Inscription supprimée avec succès.")
        
    return redirect('dashboard')


def delete_action(request, id):
    # Récupérez l'objet à supprimer
    item = get_object_or_404(Inscription, id=id)  # Remplacez 'Inscription' par le nom de votre modèle si nécessaire
    
    # Supprimez l'objet
    item.delete()
    
    # Redirigez vers une autre page après la suppression
    return redirect('index')  # Remplacez 'some_view_name' par le nom de la vue vers laquelle vous voulez rediriger

# Vue pour la modification
def modifier_action(request, id):
    action = get_object_or_404(AuditAction, id=id)
    if request.method == 'POST':
        form = AuditActionForm(request.POST, instance=action)
        if form.is_valid():
            form.save()
            return redirect('statistiques')  # Redirige vers la vue des statistiques
    else:
        form = AuditActionForm(instance=action)
    return render(request, 'modifier_action.html', {'form': form})

@login_required
def statistiques_inscriptions(request):
    statistiques = StatistiqueInscription.objects.all()

    # Vous pouvez ajouter des filtres ici si nécessaire, comme par date ou par type d'action
    return render(request, 'inscriptions/statistiques_inscriptions.html', {'statistiques': statistiques})


def enregistrer_statistique(request):
    if request.method == 'POST':
        # Exemple d'ajout d'une nouvelle statistique
        statistique = StatistiqueInscription.objects.create(
            action_type='ajout',  # L'action peut être 'ajout', 'modification' ou 'suppression'
            inscription_id=request.POST.get('inscription_id'),
            timestamp=request.POST.get('timestamp')
        )
        statistique.save()
        return redirect('statistique_view')  # Rediriger après l'enregistrement

    return render(request, 'enregistrer_statistique.html')