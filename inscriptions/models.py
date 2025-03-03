from django.db import models
from django.contrib.auth.models import User

class Inscription(models.Model):
    matricule = models.CharField(max_length=20)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    date_naissance = models.DateField()
    adresse = models.TextField(blank=True, null=True)
    droit_inscription = models.BooleanField(default=True)  # Valeur par défaut ajoutée

    def __str__(self):
        return f"{self.nom} {self.prenom} - {self.matricule}"

class AuditInscription(models.Model):
    AJOUT = 'AJOUT'
    MODIFICATION = 'MODIFICATION'
    SUPPRESSION = 'SUPPRESSION'
    ACTION_CHOICES = [
        (AJOUT, 'Ajout'),
        (MODIFICATION, 'Modification'),
        (SUPPRESSION, 'Suppression'),
    ]

    inscription = models.ForeignKey(Inscription, on_delete=models.CASCADE, null=True)
    matricule = models.CharField(max_length=100)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100, default="Inconnu")  # Valeur par défaut ajoutée
    date_naissance = models.DateField(null=False, default="2000-01-01")  # Valeur par défaut ajoutée
    adresse = models.CharField(max_length=255, default="Adresse inconnue")
    droit_inscription = models.BooleanField(default=True)  # Valeur par défaut ajoutée
    type_action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    utilisateur = models.CharField(max_length=100)
    date_mise_a_jour = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.type_action} par {self.utilisateur} - {self.inscription}"

class Audit(models.Model):
    matricule = models.CharField(max_length=100)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    date_naissance = models.DateField()
    adresse = models.CharField(max_length=200)
    droit_ancien = models.CharField(max_length=100)
    droit_nouveau = models.CharField(max_length=100)
    type_action = models.CharField(max_length=100)
    date_action = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nom} {self.prenom} - {self.type_action}"

# Définition du modèle StatistiqueInscription séparée pour éviter les problèmes d'importation circulaire
class StatistiqueInscription(models.Model):
    ACTION_CHOICES = [
        ('ajout', 'Ajout'),
        ('modification', 'Modification'),
        ('suppression', 'Suppression'),
    ]

    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    inscription_id = models.IntegerField()  # ID de l'inscription concernée
    date_action = models.DateTimeField(auto_now_add=True)
    utilisateur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  # Si vous voulez enregistrer l'utilisateur
    details = models.TextField(blank=True, null=True)  # Détails supplémentaires si nécessaire

    def __str__(self):
        return f"{self.get_action_display()} - {self.inscription_id} - {self.date_action}"

class AuditAction(models.Model):
    AJOUT = 'AJOUT'
    MODIFICATION = 'MODIFICATION'
    SUPPRESSION = 'SUPPRESSION'
    
    ACTION_CHOICES = [
        (AJOUT, 'Ajout'),
        (MODIFICATION, 'Modification'),
        (SUPPRESSION, 'Suppression'),
    ]

    audit = models.ForeignKey(Audit, on_delete=models.CASCADE)
    type_action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    utilisateur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    date_action = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.type_action} par {self.utilisateur} - {self.date_action}"
