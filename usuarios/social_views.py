from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.views.generic import TemplateView
from allauth.socialaccount.models import SocialAccount
from allauth.account.signals import user_signed_up
from django.dispatch import receiver
from .models import Usuario

class SocialLoginView(TemplateView):
    template_name = 'usuarios/social_login.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Iniciar Sesión con Google'
        return context

class GoogleSetupRequiredView(TemplateView):
    template_name = 'usuarios/google_setup_required.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Configuración de Google OAuth Requerida'
        return context

@receiver(user_signed_up)
def handle_social_signup(sender, request, user, **kwargs):
    """Manejar el registro de usuarios a través de redes sociales"""
    try:
        # Obtener la cuenta social
        social_account = SocialAccount.objects.get(user=user, provider='google')
        
        # Actualizar información del usuario si es necesario
        if social_account.extra_data:
            extra_data = social_account.extra_data
            
            # Actualizar nombre si está disponible
            if 'name' in extra_data:
                user.first_name = extra_data['name'].split()[0] if extra_data['name'] else ''
                user.last_name = ' '.join(extra_data['name'].split()[1:]) if len(extra_data['name'].split()) > 1 else ''
            
            # Actualizar email si está disponible
            if 'email' in extra_data:
                user.email = extra_data['email']
            
            user.save()
            
        messages.success(request, f'¡Bienvenido {user.get_full_name() or user.email}! Tu cuenta ha sido creada exitosamente.')
        
    except SocialAccount.DoesNotExist:
        pass
    except Exception as e:
        print(f"Error en handle_social_signup: {e}")

def social_login_redirect(request):
    """Redirigir después del login social exitoso"""
    if request.user.is_authenticated:
        messages.success(request, f'¡Bienvenido de vuelta {request.user.get_full_name() or request.user.email}!')
        return redirect('usuarios:perfil')
    return redirect('usuarios:login')
