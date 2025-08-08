from ninja import Schema
from typing import Optional
from datetime import date

class UsuarioRegistroSchema(Schema):
    """Schema para registro de usuarios"""
    username: str
    email: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    telefono: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    direccion: Optional[str] = None

class UsuarioLoginSchema(Schema):
    """Schema para login de usuarios"""
    username: str
    password: str

class UsuarioResponseSchema(Schema):
    """Schema para respuesta de usuario"""
    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    telefono: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    direccion: Optional[str] = None
    es_activo: bool
    fecha_registro: str
    ultimo_acceso: Optional[str] = None

class UsuarioActualizarSchema(Schema):
    """Schema para actualizar usuario"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    direccion: Optional[str] = None

class CambioPasswordSchema(Schema):
    """Schema para cambio de contraseña"""
    password_actual: str
    password_nuevo: str

class RespuestaAuthSchema(Schema):
    """Schema para respuesta de autenticación"""
    success: bool
    message: str
    usuario: Optional[UsuarioResponseSchema] = None
    token: Optional[str] = None