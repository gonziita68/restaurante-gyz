from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal
import uuid

User = get_user_model()

class TipoEmpleado(models.TextChoices):
    """Tipos de empleado según su rol"""
    GERENTE = 'gerente', 'Gerente'
    SUBGERENTE = 'subgerente', 'Subgerente'
    CHEF = 'chef', 'Chef'
    COCINERO = 'cocinero', 'Cocinero'
    AYUDANTE_COCINA = 'ayudante_cocina', 'Ayudante de Cocina'
    MESERO = 'mesero', 'Mesero'
    HOSTESS = 'hostess', 'Hostess/Anfitrión'
    BARTENDER = 'bartender', 'Bartender'
    CAJERO = 'cajero', 'Cajero'
    REPARTIDOR = 'repartidor', 'Repartidor'
    LIMPIEZA = 'limpieza', 'Personal de Limpieza'
    SEGURIDAD = 'seguridad', 'Seguridad'
    ADMINISTRACION = 'administracion', 'Administración'

class EstadoEmpleado(models.TextChoices):
    """Estados del empleado"""
    ACTIVO = 'activo', 'Activo'
    INACTIVO = 'inactivo', 'Inactivo'
    VACACIONES = 'vacaciones', 'En Vacaciones'
    LICENCIA = 'licencia', 'Con Licencia'
    SUSPENDIDO = 'suspendido', 'Suspendido'
    DESPEDIDO = 'despedido', 'Despedido'

class TipoContrato(models.TextChoices):
    """Tipos de contrato laboral"""
    TIEMPO_COMPLETO = 'tiempo_completo', 'Tiempo Completo'
    MEDIO_TIEMPO = 'medio_tiempo', 'Medio Tiempo'
    POR_HORAS = 'por_horas', 'Por Horas'
    TEMPORAL = 'temporal', 'Temporal'
    PRACTICANTE = 'practicante', 'Practicante'
    FREELANCE = 'freelance', 'Freelance'

class TipoTurno(models.TextChoices):
    """Tipos de turno"""
    MATUTINO = 'matutino', 'Matutino'
    VESPERTINO = 'vespertino', 'Vespertino'
    NOCTURNO = 'nocturno', 'Nocturno'
    MIXTO = 'mixto', 'Mixto'
    ROTATIVO = 'rotativo', 'Rotativo'

class Departamento(models.Model):
    """Departamentos del restaurante"""
    
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    responsable = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='departamentos_responsable'
    )
    presupuesto_mensual = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        help_text="Presupuesto mensual del departamento"
    )
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Departamento"
        verbose_name_plural = "Departamentos"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre
    
    @property
    def total_empleados(self):
        """Total de empleados activos en el departamento"""
        return self.empleados.filter(estado=EstadoEmpleado.ACTIVO).count()
    
    @property
    def costo_nomina_mensual(self):
        """Costo total de nómina mensual del departamento"""
        return self.empleados.filter(
            estado=EstadoEmpleado.ACTIVO
        ).aggregate(
            total=models.Sum('salario_base')
        )['total'] or Decimal('0')

class Puesto(models.Model):
    """Puestos de trabajo específicos"""
    
    nombre = models.CharField(max_length=100)
    departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE, related_name='puestos')
    tipo_empleado = models.CharField(max_length=30, choices=TipoEmpleado.choices)
    descripcion = models.TextField(blank=True)
    
    # Requisitos
    experiencia_minima = models.PositiveIntegerField(
        default=0, 
        help_text="Años de experiencia mínima"
    )
    educacion_requerida = models.CharField(max_length=200, blank=True)
    habilidades_requeridas = models.TextField(blank=True)
    
    # Salario
    salario_minimo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    salario_maximo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Puesto"
        verbose_name_plural = "Puestos"
        ordering = ['departamento', 'nombre']
        unique_together = ['nombre', 'departamento']
    
    def __str__(self):
        return f"{self.nombre} - {self.departamento.nombre}"

