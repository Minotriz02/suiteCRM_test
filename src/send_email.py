import requests

# Configuración base
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

# Autenticación
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

# 1. Obtener los registros del módulo Accounts
accounts_url = f"{BASE_URL}/legacy/Api/V8/module/Accounts"
accounts_resp = requests.get(accounts_url, headers=headers, verify=False)
if accounts_resp.status_code != 200:
    print("Error al obtener Accounts:", accounts_resp.text)
    exit()

accounts_data = accounts_resp.json()
accounts_list = accounts_data.get("data", [])
print(f"Se encontraron {len(accounts_list)} registros en Accounts.")

# 2. Obtener el email template
template_id = "f2a10cf7-c78b-7630-8a5b-67bc7bfc498e"
template_url = f"{BASE_URL}/legacy/Api/V8/module/EmailTemplates/{template_id}"
template_resp = requests.get(template_url, headers=headers, verify=False)
if template_resp.status_code == 200:
    template_attributes = template_resp.json()['data']['attributes']
    template_body = template_attributes.get('body_html', '')
    template_subject = template_attributes.get('subject', 'Clima Boletín')
else:
    print("Error al obtener el email template:", template_resp.text)
    exit()

# 3. Iterar sobre los registros y enviar email a los que tengan clima_bulletin_c activado
email_sent = 0
for account in accounts_list:
    attributes = account.get("attributes", {})
    clima_bulletin = attributes.get("clima_bulletin_c", False)

    # Consideramos activado si el valor es True, "true", 1 o "1"
    if clima_bulletin in [True, "true", 1, "1"]:
        first_name = attributes.get("first_name", "")
        last_name = attributes.get("last_name_c", "")
        email_address = attributes.get("mail_c", "")  # Ajusta al campo real que contenga el email

        # Reemplazar variables en el template
        email_body = template_body.replace("{{first_name}}", first_name).replace("{{last_name}}", last_name)
        email_subject = template_subject.replace("{{first_name}}", first_name).replace("{{last_name}}", last_name)

        # 4. Crear el registro de Email con los campos adecuados
        email_payload = {
            "data": {
                "type": "Emails",
                "attributes": {
                    "name": email_subject,          # Nombre interno
                    "subject": email_subject,       # Asunto visible
                    "description": email_body,      # Cuerpo del email
                    "to_addrs": email_address,      # Destinatario
                    "from_addr": "sebaslopezastu@gmail.com",
                    "from_name": "Sebastian",
                    "type": "out",                  # Correo saliente
                    "status": "ready"               # Listo para enviar
                }
            }
        }

        email_url = f"{BASE_URL}/legacy/Api/V8/module"
        email_resp = requests.post(email_url, json=email_payload, headers=headers, verify=False)
        if email_resp.status_code in [200, 201]:
            email_sent+=1
            print(f"Email enviado a {email_address}")
        else:
            print(f"Error al enviar email a {email_address}: {email_resp.text}")
print(f"Se enviaron {email_sent} emails.")