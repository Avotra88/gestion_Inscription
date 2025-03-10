from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect, get_object_or_404
from inscriptions.models import Inscription, AuditInscription
from django.contrib.auth.decorators import login_required
import logging
from django.contrib import messages
from .forms import InscriptionForm
from .models import StatistiqueInscription


# Configuration du logger
logger = logging.getLogger(__name__)

# Vue de la page d'accueil
def home(request):
    return redirect('login')

@login_required
def dashboard(request):
    inscriptions = Inscription.objects.all()
    audits = AuditInscription.objects.all()  # Récupérer toutes les entrées d'audit
    
    # Calcul des statistiques basées sur les actions dans les audits
    ajouts = audits.filter(type_action='ajout').count()
    modifications = audits.filter(type_action='Modification').count()
    suppressions = audits.filter(type_action='Suppression').count()

    print(f"Ajouts: {ajouts}, Modifications: {modifications}, Suppressions: {suppressions}")

    stats = {
        'ajouts': ajouts,
        'modifications': modifications,
        'suppressions': suppressions,
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

        # Création de l'inscription avec l'utilisateur connecté
        inscription = Inscription.objects.create(
            matricule=matricule,
            nom=nom,
            prenom=prenom,
            date_naissance=date_naissance,
            adresse=adresse,
            droit_inscription=droit_inscription,
            utilisateur=request.user  # Ajout de l'utilisateur connecté
        )

        # Enregistrement de l'audit pour l'ajout
        create_audit(inscription, 'ajout', request)

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
            create_audit(inscription, 'modification', request)
            messages.success(request, "Inscription modifiée avec succès.")
        elif action == 'supprimer':
            create_audit(inscription, 'suppression', request)
            inscription.delete()
            messages.success(request, "Inscription supprimée avec succès.")
        
    return redirect('dashboard')

def create_audit(inscription, action, request):
    # Vérifier si l'utilisateur est connecté
    utilisateur = request.user if request.user.is_authenticated else None

    # Si l'utilisateur n'est pas authentifié, vous pouvez soit le définir par défaut, soit lever une exception
    if utilisateur is None:
        # Par exemple, si vous souhaitez laisser un utilisateur par défaut (par exemple, un admin ou autre)
        utilisateur = 'Utilisateur Anonyme'  # Ou une instance d'utilisateur par défaut

    # Assigner les anciens et nouveaux droits d'inscription
    droit_ancien = inscription.droit_inscription  # Assurez-vous que ce champ existe dans votre modèle
    droit_nouveau = inscription.droit_inscription  # Ajoutez la logique pour mettre à jour le droit si nécessaire

    # Créer un audit
    AuditInscription.objects.create(
        inscription=inscription,
        matricule=inscription.matricule,
        nom=inscription.nom,
        prenom=inscription.prenom,
        date_naissance=inscription.date_naissance,
        adresse=inscription.adresse,
        droit_ancien=droit_ancien,  # Avant modification
        droit_nouveau=droit_nouveau,  # Après modification
        type_action=action,
        utilisateur=utilisateur  # Assurez-vous que l'utilisateur est renseigné
    )



# Vue pour afficher les statistiques des inscriptions
@login_required
def statistiques_inscriptions(request):
    statistiques = StatistiqueInscription.objects.all().order_by('-timestamp')
    return render(request, 'inscriptions/statistiques_inscriptions.html', {'statistiques': statistiques})

# Vue pour modifier une inscription
@login_required
def modifier_inscription(request, id):
    inscription = get_object_or_404(Inscription, id=id)
    # Vérifier si l'utilisateur est connecté
    utilisateur = request.user if request.user.is_authenticated else None

    # Si l'utilisateur n'est pas authentifié, vous pouvez soit le définir par défaut, soit lever une exception
    if utilisateur is None:
        # Par exemple, si vous souhaitez laisser un utilisateur par défaut (par exemple, un admin ou autre)
        utilisateur = 'Utilisateur Anonyme'  # Ou une instance d'utilisateur par défaut

    if request.method == 'POST':
        form = InscriptionForm(request.POST, instance=inscription)
        if form.is_valid():
            

            # Assigner les anciens et nouveaux droits d'inscription
            droit_ancien = inscription.droit_inscription  # Assurez-vous que ce champ existe dans votre modèle
            droit_nouveau = inscription.droit_inscription  # Ajoutez la logique pour mettre à jour le droit si nécessaire

            # Créer un audit
            AuditInscription.objects.create(
                inscription=inscription,
                matricule=inscription.matricule,
                nom=inscription.nom,
                prenom=inscription.prenom,
                date_naissance=inscription.date_naissance,
                adresse=inscription.adresse,
                droit_ancien=droit_ancien,  # Avant modification
                droit_nouveau=droit_nouveau,  # Après modification
                type_action="Modification",
                utilisateur=utilisateur  # Assurez-vous que l'utilisateur est renseigné
            )
            form.save()
            messages.success(request, "L'inscription a été modifiée avec succès !")
            return redirect('dashboard')
    else:
        form = InscriptionForm(instance=inscription)

    return render(request, 'modifier_inscription.html', {'form': form, 'id': id})

# Vue pour supprimer une inscription
@login_required
def delete_action(request, id):
    # Vérifier si l'utilisateur est connecté
    utilisateur = request.user if request.user.is_authenticated else None

    # Si l'utilisateur n'est pas authentifié, vous pouvez soit le définir par défaut, soit lever une exception
    if utilisateur is None:
        # Par exemple, si vous souhaitez laisser un utilisateur par défaut (par exemple, un admin ou autre)
        utilisateur = 'Utilisateur Anonyme'  # Ou une instance d'utilisateur par défaut
    # Logique pour supprimer l'objet avec l'id donné
    try:
        objet_a_supprimer = Inscription.objects.get(id=id)

        # Assigner les anciens et nouveaux droits d'inscription
        droit_ancien = objet_a_supprimer.droit_inscription  # Assurez-vous que ce champ existe dans votre modèle
        droit_nouveau = objet_a_supprimer.droit_inscription  # Ajoutez la logique pour mettre à jour le droit si nécessaire

        # Créer un audit
        AuditInscription.objects.create(
            inscription=objet_a_supprimer,
            matricule=objet_a_supprimer.matricule,
            nom=objet_a_supprimer.nom,
            prenom=objet_a_supprimer.prenom,
            date_naissance=objet_a_supprimer.date_naissance,
            adresse=objet_a_supprimer.adresse,
            droit_ancien=droit_ancien,  # Avant modification
            droit_nouveau=droit_nouveau,  # Après modification
            type_action="Suppression",
            utilisateur=utilisateur  # Assurez-vous que l'utilisateur est renseigné
        )
        objet_a_supprimer.delete()
        messages.success(request, "L'inscription a été supprimée avec succès.")
        return redirect('dashboard')  # Redirige vers la page du tableau de bord après la suppression
    except Inscription.DoesNotExist:
        # Gère le cas où l'objet n'existe pas
        messages.error(request, "L'inscription spécifiée n'existe pas.")
        return redirect('dashboard')  # Redirige vers le tableau de bord en cas d'erreur



