# Generated by Django 5.0.6 on 2024-12-10 13:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("peer", "0004_torrent_piece_usertorrent"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="is_active",
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name="torrent",
            name="info_hash",
            field=models.CharField(max_length=40),
        ),
    ]
