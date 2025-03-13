# forms.py
from django import forms
from .models import Inscription, AuditInscription  # Utilisation de AuditInscription au lieu de Audit et AuditAction
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm  # Assurez-vous de l'importer depuis django.contrib.auth.forms
from django.core.exceptions import ValidationError

class InscriptionForm(forms.ModelForm):
    class Meta:
        model = Inscription
        fields = ['matricule', 'nom', 'prenom', 'date_naissance', 'adresse', 'droit_inscription']


class AuditInscriptionForm(forms.ModelForm):  # Formulaire pour le modèle AuditInscription
    class Meta:
        model = AuditInscription
        fields = ['type_action', 'matricule', 'nom', 'prenom', 'date_naissance', 'adresse', 'droit_ancien', 'droit_nouveau']

from django import forms
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError

class CustomUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label="Mot de passe", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirmer le mot de passe", widget=forms.PasswordInput)
    group = forms.ModelChoiceField(queryset=Group.objects.all(), required=False, label="Groupe")  # Optionnel pour affecter un groupe

    class Meta:
        model = User
        fields = ['username', 'email']  # Inclure 'email' et 'username' dans les champs du formulaire

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        # Vérification que les mots de passe correspondent
        if password1 and password2 and password1 != password2:
            raise ValidationError("Les mots de passe ne correspondent pas.")
        return password2

    def save(self, commit=True):
        # Créer l'utilisateur sans l'enregistrer immédiatement dans la base de données
        user = super().save(commit=False)
        
        # Hachage et affectation du mot de passe
        user.set_password(self.cleaned_data["password1"])
        
        if commit:
            user.save()  # Sauvegarder l'utilisateur dans la base de données
            
            # Ajouter l'utilisateur au groupe s'il en a sélectionné un
            group = self.cleaned_data.get('group')
            if group:
                user.groups.add(group)  # Ajouter l'utilisateur au groupe sélectionné
            
        return user
