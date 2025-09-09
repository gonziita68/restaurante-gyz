from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Evento, TipoEvento, MenuEvento, ServicioAdicional, Catering, CotizacionEvento

Usuario = get_user_model()

class SolicitudEventoForm(forms.ModelForm):
    """Formulario para solicitar un evento"""
    
    class Meta:
        model = Evento
        fields = [
            'nombre_evento', 'descripcion', 'fecha_evento', 'hora_inicio', 'hora_fin',
            'tipo_ubicacion', 'direccion_evento', 'instrucciones_ubicacion',
            'numero_invitados', 'categoria', 'notas_especiales', 'alergias_especiales',
            'preferencias_dieteticas'
        ]
        widgets = {
            'fecha_evento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'hora_inicio': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'hora_fin': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'nombre_evento': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Cumpleaños de María'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describe tu evento...'}),
            'direccion_evento': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Dirección completa del evento'}),
            'instrucciones_ubicacion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Instrucciones adicionales para llegar'}),
            'numero_invitados': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'tipo_ubicacion': forms.Select(attrs={'class': 'form-control'}),
            'notas_especiales': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Requerimientos especiales...'}),
            'alergias_especiales': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Alergias alimentarias de los invitados'}),
            'preferencias_dieteticas': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Preferencias dietéticas (vegetariano, vegano, etc.)'}),
        }
    
    def clean_fecha_evento(self):
        fecha = self.cleaned_data['fecha_evento']
        if fecha < timezone.now().date():
            raise ValidationError("La fecha del evento no puede ser en el pasado.")
        
        # Verificar que no sea muy lejano (más de 1 año)
        if fecha > timezone.now().date() + timedelta(days=365):
            raise ValidationError("La fecha del evento no puede ser más de un año en el futuro.")
        
        return fecha
    
    def clean(self):
        cleaned_data = super().clean()
        hora_inicio = cleaned_data.get('hora_inicio')
        hora_fin = cleaned_data.get('hora_fin')
        fecha_evento = cleaned_data.get('fecha_evento')
        
        if hora_inicio and hora_fin:
            if hora_inicio >= hora_fin:
                raise ValidationError("La hora de fin debe ser posterior a la hora de inicio.")
        
        # Verificar disponibilidad básica (solo horario del restaurante)
        if hora_inicio:
            hora_restaurante_inicio = datetime.strptime('08:00', '%H:%M').time()
            hora_restaurante_fin = datetime.strptime('23:00', '%H:%M').time()
            
            if hora_inicio < hora_restaurante_inicio or hora_fin > hora_restaurante_fin:
                raise ValidationError("El horario debe estar dentro del horario del restaurante (8:00 AM - 11:00 PM).")
        
        return cleaned_data

class SeleccionTipoEventoForm(forms.Form):
    """Formulario para seleccionar el tipo de evento"""
    tipo_evento = forms.ModelChoiceField(
        queryset=TipoEvento.objects.filter(activo=True),
        empty_label="Selecciona un tipo de evento",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class SeleccionMenuForm(forms.Form):
    """Formulario para seleccionar el menú del evento"""
    menu_evento = forms.ModelChoiceField(
        queryset=MenuEvento.objects.filter(activo=True),
        required=False,
        empty_label="Sin menú especial",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class ServiciosAdicionalesForm(forms.Form):
    """Formulario para seleccionar servicios adicionales"""
    servicios = forms.ModelMultipleChoiceField(
        queryset=ServicioAdicional.objects.filter(activo=True),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
    )
    decoracion_especial = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describe la decoración especial que deseas...'})
    )
    musica_especial = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    fotografo = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

class CateringForm(forms.ModelForm):
    """Formulario para servicios de catering"""
    
    class Meta:
        model = Catering
        fields = [
            'tipo_catering', 'incluye_servicio_mesa', 'incluye_equipamiento', 
            'incluye_personal', 'numero_meseros', 'numero_chefs',
            'equipamiento_requerido', 'mesas_sillas', 'manteleria', 'vajilla',
            'hora_entrega', 'hora_recogida'
        ]
        widgets = {
            'tipo_catering': forms.Select(attrs={'class': 'form-control'}),
            'hora_entrega': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'hora_recogida': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'numero_meseros': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'numero_chefs': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'equipamiento_requerido': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Equipamiento adicional requerido...'}),
            'incluye_servicio_mesa': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'incluye_equipamiento': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'incluye_personal': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'mesas_sillas': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'manteleria': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'vajilla': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class CotizacionForm(forms.ModelForm):
    """Formulario para crear cotizaciones"""
    
    class Meta:
        model = CotizacionEvento
        fields = ['subtotal', 'descuento', 'total', 'notas_cliente', 'notas_internas']
        widgets = {
            'subtotal': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'descuento': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'total': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'notas_cliente': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'notas_internas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer el campo total de solo lectura
        self.fields['total'].widget.attrs['readonly'] = True

class BusquedaEventosForm(forms.Form):
    """Formulario para buscar eventos"""
    fecha_desde = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    fecha_hasta = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    estado = forms.ChoiceField(
        choices=[('', 'Todos')] + Evento.ESTADOS_EVENTO,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    categoria = forms.ChoiceField(
        choices=[('', 'Todas')] + Evento.TIPOS_EVENTO,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    cliente = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del cliente'})
    )

class FiltroEventosForm(forms.Form):
    """Formulario para filtrar eventos en el dashboard"""
    ESTADO_CHOICES = [('', 'Todos los estados')] + Evento.ESTADOS_EVENTO
    CATEGORIA_CHOICES = [('', 'Todas las categorías')] + Evento.TIPOS_EVENTO
    
    estado = forms.ChoiceField(
        choices=ESTADO_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select', 'onchange': 'this.form.submit()'})
    )
    categoria = forms.ChoiceField(
        choices=CATEGORIA_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select', 'onchange': 'this.form.submit()'})
    )
    fecha = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'onchange': 'this.form.submit()'})
    )

class ActualizarEstadoEventoForm(forms.Form):
    """Formulario para actualizar el estado de un evento"""
    estado = forms.ChoiceField(
        choices=Evento.ESTADOS_EVENTO,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    notas = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Notas sobre el cambio de estado...'})
    )

class PresupuestoEventoForm(forms.Form):
    """Formulario para crear presupuestos detallados"""
    costo_menu = forms.DecimalField(
        max_digits=12, decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )
    costo_servicios = forms.DecimalField(
        max_digits=12, decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )
    costo_decoracion = forms.DecimalField(
        max_digits=12, decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )
    costo_personal = forms.DecimalField(
        max_digits=12, decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )
    costo_equipamiento = forms.DecimalField(
        max_digits=12, decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )
    costo_transporte = forms.DecimalField(
        max_digits=12, decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )
    descuento = forms.DecimalField(
        max_digits=12, decimal_places=2, required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )
    notas = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Notas adicionales sobre el presupuesto...'})
    )
