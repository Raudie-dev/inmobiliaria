import urllib.request
import json
import threading
from django.core.mail import get_connection, send_mail
from django.conf import settings
from django.urls import reverse
from django.utils.html import strip_tags
from .models import ConfiguracionCorreo, NotificacionMatch

def enviar_whatsapp(telefono, mensaje):
    """
    Envía un mensaje de WhatsApp a través del Gateway local de Node.js.
    """
    url = 'http://127.0.0.1:3000/send'
    data = json.dumps({'number': telefono, 'message': mensaje}).encode('utf-8')
    headers = {'Content-Type': 'application/json'}
    req = urllib.request.Request(url, data=data, headers=headers, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            res_data = json.loads(response.read().decode())
            return res_data.get('ok', False)
    except Exception as e:
        print(f"Error enviando WhatsApp a {telefono}: {e}")
        return False

def enviar_correo_match(cliente, propiedad, url_propiedad):
    """
    Envía un correo electrónico usando las credenciales guardadas en ConfiguracionCorreo.
    """
    try:
        config = ConfiguracionCorreo.load()
        if not config.email_host_user or not config.email_host_password:
            print("No hay credenciales SMTP configuradas.")
            return False

        # Configurar conexión SMTP dinámica
        connection = get_connection(
            host='smtp.gmail.com',
            port=587,
            username=config.email_host_user,
            password=config.email_host_password,
            use_tls=True
        )

        asunto = f"¡Tenemos una propiedad perfecta para ti, {cliente.nombre}!"
        
        # Mensaje HTML
        mensaje_html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <h2 style="color: #2563EB;">Hola {cliente.nombre},</h2>
                <p>Hemos encontrado una propiedad que encaja perfectamente con tus intereses en <strong>{propiedad.zona}</strong>.</p>
                <div style="background-color: #f8f9fa; padding: 15px; border-left: 4px solid #2563EB; margin: 20px 0;">
                    <h3 style="margin-top: 0;">{propiedad.titulo}</h3>
                    <p><strong>Tipo:</strong> {propiedad.tipo_inmueble}</p>
                    <p><strong>Precio:</strong> ${propiedad.precio}</p>
                    <p><strong>Superficie:</strong> {propiedad.superficie} m²</p>
                    <p><strong>Habitaciones/Baños:</strong> {propiedad.habitaciones} hab. / {propiedad.banos} baños</p>
                </div>
                <p>Puedes ver más fotos y detalles haciendo clic en el siguiente enlace:</p>
                <p>
                    <a href="{url_propiedad}" style="background-color: #2563EB; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">Ver Propiedad</a>
                </p>
                <p>¡Esperamos tu mensaje si deseas agendar una visita!</p>
                <p>Atentamente,<br><strong>Tu Equipo Inmobiliario</strong></p>
            </body>
        </html>
        """
        
        mensaje_texto = strip_tags(mensaje_html)

        send_mail(
            subject=asunto,
            message=mensaje_texto,
            from_email=config.email_host_user,
            recipient_list=[cliente.email],
            html_message=mensaje_html,
            connection=connection,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error enviando correo a {cliente.email}: {e}")
        return False

def procesar_notificaciones_match(matches, dominio):
    """
    Procesa una lista de NotificacionMatch y envía los correos/whatsapps de forma síncrona dentro del hilo.
    """
    for match in matches:
        cliente = match.cliente
        propiedad = match.propiedad
        url_propiedad = f"{dominio}{reverse('detalle_propiedad_publica', args=[propiedad.pk])}"
        
        exito_whatsapp = False
        exito_email = False

        # Enviar WhatsApp si el cliente tiene teléfono
        if cliente.telefono:
            mensaje_wa = (
                f"¡Hola {cliente.nombre}! 👋\n\n"
                f"Tenemos una nueva propiedad que coincide con lo que buscas:\n"
                f"📍 *{propiedad.zona}*\n"
                f"🏠 {propiedad.titulo}\n"
                f"💰 ${propiedad.precio}\n\n"
                f"Mira las fotos y todos los detalles aquí:\n"
                f"{url_propiedad}\n\n"
                f"¿Te interesaría agendar una visita?"
            )
            exito_whatsapp = enviar_whatsapp(cliente.telefono, mensaje_wa)

        # Enviar Correo si el cliente tiene email
        if cliente.email:
            exito_email = enviar_correo_match(cliente, propiedad, url_propiedad)

        # Marcar como enviado si al menos uno funcionó, o actualizar el estado en general
        if exito_whatsapp or exito_email:
            match.estado = 'Enviado'
            match.canal = 'WhatsApp y Email' if exito_whatsapp and exito_email else ('WhatsApp' if exito_whatsapp else 'Email')
            match.save()

def disparar_notificaciones_asincronas(matches, dominio):
    """
    Lanza el procesamiento de notificaciones en un hilo en segundo plano.
    """
    thread = threading.Thread(target=procesar_notificaciones_match, args=(matches, dominio))
    thread.daemon = True
    thread.start()
