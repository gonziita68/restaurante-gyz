from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.core.cache import cache
from .forms import RegistroUsuarioForm, LoginUsuarioForm, PasswordResetForm, SetPasswordForm
from .models import Usuario
from .emails import enviar_correo_registro_exitoso, enviar_correo_recuperacion_password, enviar_correo_password_cambiado, enviar_correo_verificacion_cuenta
from .tasks import send_email_task
from django.conf import settings
from django.urls import reverse

THROTTLE_SECONDS = 300  # 5 minutos


def _enqueue_email(*, to_email: str, subject: str, template: str, context: dict, purpose: str) -> None:
    """Encola el envío con Celery si es posible; si falla, ejecuta localmente.
    Usa ejecución local directa cuando CELERY_TASK_ALWAYS_EAGER=True.
    """
    if getattr(settings, 'CELERY_TASK_ALWAYS_EAGER', False):
        # Ejecuta sin broker (modo eager/local)
        send_email_task.apply(kwargs={
            'to_email': to_email,
            'subject': subject,
            'template': template,
            'context': context,
            'purpose': purpose,
        })
        return
    try:
        send_email_task.delay(
            to_email=to_email,
            subject=subject,
            template=template,
            context=context,
            purpose=purpose,
        )
    except Exception:
        # Fallback si no hay broker o hay error de conexión
        send_email_task.apply(kwargs={
            'to_email': to_email,
            'subject': subject,
            'template': template,
            'context': context,
            'purpose': purpose,
        })


def registro_usuario(request):
    """Vista para registro de usuarios con verificación por correo"""
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # El usuario queda inactivo hasta verificar el correo
            user.is_active = False
            user.save()
            # Preparar enlace de verificación
            from django.utils.http import urlsafe_base64_encode
            from django.utils.encoding import force_bytes
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            activar_url = request.build_absolute_uri(
                reverse('usuarios:activar_cuenta', kwargs={'uidb64': uid, 'token': token})
            )
            context = {
                'usuario': user,
                'activar_url': activar_url,
                'nombre_restaurante': getattr(settings, 'SITE_NAME', 'Restaurante GYZ'),
                'site_name': getattr(settings, 'SITE_NAME', 'Restaurante GYZ'),
                'primary_color': getattr(settings, 'BRAND_PRIMARY_COLOR', '#10b981'),
                'logo_url': getattr(settings, 'BRAND_LOGO_URL', ''),
                'support_email': getattr(settings, 'BRAND_SUPPORT_EMAIL', settings.DEFAULT_FROM_EMAIL),
                'subject': 'Verifica tu cuenta - Restaurante GYZ',
            }
            # Enviar asíncrono con fallback
            _enqueue_email(
                to_email=user.email,
                subject='Verifica tu cuenta - Restaurante GYZ',
                template='usuarios/emails/verificacion_cuenta.html',
                context=context,
                purpose='verification',
            )
            messages.success(request, '¡Registro exitoso! Te enviamos un correo para verificar tu cuenta.')
            return redirect('usuarios:login')
        else:
            messages.error(request, 'Por favor, corrige los errores en el formulario.')
    else:
        form = RegistroUsuarioForm()
    
    return render(request, 'usuarios/registro.html', {'form': form})


def login_usuario(request):
    """Vista para login de usuarios"""
    if request.user.is_authenticated:
        return redirect('usuarios:index')
    
    if request.method == 'POST':
        form = LoginUsuarioForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            # Intentar autenticar con username
            user = authenticate(username=username, password=password)
            if user is None:
                # Si no funciona con username, intentar con email
                try:
                    usuario = Usuario.objects.get(email=username)
                    user = authenticate(username=usuario.username, password=password)
                except Usuario.DoesNotExist:
                    user = None
            
            if user is not None:
                if not user.is_active:
                    messages.error(request, 'Tu cuenta aún no está verificada. Revisa tu correo o solicita reenvío.')
                    return redirect('usuarios:login')
                login(request, user)
                user.actualizar_ultimo_acceso()
                messages.success(request, f'¡Bienvenido de vuelta, {user.first_name or user.username}!')
                return redirect('usuarios:index')
            else:
                messages.error(request, 'Credenciales inválidas. Por favor, intenta de nuevo.')
    else:
        form = LoginUsuarioForm()
    
    return render(request, 'usuarios/login.html', {'form': form})


def logout_usuario(request):
    """Vista para logout de usuarios"""
    logout(request)
    messages.info(request, 'Has cerrado sesión exitosamente.')
    return redirect('usuarios:index')

@login_required
def perfil_usuario(request):
    """Vista para mostrar y editar perfil del usuario"""
    if request.method == 'POST':
        messages.success(request, 'Perfil actualizado exitosamente.')
        return redirect('usuarios:perfil')
    
    return render(request, 'usuarios/perfil.html')

def index(request):
    """Vista para la página principal del restaurante"""
    return render(request, 'usuarios/index.html')


def password_reset_request(request):
    """Vista para solicitar reset de contraseña"""
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                usuario = Usuario.objects.get(email=email)
                if enviar_correo_recuperacion_password(usuario, request):
                    messages.success(request, 
                        'Te hemos enviado un correo con las instrucciones para restablecer tu contraseña.')
                else:
                    messages.error(request, 
                        'Hubo un problema enviando el correo. Por favor, intenta más tarde.')
            except Usuario.DoesNotExist:
                messages.success(request, 
                    'Te hemos enviado un correo con las instrucciones para restablecer tu contraseña.')
            
            return redirect('usuarios:login')
    else:
        form = PasswordResetForm()
    
    return render(request, 'usuarios/password_reset.html', {'form': form})