class Empleado(models.Model):
    """Información extendida de empleados"""
    
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='empleado')
    
    # Información personal
    cedula = models.CharField(max_length=20, unique=True, help_text="Número de identificación")
    fecha_nacimiento = models.DateField()
    telefono_personal = models.CharField(max_length=15, blank=True)
    telefono_emergencia = models.CharField(max_length=15, blank=True)
    contacto_emergencia = models.CharField(max_length=200, blank=True)
    direccion = models.TextField(blank=True)
    ciudad = models.CharField(max_length=100, blank=True)
    codigo_postal = models.CharField(max_length=10, blank=True)
    
    # Información laboral
    numero_empleado = models.CharField(max_length=20, unique=True, blank=True)
    puesto = models.ForeignKey(Puesto, on_delete=models.CASCADE, related_name='empleados')
    departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE, related_name='empleados')
    
    fecha_ingreso = models.DateField()
    fecha_salida = models.DateField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=EstadoEmpleado.choices, default=EstadoEmpleado.ACTIVO)
    tipo_contrato = models.CharField(max_length=20, choices=TipoContrato.choices)
    
    # Salario y beneficios
    salario_base = models.DecimalField(max_digits=10, decimal_places=2)
    comision_ventas = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0,
        help_text="Porcentaje de comisión sobre ventas"
    )
    bonificaciones = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    descuentos = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Horarios
    turno_preferido = models.CharField(max_length=20, choices=TipoTurno.choices, blank=True)
    horas_semanales = models.PositiveIntegerField(default=40)
    
    # Información adicional
    nss = models.CharField(max_length=20, blank=True, verbose_name="Número Seguro Social")
    rfc = models.CharField(max_length=20, blank=True, verbose_name="RFC")
    banco_cuenta = models.CharField(max_length=50, blank=True)
    
    # Evaluaciones y desempeño
    evaluacion_actual = models.DecimalField(
        max_digits=3, 
        decimal_places=1, 
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="Evaluación actual (0-10)"
    )
    fecha_ultima_evaluacion = models.DateField(null=True, blank=True)
    fecha_proxima_evaluacion = models.DateField(null=True, blank=True)
    
    # Control
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    notas = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Empleado"
        verbose_name_plural = "Empleados"
        ordering = ['usuario__last_name', 'usuario__first_name']
    
    def __str__(self):
        return f"{self.usuario.get_full_name()} - {self.puesto.nombre}"
    
    def save(self, *args, **kwargs):
        # Generar número de empleado si no existe
        if not self.numero_empleado:
            ultimo_numero = Empleado.objects.count() + 1
            self.numero_empleado = f"EMP-{ultimo_numero:04d}"
        super().save(*args, **kwargs)
    
    @property
    def nombre_completo(self):
        return self.usuario.get_full_name()
    
    @property
    def edad(self):
        """Calcula la edad del empleado"""
        today = timezone.now().date()
        return today.year - self.fecha_nacimiento.year - (
            (today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
        )
    
    @property
    def tiempo_en_empresa(self):
        """Tiempo trabajando en la empresa"""
        fecha_fin = self.fecha_salida or timezone.now().date()
        return fecha_fin - self.fecha_ingreso
    
    @property
    def salario_total_mensual(self):
        """Salario total incluyendo bonificaciones menos descuentos"""
        return self.salario_base + self.bonificaciones - self.descuentos
    
    @property
    def requiere_evaluacion(self):
        """Verifica si requiere evaluación"""
        if not self.fecha_proxima_evaluacion:
            return True
        
        # Si la fecha próxima evaluación ya pasó, requiere evaluación
        if self.fecha_proxima_evaluacion <= timezone.now().date():
            return True
        
        # Si no tiene evaluación actual o es muy baja
        if self.evaluacion_actual <= 5:
            return True
            
        return False
        return timezone.now().date() >= self.fecha_proxima_evaluacion

class Horario(models.Model):
    """Horarios de trabajo de empleados"""
    
    DIAS_SEMANA = [
        ('lunes', 'Lunes'),
        ('martes', 'Martes'),
        ('miercoles', 'Miércoles'),
        ('jueves', 'Jueves'),
        ('viernes', 'Viernes'),
        ('sabado', 'Sábado'),
        ('domingo', 'Domingo'),
    ]
    
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name='horarios')
    dia_semana = models.CharField(max_length=10, choices=DIAS_SEMANA)
    hora_entrada = models.TimeField()
    hora_salida = models.TimeField()
    hora_break_inicio = models.TimeField(null=True, blank=True)
    hora_break_fin = models.TimeField(null=True, blank=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Horario"
        verbose_name_plural = "Horarios"
        unique_together = ['empleado', 'dia_semana']
        ordering = ['empleado', 'dia_semana']
    
    def __str__(self):
        return f"{self.empleado.nombre_completo} - {self.get_dia_semana_display()}: {self.hora_entrada}-{self.hora_salida}"
    
    @property
    def horas_trabajadas(self):
        """Calcula las horas trabajadas en el día"""
        from datetime import datetime, timedelta
        
        entrada = datetime.combine(timezone.now().date(), self.hora_entrada)
        salida = datetime.combine(timezone.now().date(), self.hora_salida)
        
        # Si la salida es menor que la entrada, es del día siguiente
        if salida < entrada:
            salida += timedelta(days=1)
        
        horas_totales = (salida - entrada).total_seconds() / 3600
        
        # Restar tiempo de break si existe
        if self.hora_break_inicio and self.hora_break_fin:
            break_inicio = datetime.combine(timezone.now().date(), self.hora_break_inicio)
            break_fin = datetime.combine(timezone.now().date(), self.hora_break_fin)
            horas_break = (break_fin - break_inicio).total_seconds() / 3600
            horas_totales -= horas_break
        
        return round(horas_totales, 2)

class RegistroAsistencia(models.Model):
    """Registro de entrada y salida de empleados"""
    
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name='asistencias')
    fecha = models.DateField()
    
    # Registros de tiempo
    hora_entrada_programada = models.TimeField()
    hora_entrada_real = models.TimeField(null=True, blank=True)
    hora_salida_programada = models.TimeField()
    hora_salida_real = models.TimeField(null=True, blank=True)
    
    # Break/Almuerzo
    hora_break_inicio = models.TimeField(null=True, blank=True)
    hora_break_fin = models.TimeField(null=True, blank=True)
    
    # Estado del día
    presente = models.BooleanField(default=False)
    tardanza = models.BooleanField(default=False)
    minutos_tardanza = models.PositiveIntegerField(default=0)
    salida_temprana = models.BooleanField(default=False)
    minutos_salida_temprana = models.PositiveIntegerField(default=0)
    
    # Observaciones
    observaciones = models.TextField(blank=True)
    justificacion = models.TextField(blank=True)
    aprobado_por = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='asistencias_aprobadas'
    )
    
    class Meta:
        verbose_name = "Registro de Asistencia"
        verbose_name_plural = "Registros de Asistencia"
        unique_together = ['empleado', 'fecha']
        ordering = ['-fecha', 'empleado']
    
    def __str__(self):
        return f"{self.empleado.nombre_completo} - {self.fecha}"
    
    @property
    def horas_trabajadas(self):
        """Calcula las horas realmente trabajadas"""
        if not self.hora_entrada_real or not self.hora_salida_real:
            return 0
        
        from datetime import datetime, timedelta
        
        entrada = datetime.combine(self.fecha, self.hora_entrada_real)
        salida = datetime.combine(self.fecha, self.hora_salida_real)
        
        if salida < entrada:
            salida += timedelta(days=1)
        
        horas_totales = (salida - entrada).total_seconds() / 3600
        
        # Restar tiempo de break
        if self.hora_break_inicio and self.hora_break_fin:
            break_inicio = datetime.combine(self.fecha, self.hora_break_inicio)
            break_fin = datetime.combine(self.fecha, self.hora_break_fin)
            horas_break = (break_fin - break_inicio).total_seconds() / 3600
            horas_totales -= horas_break
        
        return round(horas_totales, 2)

