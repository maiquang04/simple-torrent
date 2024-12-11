from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt


import os
import json
import bencodepy

from .models import User, UserProfile, Torrent, Piece, UserTorrent
from . import tracker_utils
from .configs import CONFIGS


@login_required(login_url="/login")
def index(request):
    try:
        # Try to fetch the user profile
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        # Handle the case where UserProfile doesn't exist
        # Create a new UserProfile and set the peer_id using the set_peer_id method
        profile = UserProfile.objects.create(user=request.user)
        profile.set_peer_id()
        profile.save()  # Save the newly created profile

    current_directory = profile.default_directory if profile else None
    peer_id = profile.peer_id

    # Fetch all torrents from the database, ordered by created_at in descending order
    torrents = Torrent.objects.all().order_by("-created_at")

    return render(
        request,
        "peer/index.html",
        {
            "current_directory": current_directory,
            "peer_id": peer_id,
            "torrents": torrents,
        },
    )


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(
                request,
                "peer/login.html",
                {"message": "Invalid username and/or password."},
            )
    else:
        return render(request, "peer/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def sign_up(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(
                request,
                "peer/sign-up.html",
                {"message": "Passwords must match."},
            )

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(
                request,
                "peer/sign-up.html",
                {"message": "Username already taken."},
            )
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "peer/sign-up.html")


@login_required
def upload(request):
    profile = UserProfile.objects.filter(user=request.user).first()
    files = []
    if profile and profile.default_directory:
        try:
            files = os.listdir(profile.default_directory)
        except FileNotFoundError:
            files = []

    if request.method == "POST":
        selected_file = request.POST.get("file")
        # Handle logic here

    return render(
        request,
        "peer/upload.html",
        {"files": files, "current_directory": profile.default_directory},
    )


@login_required
def download(request):
    return render(request, "peer/download.html")


@login_required
def set_default_directory(request):
    if request.method == "POST":
        directory = request.POST.get("default-directory")
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        profile.default_directory = directory
        profile.save()

    profile = UserProfile.objects.filter(user=request.user).first()
    current_directory = profile.default_directory if profile else None

    return render(
        request,
        "peer/set-default-directory.html",
        {"current_directory": current_directory},
    )


@login_required
def file_transfer(request):
    profile = UserProfile.objects.get(user=request.user)

    if not profile.peer_id:
        profile.set_peer_id()
        profile.save()

    peer_id = profile.peer_id
    return render(request, "peer/file-transfer.html", {"peer_id": peer_id})


@login_required
def file_slicer_and_merger(request):
    profile = UserProfile.objects.filter(user=request.user).first()
    current_directory = profile.default_directory if profile else None

    return render(
        request,
        "peer/file-slicer-and-merger.html",
        {"current_directory": current_directory},
    )


@csrf_exempt
def upload_torrent(request):
    if request.method == "POST":
        try:
            # Parse JSON body
            data = json.loads(request.body)
            torrent_data = data.get("torrent_data")

            # Check if torrent_data is a string, and parse it if necessary
            if isinstance(torrent_data, str):
                torrent_data = json.loads(torrent_data)

            print(
                "Torrent data", torrent_data
            )  # For debugging, you can print torrent_data to see its structure

            # Pass the torrent_data to the tracker utility to store it in the DB
            torrent = tracker_utils.store_torrent_data(torrent_data)
            print("Torrent", torrent)

            # Get the creation date and convert it to a Unix timestamp
            creation_date = int(torrent.created_at.timestamp())
            print("Torrent creation date:", creation_date)

            return JsonResponse(
                {"success": True, "creation date": creation_date}, status=200
            )
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)


@login_required
def download_torrent(request, torrent_id):
    torrent = get_object_or_404(Torrent, pk=torrent_id)

    # Retrieve the UserTorrent object by matching torrent and uploaded_by user
    user_torrent = get_object_or_404(
        UserTorrent, torrent=torrent, user=torrent.uploaded_by
    )

    # Fetch pieces for this torrent
    pieces = Piece.objects.filter(torrent=torrent)

    # The user who uploaded the torrent
    user_profile = torrent.uploaded_by

    # Create the torrent data dictionary
    torrent_data = {
        "announce": f'{CONFIGS["TRACKER_URL"]}/announce',
        "creation date": int(torrent.created_at.timestamp()),
        "info": {
            "length": torrent.file_length,
            "name": torrent.name,
            "piece length": torrent.piece_length,
            "pieces": [piece.hash_value.encode() for piece in pieces],
        },
        "user": {
            "current directory": user_torrent.current_directory,
            "file path": user_torrent.file_path,
            "peer id": user_profile.peer_id,
        },
    }

    # Encode the torrent data to bencode format
    bencoded_data = bencodepy.encode(torrent_data)

    # Create the torrent filename
    torrent_filename = f"{torrent.name}.torrent"

    # Prepare the response with the torrrent file
    response = HttpResponse(
        bencoded_data, content_type="application/x-bittorrent"
    )
    response["Content-Disposition"] = (
        f'attachment; filename="{torrent_filename}"'
    )

    return response


@csrf_exempt
def get_peer_list(request):

    return JsonResponse({"success": True})


@csrf_exempt
def seed_file(request):
    return JsonResponse({"success": True})
