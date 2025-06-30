#!/usr/bin/env python3
"""
test_smtp_relay.py
──────────────────
Envía un correo de prueba desde notificationsmbo@snaplogic.com
usando el relay smtp-relay.gmail.com configurado por IT.

• Intenta primero SIN autenticación (modo “IP-allowlist”)
• Si el servidor pide auth, vuelve a intentar con usuario/clave
• Muestra el resultado por pantalla
"""

import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# ───── CONFIGURA AQUÍ ────────────────────────────────────────────
SMTP_HOST   = "smtp-relay.gmail.com"
SMTP_PORT   = 587                # STARTTLS
USE_TLS     = True               # STARTTLS sí o sí (puerto 587)
SMTP_USER   = "notificationsmbo@snaplogic.com"   # ← solo si hace falta auth
SMTP_PASS   = ")cXzn2'z"               # ← idem

SENDER   = "notificationsmbo@snaplogic.com"
RECIPIENT = "atdughetti@snaplogic.com"
# ────────────────────────────────────────────────────────────────

def build_message() -> str:
    """Crea un mensaje multiparte (texto + HTML)."""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Prueba SMTP relay (MBO Tracker)"
    msg["From"]    = SENDER
    msg["To"]      = RECIPIENT

    text = (
        "Hola Angelica,\n\n"
        "Esto es un correo de prueba enviado a través del SMTP relay "
        "de Google Workspace.\n\n"
        "¡Si lo recibes, todo funciona! 😊\n"
        "-- MBO Tracker"
    )

    html = f"""
    <html>
      <body>
        <p>Hola Angelica,<br><br>
           <strong>Esto es un correo de prueba</strong> enviado a través del
           SMTP&nbsp;relay de Google Workspace.<br><br>
           ¡Si lo recibes, todo funciona! 😊<br><br>
           — MBO&nbsp;Tracker
        </p>
      </body>
    </html>
    """

    msg.attach(MIMEText(text, "plain", "utf-8"))
    msg.attach(MIMEText(html, "html", "utf-8"))
    return msg.as_string()

def send_via_relay():
    context = ssl.create_default_context()
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as server:
        print(f"Conectado a {SMTP_HOST}:{SMTP_PORT}")
        if USE_TLS:
            server.starttls(context=context)
            print("→ STARTTLS OK")

        # ── INTENTO 1: sin autenticación ─────────────────────────
        try:
            print("→ Intento 1: enviar SIN autenticación…")
            server.sendmail(SENDER, RECIPIENT, build_message())
            print("✓ Mensaje enviado SIN autenticación")
            return
        except smtplib.SMTPException as e:
            print(f"   Falló sin auth: {e}")

        # ── INTENTO 2: con usuario/clave ─────────────────────────
        try:
            print("→ Intento 2: autenticando con LOGIN…")
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SENDER, RECIPIENT, build_message())
            print("✓ Mensaje enviado CON autenticación")
        except smtplib.SMTPException as e:
            print(f"✗ Falló con auth: {e}")

if __name__ == "__main__":
    send_via_relay()
# ── FIN DEL SCRIPT ─────────────────────────────────────────────


