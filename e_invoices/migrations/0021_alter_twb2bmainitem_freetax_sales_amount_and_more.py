# Generated by Django 5.1.7 on 2025-04-14 10:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('e_invoices', '0020_alter_twb2bmainitem_invoice_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='twb2bmainitem',
            name='freetax_sales_amount',
            field=models.DecimalField(blank=True, decimal_places=7, max_digits=13, null=True),
        ),
        migrations.AlterField(
            model_name='twb2bmainitem',
            name='zerotax_sales_amount',
            field=models.DecimalField(blank=True, decimal_places=7, max_digits=13, null=True),
        ),
    ]
