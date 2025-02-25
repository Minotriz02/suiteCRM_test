import requests

# Configuración base (ajusta según tu entorno)
BASE_URL = "https://localhost"
AUTH_URL = f"{BASE_URL}/legacy/Api/access_token"

# Credenciales de autenticación
credentials = {
    "grant_type": "password",
    "client_id": "6e4daf9f-bd5c-bdcf-2188-67bc9a9789b3",
    "client_secret": "admin123",
    "username": "user",
    "password": "bitnami",
    "platform": "suitecrm"
}

# Autenticación para obtener el token
response = requests.post(AUTH_URL, data=credentials, verify=False)
if response.status_code == 200:
    access_token = response.json().get("access_token")
    print("Token obtenido:", access_token)
else:
    print("Error autenticando:", response.text)
    exit()

headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

# Payload para el registro de Email (nota el cambio en "type")
email_payload = {
    "data": {
        "type": "Emails",  # Debe coincidir con el nombre del módulo
        "attributes": {
            "name": "Correo de Prueba",  # Nombre interno del registro
            "subject": "Prueba de envío de correo desde SuiteCRM",  # Asunto del correo
            "description": "<p>Hola, este es un correo de prueba enviado desde SuiteCRM via API.</p>",
            "to_addrs": "sebaslopezastu08@gmail.com",  # Destinatario
            "from_addr": "sebaslopezastu08@gmail.com",  # Remitente (debe estar configurado en Email Settings)
            "from_name": "SuiteCRM Test",               # Nombre del remitente
            "type": "out",                              # Indica que es un correo saliente
            "status": "ready"                           # Marca el registro para envío (el Scheduler lo procesará)
        }
    }
}

# Enviar el registro de Email mediante la API (incluye el módulo en la URL)
email_url = f"{BASE_URL}/legacy/Api/V8/module"
email_resp = requests.post(email_url, json=email_payload, headers=headers, verify=False)
if email_resp.status_code in [200, 201]:
    print("Registro de Email creado correctamente. Revisa en SuiteCRM si se envía el correo.")
    print(email_resp.json())
else:
    print("Error al crear el Email:", email_resp.text)
