import requests
import json

# Configuración base: ajusta la URL según tu entorno
BASE_URL = "https://localhost"  # Usa la IP/hostname y puerto mapeado (por ejemplo, http://localhost si mapeaste el puerto 80)
AUTH_URL = f"{BASE_URL}/legacy/Api/access_token"

# Credenciales de autenticación (ajusta según corresponda)
credentials = {
    "grant_type": "password",
    "client_id": "6e4daf9f-bd5c-bdcf-2188-67bc9a9789b3",
    "client_secret": "admin123",
    "username": "user",
    "password": "bitnami",
    "platform": "suitecrm"
}

# Solicitud de autenticación para obtener el token
response = requests.post(AUTH_URL, data=credentials, verify=False)
if response.status_code == 200:
    access_token = response.json().get("access_token")
    print("Token obtenido:", access_token)
else:
    print("Error autenticando:", response.text)
    exit()

# Cargar el archivo JSON con los usuarios
with open("users.json", "r", encoding="utf-8") as f:
    usuarios = json.load(f)

# Iterar sobre cada usuario y realizar la importación
for usuario in usuarios:
    # Mapea los campos del JSON a los campos del módulo de SuiteCRM.
    # Ajusta los nombres de campos según la configuración de tu SuiteCRM.
    payload = {
        "data": {
            "type": "Accounts",
            "attributes": {
                "name": usuario.get("name"),
                "last_name_c": usuario.get("lastName"),
                "phone_mobile_c": usuario.get("cell"),
                "email1": usuario.get("mail"),
                "forecast_bulletin_c": usuario.get("forecastBulletin"),
                "clima_bulletin_c": usuario.get("climaBulletin"),
                "primary_address_city_c": usuario.get("location")
            },
        }
    }

    # Se utiliza el módulo Contacts en este ejemplo. Si deseas otro módulo, cambia "Contacts" por el nombre correspondiente.
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    create_url = f"{BASE_URL}/legacy/Api/V8/module"
    r = requests.post(create_url, json=payload, headers=headers, verify=False)
    if r.status_code in [200, 201]:
        print(f"Usuario {usuario.get('name')} {usuario.get('lastName')} importado correctamente.")
    else:
        print(f"Error al importar usuario {usuario.get('name')} {usuario.get('lastName')}: {r.text}")
        break
