from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect, get_object_or_404
from inscriptions.models import Inscription, AuditInscription, StatistiqueInscription
from django.contrib.auth.decorators import login_required, user_passes_test
import logging
from django.contrib import messages
from .forms import InscriptionForm, CustomUserCreationForm
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.http import HttpResponse


 # Si la fonction est définie dans un autre fichier dans le même répertoire

# Configuration du logger

logger = logging.getLogger(__name__)

# Vue de la page d'accueil
def home(request):
    return redirect('login')

@login_required
def dashboard(request):
    print(f"Utilisateur: {request.user.username}, is_staff: {request.user.is_staff}")
    print(f"Groupes: {[group.name for group in request.user.groups.all()]}")

    if request.user.is_staff or request.user.groups.filter(name="Administrateur").exists():
        return redirect('dashboard_admin')  # Redirection pour les administrateurs

    return redirect('dashboard_user')  # Redirection pour les utilisateurs classiques


@login_required
def dashboard_user(request):
    # Récupère toutes les inscriptions
    inscriptions = Inscription.objects.all()

    # Passer les données au template
    return render(request, 'dashboard_user.html', {'inscriptions': inscriptions})

@login_required
def dashboard_admin(request):
    # Récupérer tous les audits
    audits = AuditInscription.objects.all()

    # Calculer les statistiques
    stats = {
        'ajouts': audits.filter(type_action=AuditInscription.AJOUT).count(),
        'modifications': audits.filter(type_action=AuditInscription.MODIFICATION).count(),
        'suppressions': audits.filter(type_action=AuditInscription.SUPPRESSION).count(),
    }

    # Récupérer tous les utilisateurs
    users = User.objects.all()  # Récupérer la liste de tous les utilisateurs

    # Passer les données au template
    return render(request, 'dashboard_admin.html', {
        'audits': audits,
        'stats': stats,
        'users': users,  # Passer les utilisateurs récupérés au template
    })
    
@login_required
def user_list(request):
    # Récupérer tous les utilisateurs
    users = User.objects.all()
    return render(request, 'user_list.html', {'users': users})

# Signal pour créer les groupes et permissions
@receiver(post_migrate)
def create_roles(sender, **kwargs):
    if sender.name == 'gestion_inscription':  # Remplacez par le nom réel de votre application
        # Créer les groupes
        admin_group, created = Group.objects.get_or_create(name="Administrateur")
        user_group, created = Group.objects.get_or_create(name="Utilisateur")
        
        # Récupérer le modèle AuditInscription pour assigner des permissions
        audit_content_type = ContentType.objects.get_for_model(AuditInscription)
        
        # Créer la permission "view_audit" pour le groupe Administrateur
        view_audit_permission, created = Permission.objects.get_or_create(
            codename="view_audit",
            name="Peut voir les audits",
            content_type=audit_content_type,
        )
        admin_group.permissions.add(view_audit_permission)

        print("Groupes et permissions créés avec succès !")

# Vue pour ajouter une inscription
# Vérifier si l'utilisateur est un administrateur
@user_passes_test(lambda user: not user.is_staff)
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
        return redirect('dashboard_user')  # Redirection vers le dashboard utilisateur
    
    return render(request, 'ajouter_inscription.html')

# Vue de la connexion (login)
def login_view(request):
    if request.user.is_authenticated:
        return redirect_dashboard(request.user)

    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            logger.info(f"Connexion réussie pour {user.username}.")
            messages.success(request, "Connexion réussie !")
            return redirect_dashboard(user)
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
# Fonction de redirection en fonction du type d'utilisateur

def redirect_dashboard(user):
    if user.is_staff:
        return redirect('dashboard_admin')  # Redirige vers le tableau de bord admin
    else:
        return redirect('dashboard_user')  # Redirige vers le tableau de bord utilisateur


# Vue pour auditer une action sur une inscription
@login_required
def audit_action(request, id):
    inscription = get_object_or_404(Inscription, id=id)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'modifier':
            # Convertir date_naissance en datetime si elle est fournie
            date_naissance_str = request.POST.get('date_naissance', None)
            if date_naissance_str:
                try:
                    inscription.date_naissance = datetime.strptime(date_naissance_str, "%Y-%m-%d").date()
                except ValueError:
                    messages.error(request, "Format de date invalide")

            inscription.nom = request.POST.get('nom', inscription.nom)
            inscription.prenom = request.POST.get('prenom', inscription.prenom)
            inscription.adresse = request.POST.get('adresse', inscription.adresse)
            inscription.droit_inscription = request.POST.get('droit_inscription') == "on" if 'droit_inscription' in request.POST else False
            inscription.save()
            create_audit(inscription, 'modification', request)
            messages.success(request, "Inscription modifiée avec succès.")

        elif action == 'supprimer':
            create_audit(inscription, 'suppression', request)
            inscription.delete()
            messages.success(request, "Inscription supprimée avec succès.")

    return redirect('dashboard_user')

def create_audit(inscription, action, request):
    utilisateur = request.user if request.user.is_authenticated else None

    # Récupérer l'ancien état des droits
    dernier_audit = AuditInscription.objects.filter(inscription=inscription).order_by('-date_action').first()
    droit_ancien = dernier_audit.droit_nouveau if dernier_audit else None  
    droit_nouveau = inscription.droit_inscription  

    AuditInscription.objects.create(
        inscription=inscription,
        matricule=inscription.matricule,
        nom=inscription.nom,
        prenom=inscription.prenom,
        date_naissance=inscription.date_naissance,
        adresse=inscription.adresse,
        droit_ancien=droit_ancien,
        droit_nouveau=droit_nouveau,
        type_action=action,
        utilisateur=utilisateur
    )

