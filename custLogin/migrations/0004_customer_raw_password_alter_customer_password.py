# Generated by Django 5.1.7 on 2025-03-22 17:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('custLogin', '0003_managerprofile_password_managerprofile_username'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='raw_password',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AlterField(
            model_name='customer',
            name='password',
            field=models.CharField(max_length=128),
        ),
    ]
