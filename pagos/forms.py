from django import forms
from django.core.validators import RegexValidator

class PagoTarjetaForm(forms.Form):
    """Formulario para pago con tarjeta de crédito"""
    
    # Número de tarjeta
    numero_tarjeta = forms.CharField(
        label='Número de Tarjeta',
        max_length=19,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '1234 5678 9012 3456',
            'data-mask': '0000 0000 0000 0000',
            'autocomplete': 'cc-number'
        }),
        validators=[
            RegexValidator(
                regex=r'^[\d\s-]+$',
                message='Solo se permiten números, espacios y guiones'
            )
        ]
    )
    
    # Nombre del titular
    nombre_titular = forms.CharField(
        label='Nombre del Titular',
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'NOMBRE APELLIDO',
            'autocomplete': 'cc-name'
        })
    )
    
    # Fecha de vencimiento
    fecha_vencimiento = forms.CharField(
        label='Fecha de Vencimiento',
        max_length=5,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'MM/YY',
            'data-mask': '00/00',
            'autocomplete': 'cc-exp'
        }),
        validators=[
            RegexValidator(
                regex=r'^\d{2}/\d{2}$',
                message='Formato inválido. Use MM/YY'
            )
        ]
    )
    
    # CVV
    cvv = forms.CharField(
        label='CVV',
        max_length=4,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '123',
            'data-mask': '0000',
            'autocomplete': 'cc-csc'
        }),
        validators=[
            RegexValidator(
                regex=r'^\d{3,4}$',
                message='CVV debe tener 3 o 4 dígitos'
            )
        ]
    )
    
    # Email para envío de comprobante
    email = forms.EmailField(
        label='Email para comprobante',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'tu@email.com',
            'autocomplete': 'email'
        })
    )
    
    # Monto (oculto, se establece dinámicamente)
    monto = forms.DecimalField(
        widget=forms.HiddenInput()
    )
    
    # Descripción (oculta, se establece dinámicamente)
    descripcion = forms.CharField(
        widget=forms.HiddenInput()
    )
    
    def clean_numero_tarjeta(self):
        """Limpia y valida el número de tarjeta"""
        numero = self.cleaned_data['numero_tarjeta']
        # Eliminar espacios y guiones
        numero = numero.replace(' ', '').replace('-', '')
        
        if len(numero) < 13 or len(numero) > 19:
            raise forms.ValidationError('Número de tarjeta inválido')
        
        if not numero.isdigit():
            raise forms.ValidationError('El número de tarjeta solo debe contener dígitos')
        
        return numero
    
    def clean_fecha_vencimiento(self):
        """Valida la fecha de vencimiento"""
        fecha = self.cleaned_data['fecha_vencimiento']
        
        try:
            mes, año = fecha.split('/')
            mes = int(mes)
            año = int(año)
            
            if mes < 1 or mes > 12:
                raise forms.ValidationError('Mes inválido')
            
            # Convertir año de 2 dígitos a 4 dígitos
            if año < 100:
                año += 2000
            
            # Verificar que no esté vencida
            from datetime import datetime
            año_actual = datetime.now().year
            mes_actual = datetime.now().month
            
            if año < año_actual:
                raise forms.ValidationError('Tarjeta vencida')
            elif año == año_actual and mes < mes_actual:
                raise forms.ValidationError('Tarjeta vencida')
            
            return fecha
            
        except (ValueError, IndexError):
            raise forms.ValidationError('Formato de fecha inválido')
    
    def clean(self):
        """Validación adicional del formulario completo"""
        cleaned_data = super().clean()
        
        # Validar que el monto sea positivo
        monto = cleaned_data.get('monto')
        if monto and monto <= 0:
            raise forms.ValidationError('El monto debe ser mayor a 0')
        
        return cleaned_data
