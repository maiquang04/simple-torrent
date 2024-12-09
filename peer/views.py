from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

import os

from .models import User, UserProfile


@login_required(login_url="/login/")
def index(request):
    return render(request, "peer/index.html")


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