class Evaluacion(models.Model):
    """Evaluaciones de desempeño de empleados"""
    
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name='evaluaciones')
    evaluador = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='evaluaciones_realizadas'
    )
    
    # Fechas
    fecha_evaluacion = models.DateField()
    periodo_inicio = models.DateField()
    periodo_fin = models.DateField()
    
    # Criterios de evaluación (escala 1-10)
    puntualidad = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Puntualidad y asistencia"
    )
    calidad_trabajo = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Calidad del trabajo realizado"
    )
    productividad = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Productividad y eficiencia"
    )
    trabajo_equipo = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Trabajo en equipo y colaboración"
    )
    iniciativa = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Iniciativa y proactividad"
    )
    atencion_cliente = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Atención al cliente",
        null=True, blank=True
    )
    
    # Evaluación general
    puntaje_total = models.DecimalField(max_digits=4, decimal_places=2, editable=False)
    
    # Comentarios
    fortalezas = models.TextField(blank=True)
    areas_mejora = models.TextField(blank=True)
    objetivos_siguientes = models.TextField(blank=True)
    comentarios_generales = models.TextField(blank=True)
    
    # Recomendaciones
    recomendacion_aumento = models.BooleanField(default=False)
    recomendacion_promocion = models.BooleanField(default=False)
    recomendacion_capacitacion = models.BooleanField(default=False)
    
    # Control
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Evaluación"
        verbose_name_plural = "Evaluaciones"
        ordering = ['-fecha_evaluacion']
    
    def __str__(self):
        return f"Evaluación {self.empleado.nombre_completo} - {self.fecha_evaluacion}"
    
    def save(self, *args, **kwargs):
        # Calcular puntaje total
        criterios = [
            self.puntualidad,
            self.calidad_trabajo,
            self.productividad,
            self.trabajo_equipo,
            self.iniciativa,
        ]
        
        if self.atencion_cliente:
            criterios.append(self.atencion_cliente)
        
        self.puntaje_total = sum(criterios) / len(criterios)
        
        super().save(*args, **kwargs)
        
        # Actualizar evaluación del empleado
        self.empleado.evaluacion_actual = self.puntaje_total
        self.empleado.fecha_ultima_evaluacion = self.fecha_evaluacion
        # Programar próxima evaluación en 6 meses
        from dateutil.relativedelta import relativedelta
        self.empleado.fecha_proxima_evaluacion = self.fecha_evaluacion + relativedelta(months=6)
        self.empleado.save()

