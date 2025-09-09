# Configuración de Google OAuth para Login Social

## Pasos para configurar Google OAuth

### 1. Crear un proyecto en Google Cloud Console

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuevo proyecto o selecciona uno existente
3. Habilita la API de Google+ (si no está habilitada)

### 2. Configurar las credenciales OAuth 2.0

1. En el menú lateral, ve a "APIs y servicios" > "Credenciales"
2. Haz clic en "Crear credenciales" > "ID de cliente de OAuth 2.0"
3. Selecciona "Aplicación web" como tipo de aplicación
4. Configura los URIs autorizados:
   - **URI de origen autorizado**: `http://localhost:8000`
   - **URI de redirección autorizado**: `http://localhost:8000/accounts/google/login/callback/`

### 3. Obtener las credenciales

Después de crear las credenciales, obtendrás:
- **ID de cliente**
- **Secreto del cliente**

### 4. Configurar en Django Admin

1. Ejecuta el servidor de desarrollo:
   ```bash
   python manage.py runserver
   ```

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

### 5. Configurar variables de entorno (opcional)

Puedes agregar las credenciales a tu archivo `.env`:

```env
GOOGLE_CLIENT_ID=tu_client_id_aqui
GOOGLE_CLIENT_SECRET=tu_client_secret_aqui
```

### 6. Probar el login social

1. Ve a `http://localhost:8000/usuarios/login/`
2. Haz clic en "Continuar con Google"
3. Deberías ser redirigido a Google para autenticación
4. Después de la autenticación exitosa, serás redirigido de vuelta a tu aplicación

## Notas importantes

- **Para producción**: Cambia los URIs autorizados a tu dominio real
- **Seguridad**: Nunca compartas tus credenciales de cliente
- **HTTPS**: En producción, asegúrate de usar HTTPS para todas las URLs

## Solución de problemas

### Error: "redirect_uri_mismatch"
- Verifica que el URI de redirección en Google Cloud Console coincida exactamente con el de tu aplicación

### Error: "invalid_client"
- Verifica que el ID de cliente y el secreto estén correctamente configurados en Django Admin

### Error: "access_denied"
- El usuario canceló la autenticación o no dio permisos

## URLs disponibles

- Login social: `/usuarios/social-login/`
- Login normal: `/usuarios/login/`
- Registro: `/usuarios/registro/`
- Admin: `/admin/`
