# Generated by Django 4.1.7 on 2023-04-06 07:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0010_alter_address_city_productreview'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='city',
            field=models.CharField(choices=[('Coimbator', 'Coimbator'), ('Madurai', 'Madurai'), ('Kochi', 'Kochi'), ('Hubli', 'Hubli'), ('Kannur', 'Kannur'), ('Thiruvananthapuram', 'Thiruvananthapuram'), ('Ernakulam', 'Ernakulam'), ('Banglore', 'Banglore'), ('Hydrabad', 'Hydrabad'), ('Kozhikkode', 'Kozhikkode')], max_length=255),
        ),
        migrations.AlterField(
            model_name='productreview',
            name='rating',
            field=models.IntegerField(choices=[('Poor', 'Poor'), ('Fair', 'Fair'), ('Average', 'Average'), ('Good', 'Good'), ('Excellent', 'Excellent')]),
        ),
    ]