class Capacitacion(models.Model):
    """Capacitaciones y entrenamientos"""
    
    TIPOS_CAPACITACION = [
        ('orientacion', 'Orientación'),
        ('seguridad', 'Seguridad e Higiene'),
        ('atencion_cliente', 'Atención al Cliente'),
        ('tecnica', 'Técnica Específica'),
        ('liderazgo', 'Liderazgo'),
        ('ventas', 'Ventas'),
        ('sistemas', 'Sistemas y Tecnología'),
        ('idiomas', 'Idiomas'),
        ('otros', 'Otros'),
    ]
    
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    tipo = models.CharField(max_length=20, choices=TIPOS_CAPACITACION)
    instructor = models.CharField(max_length=200, blank=True)
    
    # Fechas y duración
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    horas_duracion = models.PositiveIntegerField(help_text="Duración en horas")
    
    # Costo y ubicación
    costo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ubicacion = models.CharField(max_length=200, blank=True)
    modalidad = models.CharField(
        max_length=20,
        choices=[
            ('presencial', 'Presencial'),
            ('virtual', 'Virtual'),
            ('mixta', 'Mixta'),
        ],
        default='presencial'
    )
    
    # Participantes
    empleados = models.ManyToManyField(
        Empleado, 
        through='ParticipacionCapacitacion',
        related_name='capacitaciones'
    )
    
    # Control
    activa = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Capacitación"
        verbose_name_plural = "Capacitaciones"
        ordering = ['-fecha_inicio']
    
    def __str__(self):
        return f"{self.nombre} - {self.fecha_inicio}"
    
    @property
    def total_participantes(self):
        return self.empleados.count()

class ParticipacionCapacitacion(models.Model):
    """Participación de empleados en capacitaciones"""
    
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE)
    capacitacion = models.ForeignKey(Capacitacion, on_delete=models.CASCADE)
    
    # Participación
    fecha_inscripcion = models.DateTimeField(auto_now_add=True)
    asistio = models.BooleanField(default=False)
    horas_asistidas = models.PositiveIntegerField(default=0)
    calificacion = models.PositiveIntegerField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    aprobado = models.BooleanField(default=False)
    certificado = models.BooleanField(default=False)
    
    # Observaciones
    comentarios = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Participación en Capacitación"
        verbose_name_plural = "Participaciones en Capacitaciones"
        unique_together = ['empleado', 'capacitacion']
    
    def __str__(self):
        return f"{self.empleado.nombre_completo} - {self.capacitacion.nombre}"

class Nomina(models.Model):
    """Nóminas mensuales"""
    
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name='nominas')
    mes = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)])
    año = models.PositiveIntegerField()
    
    # Ingresos
    salario_base = models.DecimalField(max_digits=10, decimal_places=2)
    horas_extra = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    comisiones = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    bonificaciones = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Deducciones
    impuestos = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    seguro_social = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    otras_deducciones = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Totales
    total_ingresos = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    total_deducciones = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    salario_neto = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    
    # Control
    procesada = models.BooleanField(default=False)
    fecha_procesamiento = models.DateTimeField(null=True, blank=True)
    procesada_por = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='nominas_procesadas'
    )
    
    class Meta:
        verbose_name = "Nómina"
        verbose_name_plural = "Nóminas"
        unique_together = ['empleado', 'mes', 'año']
        ordering = ['-año', '-mes', 'empleado']
    
    def __str__(self):
        return f"{self.empleado.nombre_completo} - {self.mes}/{self.año}"
    
    def save(self, *args, **kwargs):
        # Calcular totales
        self.total_ingresos = (
            self.salario_base + 
            self.horas_extra + 
            self.comisiones + 
            self.bonificaciones
        )
        self.total_deducciones = (
            self.impuestos + 
            self.seguro_social + 
            self.otras_deducciones
        )
        self.salario_neto = self.total_ingresos - self.total_deducciones
        
        super().save(*args, **kwargs)
