from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auction', '0016_bid_selectedskills'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auction',
            name='desiredFlatFeeHourly',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Desired Flat Fee Hourly'),
        ),
        migrations.AlterField(
            model_name='auction',
            name='desiredFlatFeeTotalContract',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Desired Flat Fee Total Contract'),
        ),
    ]
