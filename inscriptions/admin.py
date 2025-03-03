from django.contrib import admin
from .models import AuditInscription  # Assurez-vous que le modèle est importé correctement

# Enregistrer le modèle dans l'admin
admin.site.register(AuditInscription)
