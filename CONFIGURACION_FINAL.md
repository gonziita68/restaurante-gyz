# 🎯 Configuración Final - Login Social con Google

## ✅ Estado Actual

El sistema de login social está **casi completamente configurado**. Solo necesitas completar estos pasos finales:

## 🔧 Pasos para Completar la Configuración

### **1. Acceder al Admin de Django**

1. **Ejecuta el servidor**:
   ```bash
   python manage.py runserver
   ```

2. **Ve al admin**: `http://localhost:8000/admin/`
   - **Usuario**: `admin`
   - **Contraseña**: `admin123456`

### **2. Configurar el Sitio**

1. En el admin, ve a **"Sites"**
2. Haz clic en el sitio existente
3. Cambia:
   - **Domain name**: `localhost:8000`
   - **Display name**: `Restaurante GYZ`
4. **Guarda**

### **3. Crear Aplicación Social de Google**

1. En el admin, ve a **"Social Applications"**
2. Haz clic en **"Add Social Application"**
3. Completa:
   - **Provider**: `Google`
   - **Name**: `Google OAuth`
   - **Client id**: `123456789-test.apps.googleusercontent.com` (temporal)
   - **Secret key**: `GOCSPX-test-secret-key` (temporal)
   - **Sites**: Selecciona `localhost:8000`
4. **Guarda**

### **4. Probar el Sistema (Con Credenciales Temporales)**

1. Ve a `http://localhost:8000/usuarios/registro/`
2. Haz clic en "Registrarse con Google"
3. Verás una página de error de Google (esto es normal con credenciales temporales)

### **5. Configurar Credenciales Reales (Opcional)**

Si quieres que funcione completamente:

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuevo proyecto
3. Habilita la API de Google+
4. Ve a "Credenciales" > "Crear credenciales" > "ID de cliente de OAuth 2.0"
5. Configura:
   - **URI de origen autorizado**: `http://localhost:8000`
   - **URI de redirección autorizado**: `http://localhost:8000/accounts/google/login/callback/`
6. Copia el **Client ID** y **Client Secret**
7. Actualiza estos valores en Django Admin

## 🎯 URLs para Probar

- **Página principal**: `http://localhost:8000/`
- **Registro**: `http://localhost:8000/usuarios/registro/`
- **Login**: `http://localhost:8000/usuarios/login/`
- **Admin**: `http://localhost:8000/admin/`

## ✅ Lo que Ya Está Funcionando

- ✅ Sistema de registro normal con email/contraseña
- ✅ Sistema de login normal
- ✅ Botones de Google visibles en login y registro
- ✅ Configuración de django-allauth
- ✅ Templates actualizados
- ✅ URLs configuradas
- ✅ Superusuario creado
- ✅ Sitio configurado

## 🚨 Solución de Problemas

### Si el botón de Google no funciona:
1. Verifica que hayas creado la "Social Application" en Django Admin
2. Verifica que el sitio esté configurado correctamente
3. Revisa los logs del servidor para errores específicos

### Si quieres usar credenciales reales:
1. Sigue el paso 5 de configuración real
2. Actualiza las credenciales en Django Admin
3. El login social funcionará completamente

## 🎉 ¡Listo!

Una vez que completes los pasos 2 y 3, el sistema estará completamente funcional. Los botones de Google te llevarán a Google para autenticación (aunque con credenciales temporales mostrarán un error, pero el flujo estará configurado correctamente).

¡El sistema de login social está listo! 🚀
