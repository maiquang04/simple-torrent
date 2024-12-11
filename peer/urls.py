from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("sign-up", views.sign_up, name="sign-up"),
    path("upload", views.upload, name="upload"),
    path("download", views.download, name="download"),
    path(
        "set-default-directory",
        views.set_default_directory,
        name="set-default-directory",
    ),
    path("file-transfer", views.file_transfer, name="file-transfer"),
    path(
        "file-slicer-and-merger",
        views.file_slicer_and_merger,
        name="file-slicer-and-merger",
    ),
    path("upload-torrent", views.upload_torrent, name="upload-torrent"),
    path(
        "download-torrent/<int:torrent_id>",
        views.download_torrent,
        name="download-torrent",
    ),
]
