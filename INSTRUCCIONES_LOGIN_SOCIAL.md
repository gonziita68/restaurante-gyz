# 🚀 Login Social con Google - Restaurante GYZ

## ✅ Estado Actual

El sistema de login social con Google ha sido **implementado exitosamente** en tu proyecto. Ahora puedes:

- ✅ Ver botones de "Continuar con Google" en las páginas de login y registro
- ✅ Acceder a la página dedicada de login social en `/usuarios/social-login/`
- ✅ El sistema está configurado y listo para usar

## 🔧 Configuración Requerida

Para que el login social funcione completamente, necesitas configurar las credenciales de Google OAuth:

### 1. Crear Proyecto en Google Cloud Console

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuevo proyecto o selecciona uno existente
3. Habilita la API de Google+ (si no está habilitada)

### 2. Configurar Credenciales OAuth 2.0

1. En el menú lateral, ve a "APIs y servicios" > "Credenciales"
2. Haz clic en "Crear credenciales" > "ID de cliente de OAuth 2.0"
3. Selecciona "Aplicación web" como tipo de aplicación
4. Configura los URIs autorizados:
   - **URI de origen autorizado**: `http://localhost:8000`
   - **URI de redirección autorizado**: `http://localhost:8000/accounts/google/login/callback/`

### 3. Obtener Credenciales

Después de crear las credenciales, obtendrás:
- **ID de cliente**
- **Secreto del cliente**

### 4. Configurar en Django Admin

1. Ejecuta el servidor: `python manage.py runserver`
2. Ve a `http://localhost:8000/admin/` y accede con tu superusuario
3. En el admin, ve a "Sites" y edita el sitio existente:
   - **Domain name**: `localhost:8000`
   - **Display name**: `Restaurante GYZ`
4. Ve a "Social Applications" y crea una nueva aplicación:
   - **Provider**: `Google`
   - **Name**: `Google OAuth`
   - **Client id**: [Tu ID de cliente de Google]
   - **Secret key**: [Tu secreto del cliente de Google]
   - **Sites**: Selecciona `localhost:8000`

## 🎯 URLs Disponibles

- **Página principal**: `http://localhost:8000/`
- **Login normal**: `http://localhost:8000/usuarios/login/`
- **Registro normal**: `http://localhost:8000/usuarios/registro/`
- **Login social dedicado**: `http://localhost:8000/usuarios/social-login/`
- **Admin**: `http://localhost:8000/admin/`

## 🔍 Cómo Probar

1. **Sin configuración de Google** (actual):
   - Los botones de Google están visibles pero redirigirán a una página de error
   - Esto es normal hasta que configures las credenciales

2. **Con configuración de Google**:
   - Haz clic en "Continuar con Google" en cualquier página de login/registro
   - Serás redirigido a Google para autenticación
   - Después de la autenticación exitosa, volverás a tu aplicación

## 🛠️ Características Implementadas

### ✅ Funcionalidades Completadas

1. **Configuración de django-allauth**
   - Instalación y configuración completa
   - Migraciones aplicadas
   - URLs configuradas

2. **Templates Actualizados**
   - Botones de Google en login y registro
   - Página dedicada de login social
   - Diseño moderno y responsive

3. **Vistas Personalizadas**
   - Manejo de registro social
   - Actualización automática de datos de usuario
   - Redirecciones personalizadas

4. **Configuración de Seguridad**
   - Configuraciones de rate limiting
   - Validaciones de email
   - Manejo de sesiones

### 🔧 Archivos Creados/Modificados

- ✅ `config/settings.py` - Configuración de allauth
- ✅ `config/urls.py` - URLs de allauth
- ✅ `usuarios/social_views.py` - Vistas para login social
- ✅ `usuarios/urls.py` - URLs para login social
- ✅ `usuarios/templates/usuarios/social_login.html` - Template dedicado
- ✅ `usuarios/templates/usuarios/login.html` - Botón de Google agregado
- ✅ `usuarios/templates/usuarios/registro.html` - Botón de Google agregado
- ✅ `setup_site.py` - Script para configurar el sitio
- ✅ `CONFIGURACION_GOOGLE_OAUTH.md` - Documentación de configuración

## 🚨 Solución de Problemas

### Error: "Template error en provider_login_url"
- **Solución**: Ya corregido. Los botones ahora usan URLs directas
- **Estado**: ✅ Resuelto

### Error: "redirect_uri_mismatch"
- **Causa**: URI de redirección incorrecto en Google Cloud Console
- **Solución**: Verifica que coincida exactamente con `http://localhost:8000/accounts/google/login/callback/`

### Error: "invalid_client"
- **Causa**: Credenciales incorrectas en Django Admin
- **Solución**: Verifica ID de cliente y secreto en Social Applications

## 🎉 Próximos Pasos

1. **Configurar Google OAuth** (opcional pero recomendado)
2. **Probar el flujo completo** una vez configurado
3. **Personalizar mensajes y redirecciones** según necesidades
4. **Configurar para producción** cuando esté listo

## 📞 Soporte

Si tienes problemas:
1. Verifica que el servidor esté corriendo: `python manage.py runserver`
2. Revisa los logs del servidor para errores específicos
3. Asegúrate de que todas las migraciones estén aplicadas: `python manage.py migrate`

¡El sistema de login social está listo para usar! 🎊
