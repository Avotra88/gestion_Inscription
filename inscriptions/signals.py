from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from .models import AuditInscription

@receiver(post_migrate)
def create_roles(sender, **kwargs):
    if sender.name == 'inscriptions':  # Utilisez 'inscriptions' ici
        admin_group, created = Group.objects.get_or_create(name="Administrateur")
        user_group, created = Group.objects.get_or_create(name="Utilisateur")

        # Récupérer le modèle AuditInscription pour assigner des permissions
        audit_content_type = ContentType.objects.get_for_model(AuditInscription)

        # Ajouter la permission de voir les audits
        view_audit_permission, created = Permission.objects.get_or_create(
            codename="view_audit",
            name="Peut voir les audits",
            content_type=audit_content_type,
        )

        # Assigner la permission aux groupes
        admin_group.permissions.add(view_audit_permission)
        user_group.permissions.add(view_audit_permission)

        print("Groupes et permissions créés avec succès !")
