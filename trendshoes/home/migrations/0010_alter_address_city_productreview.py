# Generated by Django 4.1.7 on 2023-04-06 07:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('admindb', '0001_initial'),
        ('home', '0009_alter_address_city_delete_productreview'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='city',
            field=models.CharField(choices=[('Hubli', 'Hubli'), ('Kochi', 'Kochi'), ('Hydrabad', 'Hydrabad'), ('Kozhikkode', 'Kozhikkode'), ('Thiruvananthapuram', 'Thiruvananthapuram'), ('Kannur', 'Kannur'), ('Ernakulam', 'Ernakulam'), ('Madurai', 'Madurai'), ('Coimbator', 'Coimbator'), ('Banglore', 'Banglore')], max_length=255),
        ),
        migrations.CreateModel(
            name='ProductReview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.CharField(max_length=50)),
                ('rating', models.IntegerField(choices=[(1, 'Poor'), (2, 'Fair'), (3, 'Average'), (4, 'Good'), (5, 'Excellent')])),
                ('comment', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='admindb.variant')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
