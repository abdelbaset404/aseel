from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('advances', '0004_alter_advanceperiod_options_and_more'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                ALTER TABLE advances_advancerequest
                ADD COLUMN IF NOT EXISTS admin_decision VARCHAR(20) NULL;

                ALTER TABLE advances_advancerequest
                ADD COLUMN IF NOT EXISTS user_locked BOOLEAN NOT NULL DEFAULT FALSE;
            """,
            reverse_sql="""
                ALTER TABLE advances_advancerequest
                DROP COLUMN IF EXISTS admin_decision;

                ALTER TABLE advances_advancerequest
                DROP COLUMN IF EXISTS user_locked;
            """
        ),
    ]
