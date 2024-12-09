from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Home page
    path('register/', views.register, name='register'),
    path('log-in/', views.user_login, name='log-in'),
    path('features/', views.features, name='features'),
    path('innovaters/', views.innovaters, name='innovaters'),
    path('profile/', views.profile, name='profile'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('idea_feed/', views.idea_feed, name='idea_feed'),
    path('post/<int:idea_id>/', views.post_detail, name='post_detail'),
    path('donate/', views.donate, name='donate'),
    path('callback/', views.mpesa_callback, name='mpesa_callback'),
]
