# Generated by Django 5.0.6 on 2024-12-10 13:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("peer", "0005_userprofile_is_active_alter_torrent_info_hash"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="usertorrent",
            name="peer_id",
        ),
    ]