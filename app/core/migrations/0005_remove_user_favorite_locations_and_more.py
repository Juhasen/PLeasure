# Generated by Django 4.0.10 on 2024-05-26 18:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_remove_user_favorite_locations_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='favorite_locations',
        ),
        migrations.AddField(
            model_name='user',
            name='favorite_locations',
            field=models.ManyToManyField(blank=True, to='core.location'),
        ),
    ]