def password_reset_confirm(request, uidb64, token):
    """Vista para confirmar el reset de contraseña"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        usuario = Usuario.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Usuario.DoesNotExist):
        usuario = None
    
    if usuario is not None and default_token_generator.check_token(usuario, token):
        if request.method == 'POST':
            form = SetPasswordForm(usuario, request.POST)
            if form.is_valid():
                form.save()
                # Enviar correo de confirmación (asíncrono con fallback)
                ctx = {
                    'usuario': usuario,
                    'nombre_restaurante': getattr(settings, 'SITE_NAME', 'Restaurante GYZ'),
                    'site_name': getattr(settings, 'SITE_NAME', 'Restaurante GYZ'),
                    'primary_color': getattr(settings, 'BRAND_PRIMARY_COLOR', '#10b981'),
                    'logo_url': getattr(settings, 'BRAND_LOGO_URL', ''),
                    'support_email': getattr(settings, 'BRAND_SUPPORT_EMAIL', settings.DEFAULT_FROM_EMAIL),
                    'subject': 'Contraseña Cambiada Exitosamente - Restaurante GYZ',
                }
                _enqueue_email(
                    to_email=usuario.email,
                    subject='Contraseña Cambiada Exitosamente - Restaurante GYZ',
                    template='usuarios/emails/password_cambiado.html',
                    context=ctx,
                    purpose='password_changed',
                )
                messages.success(request, 
                    'Tu contraseña ha sido restablecida exitosamente. Ya puedes iniciar sesión.')
                return redirect('usuarios:login')
        else:
            form = SetPasswordForm(usuario)
        
        return render(request, 'usuarios/password_reset_confirm.html', {'form': form})
    else:
        messages.error(request, 
            'El enlace de restablecimiento es inválido o ha expirado.')
        return redirect('usuarios:password_reset_request')


def activar_cuenta(request, uidb64, token):
    """Activa la cuenta de usuario tras hacer clic en el enlace de verificación."""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        usuario = Usuario.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Usuario.DoesNotExist):
        usuario = None
    
    if usuario is not None and default_token_generator.check_token(usuario, token):
        if not usuario.is_active:
            usuario.is_active = True
            usuario.save(update_fields=['is_active'])
            # Enviar bienvenida (asíncrono con fallback)
            ctx = {
                'usuario': usuario,
                'nombre_restaurante': getattr(settings, 'SITE_NAME', 'Restaurante GYZ'),
                'site_name': getattr(settings, 'SITE_NAME', 'Restaurante GYZ'),
                'primary_color': getattr(settings, 'BRAND_PRIMARY_COLOR', '#10b981'),
                'logo_url': getattr(settings, 'BRAND_LOGO_URL', ''),
                'support_email': getattr(settings, 'BRAND_SUPPORT_EMAIL', settings.DEFAULT_FROM_EMAIL),
                'subject': 'Bienvenido a Restaurante GYZ - Registro Exitoso',
            }
            _enqueue_email(
                to_email=usuario.email,
                subject='Bienvenido a Restaurante GYZ - Registro Exitoso',
                template='usuarios/emails/registro_exitoso.html',
                context=ctx,
                purpose='welcome',
            )
            messages.success(request, 'Tu cuenta ha sido verificada y activada. Ahora puedes iniciar sesión.')
        else:
            messages.info(request, 'Tu cuenta ya estaba verificada.')
        return redirect('usuarios:login')
    else:
        messages.error(request, 'Enlace de verificación inválido o expirado.')
        return redirect('usuarios:login')


def reenviar_verificacion(request):
    """Permite reenviar correo de verificación con throttle por email."""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        if not email:
            messages.error(request, 'Debes ingresar un correo.'); return redirect('usuarios:login')
        key = f"resend_verif:{email}"
        if cache.get(key):
            messages.info(request, 'Ya enviamos un correo recientemente. Intenta más tarde.'); return redirect('usuarios:login')
        try:
            usuario = Usuario.objects.get(email=email)
            if usuario.is_active:
                messages.info(request, 'Tu cuenta ya está verificada.'); return redirect('usuarios:login')
            from django.utils.http import urlsafe_base64_encode
            from django.utils.encoding import force_bytes
            uid = urlsafe_base64_encode(force_bytes(usuario.pk))
            token = default_token_generator.make_token(usuario)
            activar_url = request.build_absolute_uri(
                reverse('usuarios:activar_cuenta', kwargs={'uidb64': uid, 'token': token})
            )
            context = {
                'usuario': usuario,
                'activar_url': activar_url,
                'nombre_restaurante': getattr(settings, 'SITE_NAME', 'Restaurante GYZ'),
                'site_name': getattr(settings, 'SITE_NAME', 'Restaurante GYZ'),
                'primary_color': getattr(settings, 'BRAND_PRIMARY_COLOR', '#10b981'),
                'logo_url': getattr(settings, 'BRAND_LOGO_URL', ''),
                'support_email': getattr(settings, 'BRAND_SUPPORT_EMAIL', settings.DEFAULT_FROM_EMAIL),
                'subject': 'Verifica tu cuenta - Restaurante GYZ',
            }
            _enqueue_email(
                to_email=usuario.email,
                subject='Verifica tu cuenta - Restaurante GYZ',
                template='usuarios/emails/verificacion_cuenta.html',
                context=context,
                purpose='verification',
            )
            cache.set(key, True, timeout=THROTTLE_SECONDS)
            messages.success(request, 'Hemos reenviado el correo de verificación.')
            return redirect('usuarios:login')
        except Usuario.DoesNotExist:
            messages.success(request, 'Hemos reenviado el correo de verificación si la cuenta existe.')
            return redirect('usuarios:login')
    # fallback
    return redirect('usuarios:login') 