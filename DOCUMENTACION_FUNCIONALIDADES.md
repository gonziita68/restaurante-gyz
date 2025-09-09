# 🍽️ DOCUMENTACIÓN COMPLETA DEL SISTEMA DE RESTAURANTE GYZ

## 📋 ÍNDICE
1. [Sistema de Usuarios](#sistema-de-usuarios)
2. [Sistema de Menú](#sistema-de-menú)
3. [Sistema de Pedidos](#sistema-de-pedidos)
4. [Sistema de Reservas](#sistema-de-reservas)
5. [Sistema de Pagos](#sistema-de-pagos)
6. [Sistema de Inventario](#sistema-de-inventario)
7. [Sistema de Empleados](#sistema-de-empleados)
8. [Configuración del Sistema](#configuración-del-sistema)

---

## 👥 SISTEMA DE USUARIOS

### **Funcionalidades Principales**

#### 1. **Registro de Usuario**
- **¿Qué hace?** Permite a nuevos clientes crear una cuenta en el sistema
- **Cómo funciona:** 
  - Accede a `/registro/`
  - Completa formulario con: nombre, email, contraseña, teléfono, dirección
  - Sistema valida datos y crea cuenta
  - Envía email de confirmación
- **URL:** `/registro/`
- **Permisos:** Público

#### 2. **Inicio de Sesión**
- **¿Qué hace?** Autentica usuarios existentes
- **Cómo funciona:**
  - Accede a `/login/`
  - Ingresa email/username y contraseña
  - Sistema valida credenciales
  - Redirige al dashboard o página solicitada
- **URL:** `/login/`
- **Permisos:** Público

#### 3. **Perfil de Usuario**
- **¿Qué hace?** Permite ver y editar información personal
- **Cómo funciona:**
  - Accede a `/perfil/` (requiere login)
  - Visualiza información actual
  - Edita datos personales, dirección, teléfono
  - Cambia contraseña
- **URL:** `/perfil/`
- **Permisos:** Usuario autenticado

#### 4. **Recuperación de Contraseña**
- **¿Qué hace?** Permite recuperar acceso a la cuenta
- **Cómo funciona:**
  - Accede a `/password-reset/`
  - Ingresa email registrado
  - Sistema envía link de recuperación
  - Usuario establece nueva contraseña
- **URL:** `/password-reset/`
- **Permisos:** Público

#### 5. **Cerrar Sesión**
- **¿Qué hace?** Cierra la sesión activa del usuario
- **Cómo funciona:**
  - Accede a `/logout/`
  - Sistema cierra sesión
  - Redirige a página principal
- **URL:** `/logout/`
- **Permisos:** Usuario autenticado

---

## 🍽️ SISTEMA DE MENÚ

### **Funcionalidades Principales**

#### 1. **Menú Completo**
- **¿Qué hace?** Muestra todos los platos organizados por categorías
- **Cómo funciona:**
  - Accede a `/menu/`
  - Visualiza categorías (Entrantes, Principales, Postres, Bebidas)
  - Filtra por categoría, precio, características especiales
  - Busca platos por nombre o ingredientes
- **URL:** `/menu/`
- **Permisos:** Público

#### 2. **Detalle de Categoría**
- **¿Qué hace?** Muestra todos los platos de una categoría específica
- **Cómo funciona:**
  - Accede a `/menu/categoria/<id>/`
  - Visualiza platos de la categoría seleccionada
  - Filtra por precio, disponibilidad, características
- **URL:** `/menu/categoria/<id>/`
- **Permisos:** Público

#### 3. **Detalle de Plato**
- **¿Qué hace?** Muestra información completa de un plato específico
- **Cómo funciona:**
  - Accede a `/menu/plato/<id>/`
  - Visualiza: descripción, ingredientes, precio, alergenos
  - Ve reseñas y calificaciones de otros clientes
  - Agrega al carrito con personalizaciones
  - Deja reseña personal
- **URL:** `/menu/plato/<id>/`
- **Permisos:** Público (ver), Usuario autenticado (reseñas)

#### 4. **Búsqueda de Platos**
- **¿Qué hace?** Permite encontrar platos por criterios específicos
- **Cómo funciona:**
  - Accede a `/menu/buscar/`
  - Busca por nombre, ingredientes, categoría
  - Filtra por precio, características (vegetariano, sin gluten, picante)
  - Ordena por relevancia, precio, calificación
- **URL:** `/menu/buscar/`
- **Permisos:** Público

#### 5. **Sistema de Reseñas**
- **¿Qué hace?** Permite a clientes calificar y comentar platos
- **Cómo funciona:**
  - En detalle de plato, sección "Reseñas"
  - Califica con 1-5 estrellas
  - Escribe comentario (máximo 500 caracteres)
  - Edita o elimina reseñas propias
  - Ve respuestas del restaurante
- **URL:** `/menu/plato/<id>/resena/`
- **Permisos:** Usuario autenticado

#### 6. **Dashboard de Reseñas (Staff)**
- **¿Qué hace?** Permite al personal gestionar todas las reseñas
- **Cómo funciona:**
  - Accede a `/menu/dashboard/resenas/`
  - Visualiza todas las reseñas del sistema
  - Filtra por plato, cliente, calificación, fecha
  - Responde a reseñas de clientes
  - Elimina reseñas inapropiadas
  - Exporta reportes
- **URL:** `/menu/dashboard/resenas/`
- **Permisos:** Staff

#### 7. **API del Menú**
- **¿Qué hace?** Proporciona acceso programático a datos del menú
- **Cómo funciona:**
  - Accede a `/menu/api/`
  - Obtiene datos en formato JSON
  - Incluye: platos, categorías, precios, disponibilidad
- **URL:** `/menu/api/`
- **Permisos:** Público

#### 8. **Verificación de Disponibilidad**
- **¿Qué hace?** Verifica si un plato está disponible en tiempo real
- **Cómo funciona:**
  - Accede a `/menu/api/disponibilidad/<id>/`
  - Retorna estado de disponibilidad
  - Considera horarios, stock, temporadas
- **URL:** `/menu/api/disponibilidad/<id>/`
- **Permisos:** Público

---

## 🛒 SISTEMA DE PEDIDOS

### **Funcionalidades Principales**

#### 1. **Carrito de Compras**
- **¿Qué hace?** Permite agregar platos antes de realizar el pedido
- **Cómo funciona:**
  - Accede a `/pedidos/carrito/`
  - Agrega platos desde el menú
  - Especifica cantidad y personalizaciones
  - Ve subtotal, impuestos y total
  - Modifica o elimina items
- **URL:** `/pedidos/carrito/`
- **Permisos:** Usuario autenticado

#### 2. **Agregar al Carrito**
- **¿Qué hace?** Añade un plato específico al carrito
- **Cómo funciona:**
  - Desde detalle de plato, botón "Agregar al Carrito"
  - Selecciona cantidad y opciones de personalización
  - Especifica instrucciones especiales
  - Confirma agregado
- **URL:** `/pedidos/carrito/agregar/`
- **Permisos:** Usuario autenticado

#### 3. **Actualizar Carrito**
- **¿Qué hace?** Modifica cantidad o personalizaciones de items
- **Cómo funciona:**
  - En carrito, modifica cantidad
  - Cambia opciones de personalización
  - Actualiza instrucciones especiales
  - Recalcula totales automáticamente
- **URL:** `/pedidos/carrito/actualizar/<id>/`
- **Permisos:** Usuario autenticado

#### 4. **Eliminar del Carrito**
- **¿Qué hace?** Remueve items específicos del carrito
- **Cómo funciona:**
  - En carrito, botón "Eliminar" en cada item
  - Confirma eliminación
  - Recalcula totales
- **URL:** `/pedidos/carrito/eliminar/<id>/`
- **Permisos:** Usuario autenticado

#### 5. **Limpiar Carrito**
- **¿Qué hace?** Vacía completamente el carrito
- **Cómo funciona:**
  - En carrito, botón "Limpiar Carrito"
  - Confirma acción
  - Elimina todos los items
- **URL:** `/pedidos/carrito/limpiar/`
- **Permisos:** Usuario autenticado

#### 6. **Checkout**
- **¿Qué hace?** Proceso final de confirmación del pedido
- **Cómo funciona:**
  - Accede a `/pedidos/checkout/`
  - Revisa items del carrito
  - Confirma dirección de entrega
  - Selecciona método de pago
  - Confirma pedido
- **URL:** `/pedidos/checkout/`
- **Permisos:** Usuario autenticado

#### 7. **Mis Pedidos**
- **¿Qué hace?** Historial de todos los pedidos realizados
- **Cómo funciona:**
  - Accede a `/pedidos/mis-pedidos/`
  - Ve lista de pedidos con estados
  - Filtra por fecha, estado, tipo
  - Accede a detalles de cada pedido
- **URL:** `/pedidos/mis-pedidos/`
- **Permisos:** Usuario autenticado

#### 8. **Detalle de Pedido**
- **¿Qué hace?** Información completa de un pedido específico
- **Cómo funciona:**
  - Accede a `/pedidos/pedido/<id>/`
  - Ve: items, precios, estado, fechas
  - Rastrea estado de preparación
  - Cancela pedido (si es posible)
- **URL:** `/pedidos/pedido/<id>/`
- **Permisos:** Usuario autenticado (propio pedido)

#### 9. **Cancelar Pedido**
- **¿Qué hace?** Permite cancelar pedidos pendientes
- **Cómo funciona:**
  - En detalle de pedido, botón "Cancelar"
  - Confirma cancelación
  - Sistema actualiza estado
  - Notifica al personal
- **URL:** `/pedidos/pedido/<id>/cancelar/`
- **Permisos:** Usuario autenticado (propio pedido)

#### 10. **Seguimiento Público**
- **¿Qué hace?** Permite rastrear pedidos sin login
- **Cómo funciona:**
  - Accede a `/pedidos/seguimiento/<numero>/`
  - Ingresa número de pedido
  - Ve estado actual y estimado de entrega
- **URL:** `/pedidos/seguimiento/<numero>/`
- **Permisos:** Público

---

## 🗓️ SISTEMA DE RESERVAS

### **Funcionalidades Principales**

#### 1. **Disponibilidad de Mesas**
- **¿Qué hace?** Muestra mesas disponibles para reservar
- **Cómo funciona:**
  - Accede a `/reservas/`
  - Selecciona fecha y hora
  - Ve mesas disponibles por capacidad
  - Filtra por ubicación (interior, terraza, ventana)
- **URL:** `/reservas/`
- **Permisos:** Público

#### 2. **Búsqueda de Disponibilidad**
- **¿Qué hace?** API para verificar disponibilidad en tiempo real
- **Cómo funciona:**
  - Accede a `/reservas/api/buscar-disponibilidad/`
  - Envía parámetros: fecha, hora, comensales
  - Retorna mesas disponibles
- **URL:** `/reservas/api/buscar-disponibilidad/`
- **Permisos:** Público

#### 3. **Horarios Disponibles**
- **¿Qué hace?** Muestra horarios disponibles para una fecha
- **Cómo funciona:**
  - Accede a `/reservas/api/horarios-disponibles/`
  - Envía fecha y número de comensales
  - Retorna horarios con disponibilidad
- **URL:** `/reservas/api/horarios-disponibles/`
- **Permisos:** Público

#### 4. **Crear Reserva**
- **¿Qué hace?** Permite crear una nueva reserva
- **Cómo funciona:**
  - Accede a `/reservas/crear/`
  - Selecciona fecha, hora, mesa
  - Especifica número de comensales
  - Añade información de contacto
  - Confirma reserva
- **URL:** `/reservas/crear/`
- **Permisos:** Público

#### 5. **Mis Reservas**
- **¿Qué hace?** Historial de reservas del usuario
- **Cómo funciona:**
  - Accede a `/reservas/mis-reservas/`
  - Ve lista de reservas con estados
  - Filtra por fecha, estado
  - Accede a detalles de cada reserva
- **URL:** `/reservas/mis-reservas/`
- **Permisos:** Usuario autenticado

#### 6. **Detalle de Reserva**
- **¿Qué hace?** Información completa de una reserva
- **Cómo funciona:**
  - Accede a `/reservas/reserva/<id>/`
  - Ve: mesa, fecha, hora, comensales
  - Estado actual y confirmación
  - Cancela reserva (si es posible)
- **URL:** `/reservas/reserva/<id>/`
- **Permisos:** Usuario autenticado (propia reserva)

#### 7. **Cancelar Reserva**
- **¿Qué hace?** Permite cancelar reservas futuras
- **Cómo funciona:**
  - En detalle de reserva, botón "Cancelar"
  - Confirma cancelación
  - Sistema libera mesa
  - Envía confirmación
- **URL:** `/reservas/reserva/<id>/cancelar/`
- **Permisos:** Usuario autenticado (propia reserva)

#### 8. **Consultar Reserva**
- **¿Qué hace?** Permite verificar reservas sin login
- **Cómo funciona:**
  - Accede a `/reservas/consultar/`
  - Ingresa código de reserva
  - Ve estado y detalles
- **URL:** `/reservas/consultar/`
- **Permisos:** Público

#### 9. **Calendario de Reservas (Staff)**
- **¿Qué hace?** Vista de calendario para gestión de reservas
- **Cómo funciona:**
  - Accede a `/reservas/calendario/`
  - Ve todas las reservas en formato calendario
  - Gestiona confirmaciones y cambios
  - Bloquea mesas para eventos
- **URL:** `/reservas/calendario/`
- **Permisos:** Staff

---

## 💳 SISTEMA DE PAGOS

### **Funcionalidades Principales**

#### 1. **Procesar Pago de Pedido**
- **¿Qué hace?** Gestiona el pago de un pedido específico
- **Cómo funciona:**
  - Accede a `/pagos/pedido/<id>/`
  - Selecciona método de pago
  - Procesa pago (Stripe, efectivo, transferencia)
  - Confirma transacción
- **URL:** `/pagos/pedido/<id>/`
- **Permisos:** Usuario autenticado (propio pedido)

#### 2. **Procesar Pago de Reserva**
- **¿Qué hace?** Gestiona el pago de una reserva
- **Cómo funciona:**
  - Accede a `/pagos/reserva/<id>/`
  - Paga depósito o reserva completa
  - Confirma transacción
- **URL:** `/pagos/reserva/<id>/`
- **Permisos:** Usuario autenticado (propia reserva)

#### 3. **Crear Pago**
- **¿Qué hace?** Permite crear pagos independientes
- **Cómo funciona:**
  - Accede a `/pagos/crear/`
  - Especifica monto y concepto
  - Selecciona método de pago
  - Procesa transacción
- **URL:** `/pagos/crear/`
- **Permisos:** Usuario autenticado

#### 4. **Confirmar Pago en Efectivo**
- **¿Qué hace?** Confirma pagos realizados en efectivo
- **Cómo funciona:**
  - Accede a `/pagos/confirmar-efectivo/<id>/`
  - Confirma recepción del pago
  - Actualiza estado de la transacción
- **URL:** `/pagos/confirmar-efectivo/<id>/`
- **Permisos:** Staff

#### 5. **Webhook de Stripe**
- **¿Qué hace?** Recibe notificaciones automáticas de Stripe
- **Cómo funciona:**
  - Stripe envía notificaciones a `/pagos/webhook/stripe/`
  - Sistema procesa automáticamente
  - Actualiza estados de pagos
- **URL:** `/pagos/webhook/stripe/`
- **Permisos:** Stripe (automático)

#### 6. **Historial de Pagos**
- **¿Qué hace?** Muestra historial de transacciones
- **Cómo funciona:**
  - Accede a `/pagos/historial/`
  - Ve todos los pagos realizados
  - Filtra por fecha, método, estado
  - Accede a detalles de cada transacción
- **URL:** `/pagos/historial/`
- **Permisos:** Usuario autenticado

#### 7. **Estado de Pago**
- **¿Qué hace?** Permite verificar estado de un pago específico
- **Cómo funciona:**
  - Accede a `/pagos/estado/<numero>/`
  - Ingresa número de pago
  - Ve estado actual y detalles
- **URL:** `/pagos/estado/<numero>/`
- **Permisos:** Público

---

## 📦 SISTEMA DE INVENTARIO

### **Funcionalidades Principales**

#### 1. **Dashboard de Inventario**
- **¿Qué hace?** Vista general del estado del inventario
- **Cómo funciona:**
  - Accede a `/inventario/`
  - Ve resumen de stock, alertas, movimientos
  - Gráficos de tendencias
  - Acceso rápido a funciones principales
- **URL:** `/inventario/`
- **Permisos:** Staff

#### 2. **Lista de Productos**
- **¿Qué hace?** Muestra todos los productos en inventario
- **Cómo funciona:**
  - Accede a `/inventario/productos/`
  - Ve productos con stock actual
  - Filtra por categoría, proveedor, estado
  - Busca por nombre o código
- **URL:** `/inventario/productos/`
- **Permisos:** Staff

#### 3. **Detalle de Producto**
- **¿Qué hace?** Información completa de un producto
- **Cómo funciona:**
  - Accede a `/inventario/productos/<id>/`
  - Ve: stock, costos, proveedor, movimientos
  - Historial de precios
  - Alertas activas
- **URL:** `/inventario/productos/<id>/`
- **Permisos:** Staff

#### 4. **Registrar Movimiento**
- **¿Qué hace?** Registra entradas/salidas de inventario
- **Cómo funciona:**
  - Accede a `/inventario/productos/movimiento/`
  - Selecciona producto y tipo de movimiento
  - Especifica cantidad y motivo
  - Confirma registro
- **URL:** `/inventario/productos/movimiento/`
- **Permisos:** Staff

#### 5. **Órdenes de Compra**
- **¿Qué hace?** Gestiona compras a proveedores
- **Cómo funciona:**
  - Accede a `/inventario/ordenes/`
  - Crea nuevas órdenes
  - Gestiona estados (borrador, enviada, confirmada)
  - Recibe mercadería
- **URL:** `/inventario/ordenes/`
- **Permisos:** Staff

#### 6. **Detalle de Orden**
- **¿Qué hace?** Información completa de una orden de compra
- **Cómo funciona:**
  - Accede a `/inventario/ordenes/<id>/`
  - Ve: items, proveedor, fechas, montos
  - Gestiona estados
  - Confirma recepción
- **URL:** `/inventario/ordenes/<id>/`
- **Permisos:** Staff

#### 7. **Alertas de Inventario**
- **¿Qué hace?** Sistema automático de alertas
- **Cómo funciona:**
  - Accede a `/inventario/alertas/`
  - Ve alertas activas: stock bajo, vencimientos
  - Resuelve alertas
  - Configura umbrales
- **URL:** `/inventario/alertas/`
- **Permisos:** Staff

#### 8. **Resolver Alerta**
- **¿Qué hace?** Marca alertas como resueltas
- **Cómo funciona:**
  - En alertas, botón "Resolver"
  - Especifica acción tomada
  - Marca como resuelta
- **URL:** `/inventario/alertas/<id>/resolver/`
- **Permisos:** Staff

#### 9. **Reporte de Inventario**
- **¿Qué hace?** Genera reportes del estado del inventario
- **Cómo funciona:**
  - Accede a `/inventario/reporte/`
  - Selecciona tipo de reporte
  - Define parámetros (fechas, categorías)
  - Genera y descarga reporte
- **URL:** `/inventario/reporte/`
- **Permisos:** Staff

#### 10. **Procesar Consumos**
- **¿Qué hace?** Actualiza inventario basado en pedidos
- **Cómo funciona:**
  - Accede a `/inventario/procesar-consumos/`
  - Sistema calcula ingredientes usados
  - Actualiza stock automáticamente
  - Genera alertas si es necesario
- **URL:** `/inventario/procesar-consumos/`
- **Permisos:** Staff

#### 11. **API de Productos**
- **¿Qué hace?** Proporciona datos de inventario vía API
- **Cómo funciona:**
  - Accede a `/inventario/api/productos/`
  - Retorna productos disponibles
  - Incluye stock y precios
- **URL:** `/inventario/api/productos/`
- **Permisos:** Staff

---

## 👨‍💼 SISTEMA DE EMPLEADOS

### **Funcionalidades Principales**

#### 1. **Dashboard de Empleados**
- **¿Qué hace?** Vista general del personal y estadísticas
- **Cómo funciona:**
  - Accede a `/empleados/`
  - Ve resumen de empleados, asistencia, evaluaciones
  - Gráficos de rendimiento
  - Acceso rápido a funciones
- **URL:** `/empleados/`
- **Permisos:** Staff

#### 2. **Lista de Empleados**
- **¿Qué hace?** Muestra todos los empleados del sistema
- **Cómo funciona:**
  - Accede a `/empleados/lista/`
  - Ve empleados con información básica
  - Filtra por departamento, estado, puesto
  - Busca por nombre o número
- **URL:** `/empleados/lista/`
- **Permisos:** Staff

#### 3. **Detalle de Empleado**
- **¿Qué hace?** Información completa de un empleado
- **Cómo funciona:**
  - Accede a `/empleados/empleado/<id>/`
  - Ve: datos personales, laborales, salario
  - Historial de asistencia y evaluaciones
  - Horarios y capacitaciones
- **URL:** `/empleados/empleado/<id>/`
- **Permisos:** Staff

#### 4. **Asistencia Diaria**
- **¿Qué hace?** Gestiona registro de entrada/salida
- **Cómo funciona:**
  - Accede a `/empleados/asistencia/`
  - Ve registro del día actual
  - Marca entradas y salidas
  - Gestiona justificaciones
- **URL:** `/empleados/asistencia/`
- **Permisos:** Staff

#### 5. **Marcar Asistencia**
- **¿Qué hace?** Registra entrada/salida de empleados
- **Cómo funciona:**
  - Accede a `/empleados/asistencia/marcar/`
  - Selecciona empleado y tipo de registro
  - Confirma hora y observaciones
- **URL:** `/empleados/asistencia/marcar/`
- **Permisos:** Staff

#### 6. **Evaluaciones Pendientes**
- **¿Qué hace?** Gestiona evaluaciones de desempeño
- **Cómo funciona:**
  - Accede a `/empleados/evaluaciones-pendientes/`
  - Ve empleados que requieren evaluación
  - Crea nuevas evaluaciones
  - Gestiona evaluaciones existentes
- **URL:** `/empleados/evaluaciones-pendientes/`
- **Permisos:** Staff

#### 7. **Capacitaciones**
- **¿Qué hace?** Gestiona entrenamientos del personal
- **Cómo funciona:**
  - Accede a `/empleados/capacitaciones/`
  - Crea nuevas capacitaciones
  - Inscribe empleados
  - Registra asistencia y resultados
- **URL:** `/empleados/capacitaciones/`
- **Permisos:** Staff

#### 8. **Reporte de Nómina**
- **¿Qué hace?** Genera reportes de salarios y beneficios
- **Cómo funciona:**
  - Accede a `/empleados/nomina/`
  - Selecciona período y empleados
  - Genera reporte con desgloses
  - Descarga en diferentes formatos
- **URL:** `/empleados/nomina/`
- **Permisos:** Staff

#### 9. **Mi Perfil (Empleado)**
- **¿Qué hace?** Permite al empleado ver su información
- **Cómo funciona:**
  - Accede a `/empleados/mi-perfil/`
  - Ve datos personales y laborales
  - Historial de asistencia
  - Evaluaciones recibidas
- **URL:** `/empleados/mi-perfil/`
- **Permisos:** Empleado (propio perfil)

#### 10. **API de Búsqueda**
- **¿Qué hace?** Proporciona búsqueda de empleados vía API
- **Cómo funciona:**
  - Accede a `/empleados/api/buscar/`
  - Envía parámetros de búsqueda
  - Retorna empleados que coinciden
- **URL:** `/empleados/api/buscar/`
- **Permisos:** Staff

---

## ⚙️ CONFIGURACIÓN DEL SISTEMA

### **Configuración General**

#### 1. **Configuración de Correo**
- **Archivo:** `configuracion_correo.txt`
- **¿Qué hace?** Configura envío de emails automáticos
- **Configuración:**
  - Servidor SMTP
  - Credenciales de autenticación
  - Plantillas de email
  - Configuración de seguridad

#### 2. **Base de Datos**
- **Archivo:** `db.sqlite3`
- **¿Qué hace?** Almacena todos los datos del sistema
- **Características:**
  - SQLite para desarrollo
  - Migraciones automáticas
  - Backup automático

#### 3. **Dependencias**
- **Archivo:** `requirements.txt`
- **¿Qué hace?** Lista todas las librerías Python necesarias
- **Principales:**
  - Django 5.2.4 (Framework web)
  - Pillow (Procesamiento de imágenes)
  - Stripe (Procesamiento de pagos)
  - Django REST Framework (APIs)

---

## 🚀 CÓMO HACER FUNCIONAR EL SISTEMA

### **1. Instalación Inicial**

```bash
# Clonar el proyecto
git clone <url-del-repositorio>
cd restaurante-gyz

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar base de datos
python manage.py makemigrations
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Poblar datos iniciales
python manage.py poblar_menu
python manage.py poblar_empleados
python manage.py poblar_inventario
python manage.py configurar_reservas
python manage.py configurar_pagos

# Ejecutar servidor
python manage.py runserver
```

### **2. Configuración de Variables de Entorno**

Crear archivo `.env` en la raíz del proyecto:

```env
SECRET_KEY=tu_clave_secreta_aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
STRIPE_PUBLIC_KEY=tu_clave_publica_stripe
STRIPE_SECRET_KEY=tu_clave_secreta_stripe
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu_email@gmail.com
EMAIL_HOST_PASSWORD=tu_password_aplicacion
```

### **3. Configuración de Stripe (Pagos)**

1. Crear cuenta en [Stripe.com](https://stripe.com)
2. Obtener claves API (pública y secreta)
3. Configurar webhooks para notificaciones automáticas
4. Agregar claves al archivo `.env`

### **4. Configuración de Correo**

1. Habilitar autenticación de 2 factores en Gmail
2. Generar contraseña de aplicación
3. Configurar en archivo `.env`
4. Probar envío de emails

### **5. Acceso al Sistema**

- **URL Principal:** `http://localhost:8000/`
- **Admin Django:** `http://localhost:8000/admin/`
- **API del Menú:** `http://localhost:8000/menu/api/`

### **6. Usuarios por Defecto**

- **Superusuario:** Creado durante instalación
- **Empleados de Prueba:** Creados con `poblar_empleados`
- **Menú de Prueba:** Creado con `poblar_menu`

---

## 🔧 MANTENIMIENTO Y ACTUALIZACIONES

### **Comandos de Mantenimiento**

```bash
# Actualizar dependencias
pip install --upgrade -r requirements.txt

# Hacer backup de base de datos
python manage.py dumpdata > backup.json

# Restaurar backup
python manage.py loaddata backup.json

# Limpiar archivos media obsoletos
python manage.py collectstatic --clear

# Verificar integridad del sistema
python manage.py check
```

### **Monitoreo del Sistema**

- **Logs:** Revisar archivos de log en `logs/`
- **Base de Datos:** Monitorear tamaño y rendimiento
- **Archivos Media:** Limpiar imágenes obsoletas
- **Backups:** Programar backups automáticos

---

## 📱 CARACTERÍSTICAS TÉCNICAS

### **Frontend**
- **Framework:** Bootstrap 5 (Responsive)
- **JavaScript:** Vanilla JS + Fetch API
- **Iconos:** FontAwesome
- **Templates:** Django Templates

### **Backend**
- **Framework:** Django 5.2.4
- **Base de Datos:** SQLite (desarrollo) / PostgreSQL (producción)
- **APIs:** Django REST Framework + Django Ninja
- **Autenticación:** Sistema personalizado de usuarios

### **Seguridad**
- **CSRF Protection:** Activado en todos los formularios
- **Autenticación:** Sistema de login/logout seguro
- **Permisos:** Control granular por usuario y grupo
- **Validación:** Validación en frontend y backend

### **Rendimiento**
- **Caché:** Sistema de caché integrado
- **Optimización de Imágenes:** Thumbnails automáticos
- **Lazy Loading:** Carga diferida de contenido
- **Paginación:** Paginación en listas largas

---

## 🆘 SOLUCIÓN DE PROBLEMAS COMUNES

### **Problema: Error de migraciones**
```bash
# Solución:
python manage.py makemigrations --merge
python manage.py migrate
```

### **Problema: Imágenes no se muestran**
```bash
# Solución:
python manage.py collectstatic
# Verificar configuración MEDIA_URL y MEDIA_ROOT
```

### **Problema: Emails no se envían**
```bash
# Solución:
# Verificar configuración SMTP en .env
# Probar con credenciales correctas
# Verificar firewall/antivirus
```

### **Problema: Pagos de Stripe fallan**
```bash
# Solución:
# Verificar claves API en .env
# Configurar webhooks correctamente
# Verificar modo test/producción
```

---

## 📞 SOPORTE Y CONTACTO

Para soporte técnico o consultas sobre el sistema:

- **Documentación:** Este archivo
- **Issues:** Repositorio de GitHub
- **Email:** [tu-email@dominio.com]
- **Teléfono:** [tu-numero]

---

*Documentación generada automáticamente - Sistema de Restaurante GYZ v1.0*
