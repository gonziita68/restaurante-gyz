from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from empleados.models import (
    Departamento, Puesto, Empleado, Horario, RegistroAsistencia,
    Evaluacion, Capacitacion, ParticipacionCapacitacion, Nomina,
    EstadoEmpleado, TipoEmpleado, TipoContrato, TipoTurno
)
from decimal import Decimal
from django.utils import timezone
from datetime import datetime, timedelta, time
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Pobla la base de datos con datos de ejemplo para el sistema de empleados'

    def handle(self, *args, **options):
        self.stdout.write('Poblando sistema de empleados...')
        
        # Crear departamentos
        departamentos_data = [
            {
                'nombre': 'Administración',
                'descripcion': 'Administración general y recursos humanos',
                'presupuesto_mensual': Decimal('50000.00'),
            },
            {
                'nombre': 'Cocina',
                'descripcion': 'Preparación de alimentos y bebidas',
                'presupuesto_mensual': Decimal('80000.00'),
            },
            {
                'nombre': 'Servicio al Cliente',
                'descripcion': 'Atención a comensales y servicio de mesa',
                'presupuesto_mensual': Decimal('45000.00'),
            },
            {
                'nombre': 'Delivery',
                'descripcion': 'Entrega a domicilio y logística',
                'presupuesto_mensual': Decimal('25000.00'),
            },
            {
                'nombre': 'Limpieza y Mantenimiento',
                'descripcion': 'Limpieza e higiene del restaurante',
                'presupuesto_mensual': Decimal('15000.00'),
            },
        ]
        
        departamentos = {}
        for depto_data in departamentos_data:
            departamento, created = Departamento.objects.get_or_create(
                nombre=depto_data['nombre'],
                defaults=depto_data
            )
            departamentos[depto_data['nombre']] = departamento
            if created:
                self.stdout.write(f'  ✓ Departamento {departamento.nombre} creado')
        
        # Crear puestos
        puestos_data = [
            # Administración
            {
                'nombre': 'Gerente General',
                'departamento': 'Administración',
                'tipo_empleado': TipoEmpleado.GERENTE,
                'descripcion': 'Responsable general del restaurante',
                'experiencia_minima': 5,
                'educacion_requerida': 'Licenciatura en Administración o afín',
                'salario_minimo': Decimal('25000.00'),
                'salario_maximo': Decimal('35000.00'),
            },
            {
                'nombre': 'Subgerente',
                'departamento': 'Administración',
                'tipo_empleado': TipoEmpleado.SUBGERENTE,
                'descripcion': 'Apoyo en administración general',
                'experiencia_minima': 3,
                'salario_minimo': Decimal('18000.00'),
                'salario_maximo': Decimal('25000.00'),
            },
            {
                'nombre': 'Cajero',
                'departamento': 'Administración',
                'tipo_empleado': TipoEmpleado.CAJERO,
                'descripcion': 'Manejo de caja y cobros',
                'experiencia_minima': 1,
                'salario_minimo': Decimal('8000.00'),
                'salario_maximo': Decimal('12000.00'),
            },
            # Cocina
            {
                'nombre': 'Chef Ejecutivo',
                'departamento': 'Cocina',
                'tipo_empleado': TipoEmpleado.CHEF,
                'descripcion': 'Responsable de la cocina y menús',
                'experiencia_minima': 8,
                'educacion_requerida': 'Gastronomía o Chef profesional',
                'salario_minimo': Decimal('20000.00'),
                'salario_maximo': Decimal('30000.00'),
            },
            {
                'nombre': 'Cocinero',
                'departamento': 'Cocina',
                'tipo_empleado': TipoEmpleado.COCINERO,
                'descripcion': 'Preparación de alimentos',
                'experiencia_minima': 2,
                'salario_minimo': Decimal('10000.00'),
                'salario_maximo': Decimal('15000.00'),
            },
            {
                'nombre': 'Ayudante de Cocina',
                'departamento': 'Cocina',
                'tipo_empleado': TipoEmpleado.AYUDANTE_COCINA,
                'descripcion': 'Apoyo en preparación y limpieza',
                'experiencia_minima': 0,
                'salario_minimo': Decimal('7000.00'),
                'salario_maximo': Decimal('10000.00'),
            },
            # Servicio
            {
                'nombre': 'Mesero',
                'departamento': 'Servicio al Cliente',
                'tipo_empleado': TipoEmpleado.MESERO,
                'descripcion': 'Atención a mesas y servicio',
                'experiencia_minima': 1,
                'salario_minimo': Decimal('8000.00'),
                'salario_maximo': Decimal('12000.00'),
            },
            {
                'nombre': 'Hostess',
                'departamento': 'Servicio al Cliente',
                'tipo_empleado': TipoEmpleado.HOSTESS,
                'descripcion': 'Recepción y ubicación de clientes',
                'experiencia_minima': 0,
                'salario_minimo': Decimal('7500.00'),
                'salario_maximo': Decimal('11000.00'),
            },
            # Delivery
            {
                'nombre': 'Repartidor',
                'departamento': 'Delivery',
                'tipo_empleado': TipoEmpleado.REPARTIDOR,
                'descripcion': 'Entrega de pedidos a domicilio',
                'experiencia_minima': 0,
                'salario_minimo': Decimal('6000.00'),
                'salario_maximo': Decimal('9000.00'),
            },
            # Limpieza
            {
                'nombre': 'Personal de Limpieza',
                'departamento': 'Limpieza y Mantenimiento',
                'tipo_empleado': TipoEmpleado.LIMPIEZA,
                'descripcion': 'Limpieza e higiene general',
                'experiencia_minima': 0,
                'salario_minimo': Decimal('6500.00'),
                'salario_maximo': Decimal('8500.00'),
            },
        ]
        
        puestos = {}
        for puesto_data in puestos_data:
            puesto_data['departamento'] = departamentos[puesto_data['departamento']]
            puesto, created = Puesto.objects.get_or_create(
                nombre=puesto_data['nombre'],
                departamento=puesto_data['departamento'],
                defaults=puesto_data
            )
            puestos[puesto_data['nombre']] = puesto
            if created:
                self.stdout.write(f'  ✓ Puesto {puesto.nombre} creado')
        
        # Crear usuarios y empleados
        empleados_data = [
            {
                'username': 'maria.gonzalez',
                'email': 'maria.gonzalez@restaurantegyz.com',
                'first_name': 'María',
                'last_name': 'González',
                'cedula': '12345678901',
                'fecha_nacimiento': '1985-03-15',
                'telefono_personal': '555-1001',
                'puesto': 'Gerente General',
                'fecha_ingreso': '2020-01-15',
                'salario_base': Decimal('30000.00'),
                'tipo_contrato': TipoContrato.TIEMPO_COMPLETO,
                'turno_preferido': TipoTurno.MATUTINO,
                'is_staff': True,
            },
            {
                'username': 'carlos.rodriguez',
                'email': 'carlos.rodriguez@restaurantegyz.com',
                'first_name': 'Carlos',
                'last_name': 'Rodríguez',
                'cedula': '23456789012',
                'fecha_nacimiento': '1990-07-22',
                'telefono_personal': '555-1002',
                'puesto': 'Chef Ejecutivo',
                'fecha_ingreso': '2020-02-01',
                'salario_base': Decimal('25000.00'),
                'tipo_contrato': TipoContrato.TIEMPO_COMPLETO,
                'turno_preferido': TipoTurno.MATUTINO,
            },
            {
                'username': 'ana.martinez',
                'email': 'ana.martinez@restaurantegyz.com',
                'first_name': 'Ana',
                'last_name': 'Martínez',
                'cedula': '34567890123',
                'fecha_nacimiento': '1992-11-08',
                'telefono_personal': '555-1003',
                'puesto': 'Subgerente',
                'fecha_ingreso': '2021-03-10',
                'salario_base': Decimal('20000.00'),
                'tipo_contrato': TipoContrato.TIEMPO_COMPLETO,
                'turno_preferido': TipoTurno.VESPERTINO,
            },
            {
                'username': 'luis.hernandez',
                'email': 'luis.hernandez@restaurantegyz.com',
                'first_name': 'Luis',
                'last_name': 'Hernández',
                'cedula': '45678901234',
                'fecha_nacimiento': '1988-05-14',
                'telefono_personal': '555-1004',
                'puesto': 'Cocinero',
                'fecha_ingreso': '2021-06-01',
                'salario_base': Decimal('12000.00'),
                'tipo_contrato': TipoContrato.TIEMPO_COMPLETO,
                'turno_preferido': TipoTurno.MATUTINO,
            },
            {
                'username': 'sofia.lopez',
                'email': 'sofia.lopez@restaurantegyz.com',
                'first_name': 'Sofía',
                'last_name': 'López',
                'cedula': '56789012345',
                'fecha_nacimiento': '1995-09-20',
                'telefono_personal': '555-1005',
                'puesto': 'Mesero',
                'fecha_ingreso': '2022-01-15',
                'salario_base': Decimal('10000.00'),
                'comision_ventas': Decimal('2.5'),
                'tipo_contrato': TipoContrato.TIEMPO_COMPLETO,
                'turno_preferido': TipoTurno.VESPERTINO,
            },
            {
                'username': 'pedro.sanchez',
                'email': 'pedro.sanchez@restaurantegyz.com',
                'first_name': 'Pedro',
                'last_name': 'Sánchez',
                'cedula': '67890123456',
                'fecha_nacimiento': '1993-12-03',
                'telefono_personal': '555-1006',
                'puesto': 'Mesero',
                'fecha_ingreso': '2022-03-01',
                'salario_base': Decimal('10000.00'),
                'comision_ventas': Decimal('2.5'),
                'tipo_contrato': TipoContrato.TIEMPO_COMPLETO,
                'turno_preferido': TipoTurno.NOCTURNO,
            },
            {
                'username': 'laura.torres',
                'email': 'laura.torres@restaurantegyz.com',
                'first_name': 'Laura',
                'last_name': 'Torres',
                'cedula': '78901234567',
                'fecha_nacimiento': '1997-01-25',
                'telefono_personal': '555-1007',
                'puesto': 'Hostess',
                'fecha_ingreso': '2022-08-01',
                'salario_base': Decimal('9000.00'),
                'tipo_contrato': TipoContrato.TIEMPO_COMPLETO,
                'turno_preferido': TipoTurno.VESPERTINO,
            },
            {
                'username': 'miguel.vargas',
                'email': 'miguel.vargas@restaurantegyz.com',
                'first_name': 'Miguel',
                'last_name': 'Vargas',
                'cedula': '89012345678',
                'fecha_nacimiento': '1991-04-12',
                'telefono_personal': '555-1008',
                'puesto': 'Repartidor',
                'fecha_ingreso': '2023-01-10',
                'salario_base': Decimal('7500.00'),
                'tipo_contrato': TipoContrato.MEDIO_TIEMPO,
                'turno_preferido': TipoTurno.MIXTO,
            },
        ]
        
        empleados_creados = []
        for emp_data in empleados_data:
            # Crear usuario
            usuario, created = User.objects.get_or_create(
                username=emp_data['username'],
                defaults={
                    'email': emp_data['email'],
                    'first_name': emp_data['first_name'],
                    'last_name': emp_data['last_name'],
                    'is_staff': emp_data.get('is_staff', False),
                }
            )
            
            if created:
                usuario.set_password('empleado123')
                usuario.save()
            
            # Crear empleado
            puesto = puestos[emp_data['puesto']]
            empleado_data = {
                'usuario': usuario,
                'cedula': emp_data['cedula'],
                'fecha_nacimiento': datetime.strptime(emp_data['fecha_nacimiento'], '%Y-%m-%d').date(),
                'telefono_personal': emp_data['telefono_personal'],
                'telefono_emergencia': '555-9999',
                'contacto_emergencia': 'Familia',
                'direccion': f'Calle {random.randint(1, 100)} #{random.randint(1, 999)}',
                'ciudad': 'Ciudad Principal',
                'puesto': puesto,
                'departamento': puesto.departamento,
                'fecha_ingreso': datetime.strptime(emp_data['fecha_ingreso'], '%Y-%m-%d').date(),
                'salario_base': emp_data['salario_base'],
                'comision_ventas': emp_data.get('comision_ventas', Decimal('0')),
                'tipo_contrato': emp_data['tipo_contrato'],
                'turno_preferido': emp_data['turno_preferido'],
                'horas_semanales': 40 if emp_data['tipo_contrato'] == TipoContrato.TIEMPO_COMPLETO else 20,
                'evaluacion_actual': Decimal(str(random.uniform(7.0, 9.5))),
            }
            
            empleado, created = Empleado.objects.get_or_create(
                usuario=usuario,
                defaults=empleado_data
            )
            empleados_creados.append(empleado)
            
            if created:
                self.stdout.write(f'  ✓ Empleado {empleado.nombre_completo} creado')
        
        # Crear horarios para empleados
        horarios_config = {
            TipoTurno.MATUTINO: {
                'lunes': ('07:00', '15:00'),
                'martes': ('07:00', '15:00'),
                'miercoles': ('07:00', '15:00'),
                'jueves': ('07:00', '15:00'),
                'viernes': ('07:00', '15:00'),
                'sabado': ('08:00', '16:00'),
            },
            TipoTurno.VESPERTINO: {
                'martes': ('14:00', '22:00'),
                'miercoles': ('14:00', '22:00'),
                'jueves': ('14:00', '22:00'),
                'viernes': ('14:00', '22:00'),
                'sabado': ('14:00', '22:00'),
                'domingo': ('12:00', '20:00'),
            },
            TipoTurno.NOCTURNO: {
                'miercoles': ('18:00', '02:00'),
                'jueves': ('18:00', '02:00'),
                'viernes': ('18:00', '02:00'),
                'sabado': ('18:00', '02:00'),
                'domingo': ('18:00', '01:00'),
            },
            TipoTurno.MIXTO: {
                'lunes': ('11:00', '15:00'),
                'martes': ('17:00', '21:00'),
                'jueves': ('11:00', '15:00'),
                'viernes': ('17:00', '21:00'),
                'sabado': ('11:00', '19:00'),
                'domingo': ('11:00', '19:00'),
            },
        }
        
        for empleado in empleados_creados:
            if empleado.turno_preferido in horarios_config:
                horarios = horarios_config[empleado.turno_preferido]
                for dia, (entrada, salida) in horarios.items():
                    Horario.objects.get_or_create(
                        empleado=empleado,
                        dia_semana=dia,
                        defaults={
                            'hora_entrada': time.fromisoformat(entrada),
                            'hora_salida': time.fromisoformat(salida),
                            'hora_break_inicio': time(12, 0) if empleado.turno_preferido == TipoTurno.MATUTINO else time(18, 0),
                            'hora_break_fin': time(13, 0) if empleado.turno_preferido == TipoTurno.MATUTINO else time(19, 0),
                        }
                    )
        
        # Crear algunas evaluaciones
        gerente = empleados_creados[0]  # María González
        for empleado in empleados_creados[1:4]:  # Evaluar a algunos empleados
            Evaluacion.objects.get_or_create(
                empleado=empleado,
                evaluador=gerente.usuario,
                defaults={
                    'fecha_evaluacion': timezone.now().date() - timedelta(days=random.randint(30, 180)),
                    'periodo_inicio': timezone.now().date() - timedelta(days=180),
                    'periodo_fin': timezone.now().date() - timedelta(days=30),
                    'puntualidad': random.randint(7, 10),
                    'calidad_trabajo': random.randint(7, 10),
                    'productividad': random.randint(6, 9),
                    'trabajo_equipo': random.randint(7, 10),
                    'iniciativa': random.randint(6, 9),
                    'atencion_cliente': random.randint(7, 10) if empleado.puesto.tipo_empleado in [TipoEmpleado.MESERO, TipoEmpleado.HOSTESS] else None,
                    'fortalezas': 'Excelente desempeño y actitud positiva',
                    'areas_mejora': 'Continuar desarrollando habilidades técnicas',
                    'recomendacion_aumento': random.choice([True, False]),
                }
            )
        
        # Crear una capacitación
        capacitacion = Capacitacion.objects.create(
            nombre='Seguridad e Higiene en Restaurantes',
            descripcion='Capacitación obligatoria sobre normas de seguridad',
            tipo='seguridad',
            instructor='Inspector de Salubridad',
            fecha_inicio=timezone.now().date() + timedelta(days=7),
            fecha_fin=timezone.now().date() + timedelta(days=7),
            horas_duracion=8,
            costo=Decimal('5000.00'),
            ubicacion='Salón de conferencias',
            modalidad='presencial',
        )
        
        # Inscribir empleados
        for empleado in empleados_creados:
            ParticipacionCapacitacion.objects.create(
                empleado=empleado,
                capacitacion=capacitacion,
                asistio=random.choice([True, False]),
                horas_asistidas=random.randint(6, 8),
                calificacion=random.randint(75, 95),
                aprobado=True,
            )
        
        # Crear registros de asistencia para los últimos 7 días
        for i in range(7):
            fecha = timezone.now().date() - timedelta(days=i)
            for empleado in empleados_creados:
                # Obtener horario del día
                dias_semana = {
                    0: 'lunes', 1: 'martes', 2: 'miercoles', 3: 'jueves',
                    4: 'viernes', 5: 'sabado', 6: 'domingo'
                }
                dia_nombre = dias_semana[fecha.weekday()]
                
                try:
                    horario = empleado.horarios.get(dia_semana=dia_nombre, activo=True)
                    
                    # Simular asistencia
                    presente = random.random() > 0.1  # 90% de asistencia
                    tardanza = random.random() < 0.15 if presente else False  # 15% de tardanzas
                    
                    hora_entrada_real = None
                    minutos_tardanza = 0
                    
                    if presente:
                        if tardanza:
                            minutos_tardanza = random.randint(5, 30)
                            entrada_programada = datetime.combine(fecha, horario.hora_entrada)
                            hora_entrada_real = (entrada_programada + timedelta(minutes=minutos_tardanza)).time()
                        else:
                            # Puntual o temprano
                            minutos_adelanto = random.randint(-10, 5)
                            entrada_programada = datetime.combine(fecha, horario.hora_entrada)
                            hora_entrada_real = (entrada_programada + timedelta(minutes=minutos_adelanto)).time()
                    
                    hora_salida_real = None
                    if presente:
                        # Simular salida normal
                        salida_programada = datetime.combine(fecha, horario.hora_salida)
                        minutos_variacion = random.randint(-15, 30)
                        hora_salida_real = (salida_programada + timedelta(minutes=minutos_variacion)).time()
                    
                    RegistroAsistencia.objects.get_or_create(
                        empleado=empleado,
                        fecha=fecha,
                        defaults={
                            'hora_entrada_programada': horario.hora_entrada,
                            'hora_entrada_real': hora_entrada_real,
                            'hora_salida_programada': horario.hora_salida,
                            'hora_salida_real': hora_salida_real,
                            'presente': presente,
                            'tardanza': tardanza,
                            'minutos_tardanza': minutos_tardanza,
                            'observaciones': 'Registro automático' if presente else 'Ausencia',
                        }
                    )
                    
                except Horario.DoesNotExist:
                    # No tiene horario para este día
                    continue
        
        # Crear nóminas del mes anterior
        mes_anterior = (timezone.now().replace(day=1) - timedelta(days=1))
        for empleado in empleados_creados:
            # Calcular horas trabajadas del mes (simulado)
            dias_trabajados = random.randint(20, 22)
            horas_extra = Decimal(str(random.uniform(0, 20)))
            
            # Calcular comisiones (solo para meseros)
            comisiones = Decimal('0')
            if empleado.puesto.tipo_empleado == TipoEmpleado.MESERO:
                ventas_simuladas = Decimal(str(random.uniform(15000, 25000)))
                comisiones = ventas_simuladas * (empleado.comision_ventas / 100)
            
            # Calcular deducciones
            total_ingresos = empleado.salario_base + horas_extra * 50 + comisiones
            impuestos = total_ingresos * Decimal('0.12')  # 12% impuestos
            seguro_social = total_ingresos * Decimal('0.03')  # 3% seguro
            
            Nomina.objects.get_or_create(
                empleado=empleado,
                mes=mes_anterior.month,
                año=mes_anterior.year,
                defaults={
                    'salario_base': empleado.salario_base,
                    'horas_extra': horas_extra * 50,
                    'comisiones': comisiones,
                    'bonificaciones': Decimal('0'),
                    'impuestos': impuestos,
                    'seguro_social': seguro_social,
                    'otras_deducciones': Decimal('0'),
                    'procesada': True,
                    'fecha_procesamiento': timezone.now(),
                }
            )
        
        # Asignar responsables a departamentos
        departamentos['Administración'].responsable = empleados_creados[0].usuario  # María
        departamentos['Administración'].save()
        
        departamentos['Cocina'].responsable = empleados_creados[1].usuario  # Carlos
        departamentos['Cocina'].save()
        
        # Estadísticas finales
        total_empleados = Empleado.objects.filter(activo=True).count()
        total_departamentos = Departamento.objects.filter(activo=True).count()
        total_evaluaciones = Evaluacion.objects.count()
        total_capacitaciones = Capacitacion.objects.count()
        
        self.stdout.write(
            self.style.SUCCESS('✅ Sistema de empleados poblado exitosamente!')
        )
        self.stdout.write('')
        self.stdout.write('👥 Resumen:')
        self.stdout.write(f'   - Empleados: {total_empleados}')
        self.stdout.write(f'   - Departamentos: {total_departamentos}')
        self.stdout.write(f'   - Puestos: {Puesto.objects.count()}')
        self.stdout.write(f'   - Evaluaciones: {total_evaluaciones}')
        self.stdout.write(f'   - Capacitaciones: {total_capacitaciones}')
        self.stdout.write(f'   - Registros asistencia: {RegistroAsistencia.objects.count()}')
        self.stdout.write('')
        self.stdout.write('🌐 Acceso al sistema:')
        self.stdout.write('   - Dashboard: http://127.0.0.1:8000/empleados/')
        self.stdout.write('   - Admin: http://127.0.0.1:8000/admin/empleados/')
        self.stdout.write('')
        self.stdout.write('👤 Usuarios creados (contraseña: empleado123):')
        for emp in empleados_creados:
            rol = "👑 Gerente" if emp.puesto.tipo_empleado == TipoEmpleado.GERENTE else f"👤 {emp.puesto.nombre}"
            self.stdout.write(f'   - {emp.usuario.username} - {rol}')
        self.stdout.write('')
        self.stdout.write(
            self.style.WARNING('📊 Se han creado datos simulados de asistencia, evaluaciones y nóminas.')
        )
