from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .models import User
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password


def signin(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        # Check if the user exists
        if not User.objects.filter(email=email).exists():
            messages.error(request, "User doesn't exist.")
            return render(
                request,
                "user/login.html",
                {"message": "User doesn't exist. Please sign up"},
            )

        user = User.objects.get(email=email)

        authenticated_user = authenticate(email=email, password=password)
        if authenticated_user is not None:
            # Check the password using check_password
            if check_password(password, authenticated_user.password):
                request.session["email"] = email
                request.session.save()
                login(request, authenticated_user)
                messages.success(request, "Login Successful")
                return redirect("/")

        messages.error(request, "Incorrect email or password")
        return render(
            request, "user/login.html", {"message": "Incorrect email or password"}
        )

    return render(request, "user/login.html")


def logout_view(request):
    if request.session.get("email", ""):
        del request.session["email"]
    request.session.save()
    logout(request)
    messages.success(request, "Logout Successful")
    return redirect("/")


def add_user(request):
    if request.method == "POST":
        try:
            email = request.POST.get("email")
            username = request.POST.get("username")
            if User.objects.filter(email=email).exists():
                messages.error(request, "User with this email already exists!")
                return redirect("/user/add_user")
            password = request.POST.get("password")
            conformpassword = request.POST.get("conformpassword")
            if password != conformpassword:
                messages.error(request, "Password and conform password do not match")
                return redirect("/user/add_user")
            is_student = request.POST.get("student")
            student = is_student == 'on'
            teacher = is_student != 'on'

            hashed_password = make_password(password)
            user = User.objects.create(
                username=username,
                email=email,
                password=hashed_password,
                teacher=teacher,
                student=student,
            )
            authenticated_user = authenticate(email=email, password=password)
            if authenticated_user is not None:
                # Check the password using check_password
                if check_password(password, authenticated_user.password):
                    request.session["email"] = email
                    request.session.save()
                    login(request, authenticated_user)
                    messages.success(request, "User added successfully!")
                    return redirect("/")
            messages.error(request, "Incorrect email or password")
            return render(
                request, "user/login.html", {"message": "Incorrect email or password"}
            )
        except Exception as e:
            messages.error(request, "User Name or Email already exists")
            return render(request, "user/login.html", {"page": "signup"})

    return render(request, "user/login.html", {"page": "signup"})