# Vue pour afficher les statistiques des inscriptions
@login_required
def statistiques_inscriptions(request):
    if not request.user.groups.filter(name="Administrateur").exists():
        messages.error(request, "Vous n'avez pas accès à cette page.")
        return redirect('dashboard_user')  # Ou vers une autre page d'erreur
    statistiques = StatistiqueInscription.objects.all().order_by('-timestamp')
    return render(request, 'inscriptions/statistiques_inscriptions.html', {'statistiques': statistiques})

# Vue pour modifier une inscription
@login_required
def modifier_inscription(request, id):
    inscription = get_object_or_404(Inscription, id=id)

    if request.method == 'POST':
        form = InscriptionForm(request.POST, instance=inscription)
        if form.is_valid():
            form.save()

            # Assigner les anciens et nouveaux droits d'inscription
            droit_ancien = inscription.droit_inscription  
            inscription.droit_inscription = form.cleaned_data['droit_inscription']
            droit_nouveau = inscription.droit_inscription  

            # Créer un audit
            AuditInscription.objects.create(
                inscription=inscription,
                matricule=inscription.matricule,
                nom=inscription.nom,
                prenom=inscription.prenom,
                date_naissance=inscription.date_naissance,
                adresse=inscription.adresse,
                droit_ancien=droit_ancien,  
                droit_nouveau=droit_nouveau,  
                type_action="Modification",
                utilisateur=request.user  
            )
            messages.success(request, "L'inscription a été modifiée avec succès !")
            return redirect('dashboard_user')
    else:
        form = InscriptionForm(instance=inscription)

    return render(request, 'modifier_inscription.html', {'form': form, 'id': id})

# Vue pour supprimer une inscription
@login_required
def delete_action(request, id):
    try:
        inscription = Inscription.objects.get(id=id)

        # Créer un audit avant suppression
        create_audit(inscription, 'suppression', request)
        inscription.delete()

        messages.success(request, "L'inscription a été supprimée avec succès.")
        return redirect('dashboard_user')  # Redirige vers le tableau de bord après la suppression
    except Inscription.DoesNotExist:
        messages.error(request, "L'inscription spécifiée n'existe pas.")
        return redirect('dashboard_user')  # Redirige vers le tableau de bord en cas d'erreur

def confirm_delete(request, inscription_id):
    inscription = get_object_or_404(Inscription, id=inscription_id)
    
    if request.method == 'POST':
        inscription.delete()
        messages.success(request, "L'inscription a été supprimée avec succès.")
        return redirect('dashboard_user')  # Redirigez vers le tableau de bord ou une autre page
    
    return render(request, 'confirm_delete.html', {'inscription': inscription})

@login_required
def create_user(request):
    # Vérifier que l'utilisateur a les droits d'accès (groupe Administrateur)
    if not request.user.groups.filter(name="Administrateur").exists():
        messages.error(request, "Vous n'avez pas accès à cette page.")
        return redirect('dashboard_user')  # Redirection vers le tableau de bord non admin
    
    # Traitement du formulaire lors de l'envoi
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Sauvegarder l'utilisateur
            user = form.save()
            # Vérifier si un groupe est sélectionné dans le formulaire
            group = form.cleaned_data.get('group')  # 'group' est un champ du formulaire
            if group:
                # Ajouter l'utilisateur au groupe sélectionné
                user.groups.add(group)
            
            # Sauvegarder les modifications
            user.save()

            messages.success(request, f"L'utilisateur {user.username} a été créé avec succès.")
            return redirect('dashboard_admin')  # Redirection vers le tableau de bord administrateur

        else:
            # Si le formulaire est invalide
            messages.error(request, "Formulaire invalide. Vérifiez les informations saisies.")
    else:
        form = CustomUserCreationForm()  # Afficher un formulaire vide si c'est une requête GET
    
    return render(request, 'create_user.html', {'form': form, 'name': 'Créer un utilisateur'})

@login_required
def modify_user(request, user_id):
    # Vérifier si l'utilisateur actuel est un administrateur
    if not request.user.groups.filter(name="Administrateur").exists():
        messages.error(request, "Vous n'avez pas accès à cette page.")
        return redirect('dashboard_user')  # Ou rediriger vers une autre page autorisée
    
    # Récupérer l'utilisateur à modifier
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, instance=user)
        if form.is_valid():
            # Sauvegarder les modifications de l'utilisateur
            user = form.save()

            # Mettre à jour les groupes de l'utilisateur
            user.groups.clear()  # Retirer l'utilisateur des anciens groupes
            user.groups.add(form.cleaned_data['group'])  # Ajouter l'utilisateur au groupe sélectionné

            messages.success(request, "Les informations de l'utilisateur ont été mises à jour.")
            return redirect('dashboard_admin')
        else:
            messages.error(request, "Formulaire invalide.")
    else:
        # Affichage du formulaire avec les données actuelles de l'utilisateur
        form = CustomUserCreationForm(instance=user)

    return render(request, 'modify_user.html', {'form': form})

@login_required
def delete_user(request, user_id):
    # Vérifier si l'utilisateur actuel est un administrateur
    if not request.user.groups.filter(name="Administrateur").exists():
        messages.error(request, "Vous n'avez pas accès à cette page.")
        return redirect('dashboard_user')  # Ou rediriger vers une autre page autorisée

    try:
        # Tenter de récupérer l'utilisateur à supprimer
        user = User.objects.get(id=user_id)
        user.delete()  # Supprimer l'utilisateur
        messages.success(request, "L'utilisateur a été supprimé avec succès.")
    except User.DoesNotExist:
        messages.error(request, "L'utilisateur spécifié n'existe pas.")
    
    return redirect('dashboard_admin')
