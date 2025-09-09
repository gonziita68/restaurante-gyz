from django.urls import path
from . import views
from . import social_views

app_name = 'usuarios'

urlpatterns = [
    path('', views.index, name='index'),
    path('registro/', views.registro_usuario, name='registro'),
    path('login/', views.login_usuario, name='login'),
    path('logout/', views.logout_usuario, name='logout'),
    path('perfil/', views.perfil_usuario, name='perfil'),
    path('password-reset/', views.password_reset_request, name='password_reset_request'),
    path('password-reset/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    
    # URLs para login social
    path('social-login/', social_views.SocialLoginView.as_view(), name='social_login'),
    path('social-login-redirect/', social_views.social_login_redirect, name='social_login_redirect'),
    path('google-setup-required/', social_views.GoogleSetupRequiredView.as_view(), name='google_setup_required'),
]