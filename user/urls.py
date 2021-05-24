from django.urls import path
from . import views
from .views import InboxListView, MsgListView, InboxCreateView, MsgCreateView
from django.contrib.auth import views as auth_views
from django.shortcuts import render,redirect
urlpatterns = [
    path("", InboxListView.as_view(), name='home'),
    path('link/<int:pk>/', views.inbox, name='inbox_url'),
    path('inbox/new/', InboxCreateView.as_view(), name='new-inbox'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='user/login.html'), name='login'),
    path('user/logout/', auth_views.LogoutView.as_view(template_name='user/logout.html'), name='logout'),
    path('profile', views.profile, name='profile'),
    path('sayit/message/<int:id>/<str:message>/', MsgCreateView.as_view(), name='message'),
    path('message_view/<int:pk>/<str:message>/', MsgListView.as_view(), name='message-view'),
    path('delete_profile/<int:pk>/', views.delete_profile, name='delete-profile'),
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='user/password_reset.html'),
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='user/password_reset_done.html'),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='user/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name='user/password_reset_complete.html'),
         name='password_reset_complete'),
    ]
