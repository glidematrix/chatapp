from chatapp.channels.whatsapp import WhatsApp

wa = WhatsApp()

# python -m chatapp.channels


message = 'Test Message'
phone = '+260978967132'

wa.send(
    message=message,
    phone=phone
)