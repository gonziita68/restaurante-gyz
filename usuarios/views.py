from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from .forms import RegistroUsuarioForm, LoginUsuarioForm, PasswordResetForm, SetPasswordForm
from .models import Usuario
from .emails import enviar_correo_registro_exitoso, enviar_correo_recuperacion_password, enviar_correo_password_cambiado, enviar_correo_verificacion_cuenta

def registro_usuario(request):
    """Vista para registro de usuarios con verificación por correo"""
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # El usuario queda inactivo hasta verificar el correo
            user.is_active = False
            user.save()
            # Enviar correo de verificación
            if enviar_correo_verificacion_cuenta(user, request):
                messages.success(request, '¡Registro exitoso! Te enviamos un correo para verificar tu cuenta.')
            else:
                messages.warning(request, 'Tu cuenta fue creada pero no pudimos enviar el correo de verificación. Intenta reenviar desde tu perfil.')
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
        # Aquí puedes agregar lógica para actualizar el perfil
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
                # Por seguridad, mostramos el mismo mensaje aunque el usuario no exista
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
                # Enviar correo de confirmación
                enviar_correo_password_cambiado(usuario)
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
            enviar_correo_registro_exitoso(usuario)
            messages.success(request, 'Tu cuenta ha sido verificada y activada. Ahora puedes iniciar sesión.')
        else:
            messages.info(request, 'Tu cuenta ya estaba verificada.')
        return redirect('usuarios:login')
    else:
        messages.error(request, 'Enlace de verificación inválido o expirado.')
        return redirect('usuarios:login') 