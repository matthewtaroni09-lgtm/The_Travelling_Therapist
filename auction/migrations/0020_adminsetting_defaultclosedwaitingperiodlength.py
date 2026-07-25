from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auction', '0019_auction_waitingcloseout'),
    ]

    operations = [
        migrations.AddField(
            model_name='adminsetting',
            name='defaultClosedWaitingPeriodLength',
            field=models.IntegerField(default=604800, help_text='Closed (Waiting) listings will remain in that state for this many seconds before fully closing.', verbose_name='Default Closed Waiting Period in Seconds'),
        ),
    ]
