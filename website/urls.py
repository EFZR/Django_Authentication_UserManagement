from django.urls import path
from website import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('post/', views.PostView.as_view(), name='post'),
    path('delete_post/<int:pk>', views.DeletePostView.as_view(), name='delete_post'),
    path('ban_user/<int:pk>', views.BanUserView.as_view(), name='ban_user'),
    path('unban_users/<int:pk>', views.UnbanUserView.as_view(), name='unban_user'),
    path('users/', views.UsersView.as_view(), name='users'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
]