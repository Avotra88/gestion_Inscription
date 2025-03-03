# forms.py
from django import forms
from .models import Inscription, Audit, AuditAction
from django.contrib.auth.models import User


class InscriptionForm(forms.ModelForm):
    class Meta:
        model = Inscription
        fields = ['matricule', 'nom', 'prenom', 'date_naissance', 'adresse', 'droit_inscription']

class AuditForm(forms.ModelForm):
    class Meta:
        model = Audit
        fields = ['type_action', 'matricule', 'nom', 'prenom', 'date_naissance', 'adresse', 'droit_ancien', 'droit_nouveau']

class AuditActionForm(forms.ModelForm):
    class Meta:
        model = AuditAction
        fields = ['type_action', 'audit', 'utilisateur']
