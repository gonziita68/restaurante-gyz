# 🚀 Guía Completa: Configurar Google OAuth 2.0

## Paso 1: Crear Proyecto en Google Cloud Console

1. **Ve a Google Cloud Console**
   - Abre: https://console.cloud.google.com/
   - Inicia sesión con tu cuenta de Google

2. **Crear un nuevo proyecto**
   - Haz clic en el selector de proyectos (arriba a la izquierda)
   - Haz clic en "Nuevo proyecto"
   - Nombre: `Restaurante GYZ OAuth`
   - Haz clic en "Crear"

## Paso 2: Habilitar Google+ API

1. **En el menú lateral, ve a "APIs y servicios" > "Biblioteca"**
2. **Busca "Google+ API"**
3. **Haz clic en "Google+ API"**
4. **Haz clic en "Habilitar"**

## Paso 3: Crear Credenciales OAuth 2.0

1. **Ve a "APIs y servicios" > "Credenciales"**
2. **Haz clic en "Crear credenciales" > "ID de cliente de OAuth 2.0"**
3. **Si es la primera vez, configura la pantalla de consentimiento:**
   - Tipo de usuario: "Externo"
   - Nombre de la aplicación: "Restaurante GYZ"
   - Correo electrónico de soporte: tu email
   - Dominio de la aplicación: `localhost`
   - Haz clic en "Guardar y continuar"
   - En "Alcances", haz clic en "Guardar y continuar"
   - En "Usuarios de prueba", agrega tu email y haz clic en "Guardar y continuar"

4. **Crear el ID de cliente:**
   - Tipo de aplicación: "Aplicación web"
   - Nombre: "Restaurante GYZ Web"
   - **URIs de redirección autorizados:**
     ```
     http://localhost:8000/accounts/google/login/callback/
     http://127.0.0.1:8000/accounts/google/login/callback/
     ```
   - Haz clic en "Crear"

5. **Copia las credenciales:**
   - Se mostrará un modal con tu **ID de cliente** y **Secreto del cliente**
   - **¡GUARDA ESTOS DATOS!** Los necesitarás en el siguiente paso

## Paso 4: Configurar en Django Admin

1. **Ve a tu aplicación Django:**
   ```
   http://localhost:8000/admin/
   ```

2. **Inicia sesión con tu superusuario**

3. **Ve a "Sitios" > "Sitios"**
   - Edita el sitio existente
   - Dominio: `localhost:8000`
   - Nombre: `Restaurante GYZ`
   - Guarda

4. **Ve a "Social Applications" > "Social applications"**
   - Haz clic en "Añadir social application"
   - Provider: `Google`
   - Name: `Google OAuth`
   - **Client id:** [Pega tu ID de cliente de Google]
   - **Secret key:** [Pega tu secreto del cliente de Google]
   - Sites: Mueve `localhost:8000` a "Sitios elegidos"
   - Guarda

## Paso 5: Probar

1. **Ve a tu página de registro:**
   ```
   http://localhost:8000/usuarios/registro/
   ```

2. **Haz clic en "Registrarse con Google"**

3. **Deberías ser redirigido a Google para autorizar**

4. **Después de autorizar, serás redirigido de vuelta a tu aplicación**

## 🔧 Solución de Problemas

### Error: "redirect_uri_mismatch"
- Verifica que las URIs de redirección en Google Cloud Console coincidan exactamente
- Asegúrate de incluir la barra final `/`

### Error: "invalid_client"
- Verifica que el Client ID y Secret estén correctamente copiados en Django Admin
- No debe haber espacios extra

### Error: "access_denied"
- Asegúrate de que tu email esté en la lista de "Usuarios de prueba" en Google Cloud Console

## 📝 Notas Importantes

- **Para producción:** Cambia `localhost:8000` por tu dominio real
- **Seguridad:** Nunca compartas tu Client Secret
- **Límites:** Con cuentas gratuitas de Google Cloud, tienes límites de uso

## 🎯 Verificación Final

Para verificar que todo funciona:

```bash
python diagnostico_google_oauth.py
```

Este script te dirá si la configuración está correcta.
