# Generated by Django 4.2.7 on 2023-11-08 23:55

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('Accepted', 'Accepted'), ('Denied', 'Denied'), ('Withdrawn', 'Withdrawn')], default='Pending', max_length=10)),
                ('creation_time', models.DateTimeField(auto_now_add=True)),
                ('last_update_time', models.DateTimeField(auto_now=True)),
                ('pet_name', models.CharField(max_length=50)),
                ('owner_name', models.CharField(default='', max_length=50)),
                ('area_code', models.CharField(max_length=4)),
                ('phone_number', models.CharField(max_length=10)),
                ('email', models.EmailField(max_length=254)),
                ('address1', models.CharField(max_length=100)),
                ('address2', models.CharField(blank=True, max_length=100, null=True)),
                ('city', models.CharField(max_length=100)),
                ('state', models.CharField(max_length=100)),
                ('zip', models.CharField(max_length=10)),
                ('country', models.CharField(max_length=100)),
                ('pet_ownership', models.CharField(choices=[('yes', 'YES'), ('no', 'NO')], max_length=3)),
                ('breed', models.TextField()),
                ('past_pet', models.TextField()),
                ('home_ownership', models.CharField(choices=[('own', 'Own'), ('rent', 'Rent')], max_length=4)),
                ('signature', models.CharField(max_length=255)),
            ],
        ),
    ]
