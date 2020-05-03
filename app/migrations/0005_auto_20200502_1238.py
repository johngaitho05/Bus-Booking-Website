# Generated by Django 2.2.7 on 2020-05-02 09:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_auto_20200502_0854'),
    ]

    operations = [
        migrations.RenameField(
            model_name='route',
            old_name='cost',
            new_name='economy_class_cost',
        ),
        migrations.AddField(
            model_name='route',
            name='first_class_cost',
            field=models.CharField(default='0', max_length=10),
            preserve_default=False,
        ),
    ]