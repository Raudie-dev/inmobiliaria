from django.db import models

class User_admin(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=128)
    bloqueado = models.BooleanField(default=False)
    email = models.EmailField(max_length=150, unique=True, null=True, blank=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.nombre

class Cliente(models.Model):
    TIPO_INMUEBLE_CHOICES = [
        ('Casa', 'Casa'),
        ('Departamento', 'Departamento'),
        ('Lote', 'Lote'),
        ('Comercial', 'Comercial'),
        ('Otro', 'Otro'),
    ]

    nombre = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20, help_text="Ej: 573001234567 (Incluye código de país, sin espacios ni el signo +)")
    presupuesto_min = models.DecimalField(max_digits=12, decimal_places=2)
    presupuesto_max = models.DecimalField(max_digits=12, decimal_places=2)
    tipo_inmueble = models.CharField(max_length=50, choices=TIPO_INMUEBLE_CHOICES)
    zona_interes = models.CharField(max_length=150)
    habitaciones = models.PositiveIntegerField()
    banos = models.PositiveIntegerField(verbose_name="Baños")
    activo = models.BooleanField(default=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} ({self.email})"

class Propiedad(models.Model):
    TIPO_OPERACION_CHOICES = [
        ('Venta', 'Venta'),
        ('Alquiler', 'Alquiler'),
    ]
    TIPO_INMUEBLE_CHOICES = [
        ('Casa', 'Casa'),
        ('Departamento', 'Departamento'),
        ('Lote', 'Lote'),
        ('Comercial', 'Comercial'),
        ('Otro', 'Otro'),
    ]
    ESTADO_CHOICES = [
        ('Disponible', 'Disponible'),
        ('Reservada', 'Reservada'),
        ('Vendida', 'Vendida'),
    ]

    titulo = models.CharField(max_length=200)
    tipo_operacion = models.CharField(max_length=20, choices=TIPO_OPERACION_CHOICES)
    tipo_inmueble = models.CharField(max_length=50, choices=TIPO_INMUEBLE_CHOICES)
    precio = models.DecimalField(max_digits=12, decimal_places=2)
    superficie = models.DecimalField(max_digits=10, decimal_places=2, help_text="m²")
    habitaciones = models.PositiveIntegerField()
    banos = models.PositiveIntegerField(verbose_name="Baños")
    direccion = models.CharField(max_length=250)
    zona = models.CharField(max_length=150)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='Disponible')
    descripcion = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo
    
    @property
    def get_portada(self):
        portada = self.imagenes.filter(es_portada=True).first()
        if portada:
            return portada.imagen
        elif self.imagenes.exists():
            return self.imagenes.order_by('orden').first().imagen
        return None

class PropiedadImagen(models.Model):
    propiedad = models.ForeignKey(Propiedad, related_name='imagenes', on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to='propiedades_galeria/')
    es_portada = models.BooleanField(default=False)
    orden = models.PositiveIntegerField(default=0)
    fecha_subida = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['orden', 'id']

    def __str__(self):
        return f"Imagen para {self.propiedad.titulo}"

class NotificacionMatch(models.Model):
    CANAL_CHOICES = [
        ('Email', 'Email'),
        ('WhatsApp', 'WhatsApp'),
    ]
    ESTADO_CHOICES = [
        ('Pendiente', 'Pendiente'),
        ('Enviado', 'Enviado'),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='matches')
    propiedad = models.ForeignKey(Propiedad, on_delete=models.CASCADE, related_name='matches')
    fecha_envio = models.DateTimeField(auto_now_add=True)
    canal = models.CharField(max_length=20, choices=CANAL_CHOICES, default='Email')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='Pendiente')

    def __str__(self):
        return f"Match: {self.cliente.nombre} - {self.propiedad.titulo}"

class ConfiguracionCorreo(models.Model):
    email_host_user = models.EmailField(max_length=250, help_text="Ej: tu-correo@gmail.com")
    email_host_password = models.CharField(max_length=150, help_text="Contraseña de Aplicación (16 caracteres)")
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Asegurarse de que solo exista un registro (Singleton)
        self.pk = 1
        super(ConfiguracionCorreo, self).save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return "Configuración de Correo SMTP"
