from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from elavateapp.models import Profile, Idea, Donation
from elavateapp.forms import CommentForm, IdeaForm, ProfileForm, DonationForm

import json
import requests


# Home Page
def home(request):
    return render(request, 'home.html')


# Features Page
def features(request):
    return render(request, 'features.html')


# Innovators Page

def innovaters(request):
    # Fetch all profiles marked as innovators (role='entrepreneur')
    innovators = Profile.objects.filter(role='entrepreneur')

    # Process tags for each innovator
    for innovator in innovators:
        innovator.tag_list = [
            tag.strip() for tag in (innovator.tags or "").split(',')
        ]

    # Pass the processed data to the template
    return render(request, 'innovaters.html', {'innovators': innovators})

# User Registration
def register(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')

        # Check if user already exists
        if User.objects.filter(username=email).exists():
            return render(request, 'register.html', {'error': 'Email already exists.'})

        # Create user and profile
        user = User.objects.create_user(
            username=email, email=email, password=password,
            first_name=first_name, last_name=last_name
        )
        Profile.objects.create(user=user, role=role)

        # Log in the user
        login(request, user)

        # Send welcome email
        send_welcome_email(user)
        return redirect('profile')
    return render(request, 'register.html')


# Send Welcome Email
def send_welcome_email(user):
    send_mail(
        subject="Welcome to ElevateHub!",
        message=f"Hello {user.first_name},\n\nWelcome to ElevateHub! We're thrilled to have you here.",
        from_email="support@elevatehub.com",
        recipient_list=[user.email],
    )


# User Login
def user_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')  # Redirect authenticated users to dashboard

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')  # Redirect to dashboard after successful login
        else:
            return render(request, 'log-in.html', {'error': 'Invalid email or password'})

    return render(request, 'log-in.html')


# Dashboard
# @login_required
def dashboard(request):
    # Ensure the logged-in user has a Profile
    profile, created = Profile.objects.get_or_create(user=request.user)
    suggestions = Profile.objects.exclude(user=request.user)[:5]
    posts = Idea.objects.all().order_by('-timestamp')
    return render(request, 'dashboard.html', {
        'profile': profile,  # Use the retrieved Profile object
        'suggestions': suggestions,
        'posts': posts,
    })




# Profile Setup
@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = ProfileForm(instance=request.user.profile)
    return render(request, 'profile.html', {'form': form})


# Idea Feed
@login_required
def idea_feed(request):
    ideas = Idea.objects.all().order_by('-timestamp')
    return render(request, 'idea_feed.html', {'ideas': ideas})


# Post Idea
@login_required
def post_idea(request):
    if request.method == 'POST':
        form = IdeaForm(request.POST, request.FILES)
        if form.is_valid():
            idea = form.save(commit=False)
            idea.user = request.user
            idea.save()
            return redirect('idea_feed')
    else:
        form = IdeaForm()
    return render(request, 'post_idea.html', {'form': form})


# Idea Details
@login_required
def post_detail(request, idea_id):
    idea = get_object_or_404(Idea, id=idea_id)
    comments = idea.comments.all()
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.idea = idea
            comment.user = request.user
            comment.save()
            return redirect('post_detail', idea_id=idea.id)
    else:
        form = CommentForm()
    return render(request, 'post_detail.html', {
        'idea': idea,
        'comments': comments,
        'form': form,
    })


# Donation Functionality
@login_required
def donate(request):
    if request.method == 'POST':
        form = DonationForm(request.POST)
        if form.is_valid():
            donation = form.save(commit=False)
            donation.user = request.user
            donation.status = 'Pending'
            donation.save()

            access_token = get_mpesa_access_token()
            if access_token:
                response = initiate_stk_push(access_token, donation)
                if response.get('ResponseCode') == '0':
                    donation.status = 'Successful'
                    donation.save()
                    return redirect('dashboard')
                else:
                    donation.status = 'Failed'
                    donation.save()
                    return render(request, 'donation_failed.html')
    else:
        form = DonationForm()
    return render(request, 'donate.html', {'form': form})


def get_mpesa_access_token():
    consumer_key = 'your_consumer_key'
    consumer_secret = 'your_consumer_secret'
    api_url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'

    response = requests.get(api_url, auth=(consumer_key, consumer_secret))
    if response.status_code == 200:
        return response.json().get('access_token')
    return None


def initiate_stk_push(access_token, donation):
    api_url = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
    headers = {'Authorization': f'Bearer {access_token}'}
    payload = {
        "BusinessShortCode": "174379",
        "Password": "your_generated_password",
        "Timestamp": "20231204153000",
        "TransactionType": "CustomerPayBillOnline",
        "Amount": str(donation.amount),
        "PartyA": "2547xxxxxxxx",
        "PartyB": "174379",
        "PhoneNumber": "2547xxxxxxxx",
        "CallBackURL": "https://yourdomain.com/callback",
        "AccountReference": f"Donation-{donation.id}",
        "TransactionDesc": "Donation to ElevateHub"
    }
    response = requests.post(api_url, json=payload, headers=headers)
    return response.json()


def mpesa_callback(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        transaction_id = data.get('Body', {}).get('stkCallback', {}).get('CheckoutRequestID')
        result_code = data.get('Body', {}).get('stkCallback', {}).get('ResultCode')

        try:
            donation = Donation.objects.get(transaction_id=transaction_id)
            donation.status = 'Successful' if result_code == 0 else 'Failed'
            donation.save()
        except Donation.DoesNotExist:
            pass
    return JsonResponse({'status': 'Received'})
