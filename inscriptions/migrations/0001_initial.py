# Generated by Django 5.1.6 on 2025-03-08 05:26

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Inscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('matricule', models.CharField(max_length=20, unique=True)),
                ('nom', models.CharField(max_length=100)),
                ('prenom', models.CharField(max_length=100)),
                ('date_naissance', models.DateField()),
                ('adresse', models.TextField(blank=True, null=True)),
                ('droit_inscription', models.BooleanField(default=True)),
                ('utilisateur', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='AuditInscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('matricule', models.CharField(max_length=20)),
                ('nom', models.CharField(max_length=100)),
                ('prenom', models.CharField(default='Inconnu', max_length=100)),
                ('date_naissance', models.DateField(blank=True, null=True)),
                ('adresse', models.CharField(default='Adresse inconnue', max_length=255)),
                ('droit_ancien', models.BooleanField(blank=True, null=True)),
                ('droit_nouveau', models.BooleanField(blank=True, null=True)),
                ('type_action', models.CharField(choices=[('ajout', 'Ajout'), ('modification', 'Modification'), ('suppression', 'Suppression')], max_length=20)),
                ('date_action', models.DateTimeField(auto_now_add=True)),
                ('date_mise_a_jour', models.DateTimeField(default=django.utils.timezone.now)),
                ('utilisateur', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('inscription', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='inscriptions.inscription')),
            ],
        ),
        migrations.CreateModel(
            name='StatistiqueInscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(choices=[('ajout', 'Ajout'), ('modification', 'Modification'), ('suppression', 'Suppression')], max_length=20)),
                ('date_action', models.DateTimeField(auto_now_add=True)),
                ('details', models.TextField(blank=True, null=True)),
                ('inscription', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inscriptions.inscription')),
                ('utilisateur', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
