# Generated by Django 3.2.13 on 2022-09-14 14:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import signoffs.core.models.fields
import signoffs.core.models.signets


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('signoffs_signets', '0001_initial'),
        ('signoffs_approvals', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Content',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contents', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='NewBikeRackRequest',
            fields=[
                ('stamp_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='signoffs_approvals.stamp')),
                ('street_number', models.CharField(max_length=200)),
                ('street_name', models.CharField(max_length=200)),
                ('street_side', models.CharField(max_length=200)),
                ('skytrain_station', models.CharField(max_length=200)),
                ('bia', models.CharField(max_length=200)),
                ('num_racks', models.CharField(max_length=200)),
                ('year_installed', models.CharField(max_length=200)),
                ('rack_type', models.CharField(max_length=200)),
                ('storage_capacity', models.CharField(max_length=200)),
                ('status', models.CharField(max_length=200)),
                ('street_located', models.CharField(max_length=200)),
            ],
            options={
                'ordering': ['timestamp'],
                'abstract': False,
            },
            bases=('signoffs_approvals.stamp',),
        ),
        migrations.CreateModel(
            name='VancouverBikeRack',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('street_number', models.CharField(max_length=200)),
                ('street_name', models.CharField(max_length=200)),
                ('street_side', models.CharField(max_length=200)),
                ('skytrain_station', models.CharField(max_length=200)),
                ('bia', models.CharField(max_length=200)),
                ('num_racks', models.CharField(max_length=200)),
                ('year_installed', models.CharField(max_length=200)),
                ('rack_type', models.CharField(max_length=200)),
                ('storage_capacity', models.CharField(max_length=200)),
                ('status', models.CharField(max_length=200)),
                ('street_located', models.CharField(max_length=200)),
                ('signoff_signet', signoffs.core.models.fields.SignoffOneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', signet_field_name=None, signoff_type='exampleapp.bikerack_signoff', to='signoffs_signets.signet')),
            ],
        ),
        migrations.CreateModel(
            name='ContentSignet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('signoff_id', models.CharField(max_length=100, validators=[signoffs.core.models.signets.validate_signoff_id], verbose_name='Signoff Type')),
                ('sigil', models.CharField(max_length=256, verbose_name='Signed By')),
                ('sigil_label', models.CharField(max_length=256, null=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('content', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reader', to='exampleapp.content')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['timestamp'],
                'abstract': False,
            },
        ),
    ]
