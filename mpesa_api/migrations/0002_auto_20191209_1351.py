# Generated by Django 2.2.7 on 2019-12-09 10:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mpesa_api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mpesapayment',
            name='description',
            field=models.CharField(max_length=20),
        ),
        migrations.AlterField(
            model_name='mpesapayment',
            name='phone_number',
            field=models.CharField(max_length=20),
        ),
        migrations.AlterField(
            model_name='mpesapayment',
            name='reference',
            field=models.CharField(max_length=20),
        ),
        migrations.AlterField(
            model_name='mpesapayment',
            name='type',
            field=models.CharField(max_length=50),
        ),
    ]