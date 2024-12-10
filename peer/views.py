from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt


import os
import json

from .models import User, UserProfile
from . import tracker_utils


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

    return render(
        request,
        "peer/index.html",
        {"current_directory": current_directory, "peer_id": peer_id},
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

            return JsonResponse({"success": True}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)
