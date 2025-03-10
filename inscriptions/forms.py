# forms.py
from django import forms
from .models import Inscription, AuditInscription  # Utilisation de AuditInscription au lieu de Audit et AuditAction
from django.contrib.auth.models import User


class InscriptionForm(forms.ModelForm):
    class Meta:
        model = Inscription
        fields = ['matricule', 'nom', 'prenom', 'date_naissance', 'adresse', 'droit_inscription']


class AuditInscriptionForm(forms.ModelForm):  # Formulaire pour le modèle AuditInscription
    class Meta:
        model = AuditInscription
        fields = ['type_action', 'matricule', 'nom', 'prenom', 'date_naissance', 'adresse', 'droit_ancien', 'droit_nouveau']
