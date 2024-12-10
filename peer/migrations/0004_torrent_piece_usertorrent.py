# Generated by Django 5.0.6 on 2024-12-10 12:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("peer", "0003_userprofile_peer_id"),
    ]

    operations = [
        migrations.CreateModel(
            name="Torrent",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("file_length", models.BigIntegerField()),
                ("piece_length", models.IntegerField()),
                ("info_hash", models.CharField(max_length=40, unique=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "uploaded_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="torrents",
                        to="peer.userprofile",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Piece",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("index", models.IntegerField()),
                ("hash_value", models.CharField(max_length=40)),
                (
                    "torrent",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="pieces",
                        to="peer.torrent",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="UserTorrent",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("current_directory", models.CharField(max_length=255)),
                ("file_path", models.CharField(max_length=255)),
                ("peer_id", models.CharField(max_length=255)),
                ("is_available", models.BooleanField(default=True)),
                (
                    "torrent",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="peer.torrent"
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="peer.userprofile",
                    ),
                ),
            ],
        ),
    ]
