from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_migrate
from django.dispatch import receiver

# Modèle Inscription
class Inscription(models.Model):
    matricule = models.CharField(max_length=20, unique=True)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    date_naissance = models.DateField()
    adresse = models.TextField(blank=True, null=True)
    droit_inscription = models.BooleanField(default=True)  # Valeur par défaut
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.nom} {self.prenom} - {self.matricule}"

    class Meta:
        verbose_name = 'Inscription'
        verbose_name_plural = 'Inscriptions'


# Modèle Audit des Inscriptions
class AuditInscription(models.Model):
    AJOUT = 'ajout'
    MODIFICATION = 'modification'
    SUPPRESSION = 'suppression'
    
    ACTION_CHOICES = [
        (AJOUT, 'Ajout'),
        (MODIFICATION, 'Modification'),
        (SUPPRESSION, 'Suppression'),
    ]

    inscription = models.ForeignKey(Inscription, on_delete=models.SET_NULL, null=True, blank=True)
    matricule = models.CharField(max_length=20)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100, default="Inconnu")
    date_naissance = models.DateField(null=True, blank=True)
    adresse = models.CharField(max_length=255, default="Adresse inconnue")
    droit_ancien = models.BooleanField(null=True, blank=True)  # Avant modification
    droit_nouveau = models.BooleanField(null=True, blank=True)  # Après modification

    type_action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)
    date_action = models.DateTimeField(auto_now_add=True)
    date_mise_a_jour = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.get_type_action_display()} - {self.nom} {self.prenom} ({self.matricule}) par {self.utilisateur}"

    class Meta:
        verbose_name = 'Audit d\'Inscription'
        verbose_name_plural = 'Audits des Inscriptions'


# Modèle pour les statistiques des inscriptions
class StatistiqueInscription(models.Model):
    action = models.CharField(max_length=20, choices=AuditInscription.ACTION_CHOICES)
    inscription = models.ForeignKey(Inscription, on_delete=models.CASCADE)
    date_action = models.DateTimeField(auto_now_add=True)
    utilisateur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    details = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.get_action_display()} - {self.inscription.id} - {self.date_action}"

    class Meta:
        verbose_name = 'Statistique d\'Inscription'
        verbose_name_plural = 'Statistiques des Inscriptions'


