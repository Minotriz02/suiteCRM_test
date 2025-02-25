import requests
import json

# Configuración base: ajusta la URL según tu entorno
BASE_URL = "https://localhost"  # Usa la IP/hostname y puerto mapeado
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

# Definir encabezados comunes
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

# Cargar el archivo JSON con los usuarios
with open("users.json", "r", encoding="utf-8") as f:
    usuarios = json.load(f)

# Función para obtener un registro existente por celular
def obtener_registro_por_celular(phone):
    # Se crea el filtro; en este ejemplo, se usa el campo phone_mobile_c
    url = f"{BASE_URL}/legacy/Api/V8/module/Accounts?filter[phone_mobile_c][eq]={phone}"
    resp = requests.get(url, headers=headers, verify=False)
    if resp.status_code == 200:
        data = resp.json().get("data", [])
        if data:
            return data[0]  # Se asume que el teléfono es único
    return None

# Función para comparar registros teniendo en cuenta que en SuiteCRM
# true se almacena como 1 y false como 0.
def registros_diferentes(nuevos, existentes):
    # Lista de campos a comparar
    campos = ["name", "last_name_c", "phone_mobile_c", "mail_c",
              "forecast_bulletin_c", "clima_bulletin_c", "primary_address_city_c"]
    for campo in campos:
        if campo in ["forecast_bulletin_c", "clima_bulletin_c"]:
            # Convertir el valor a 1 si es equivalente a verdadero, 0 si es falso
            valor_nuevo = 1 if str(nuevos.get(campo, "")).strip() in ["1", "True", "true"] else 0
            valor_existente = 1 if str(existentes.get(campo, "")).strip() in ["1", "True", "true"] else 0
        else:
            valor_nuevo = str(nuevos.get(campo, "")).strip()
            valor_existente = str(existentes.get(campo, "")).strip()
        # Puedes imprimir la comparación para depuración:
        # print(f"{campo}: {valor_nuevo} --- {valor_existente}")
        if valor_nuevo != valor_existente:
            return True
    return False

# Inicialización de contadores para el resumen final
registros_actualizados = 0
registros_creados = 0
registros_sin_cambios = 0

# Iterar sobre cada usuario y realizar la importación/actualización
for usuario in usuarios:
    # Construir el payload con los datos a insertar/actualizar
    nuevos_atributos = {
        "name": usuario.get("name"),
        "last_name_c": usuario.get("last_name_c"),
        "phone_mobile_c": usuario.get("phone_mobile_c"),
        "mail_c": usuario.get("mail_c"),
        "forecast_bulletin_c": usuario.get("forecast_bulletin_c"),
        "clima_bulletin_c": usuario.get("clima_bulletin_c"),
        "primary_address_city_c": usuario.get("primary_address_city_c")
    }
    
    # Buscar registro existente en Accounts, usando el celular como clave
    registro_existente = obtener_registro_por_celular(usuario.get("phone_mobile_c"))
    
    if registro_existente:
        # Registro ya existe; comparar campos
        atributos_existentes = registro_existente.get("attributes", {})
        if registros_diferentes(nuevos_atributos, atributos_existentes):
            # Se detectaron diferencias; se actualiza el registro
            record_id = registro_existente.get("id")
            payload_update = {
                "data": {
                    "type": "Accounts",
                    "id": record_id,
                    "attributes": nuevos_atributos
                }
            }
            update_url = f"{BASE_URL}/legacy/Api/V8/module"
            r = requests.patch(update_url, json=payload_update, headers=headers, verify=False)
            if r.status_code in [200, 201]:
                print(f"Registro actualizado para {usuario.get('name')}.")
                registros_actualizados += 1
            else:
                print(f"Error al actualizar registro para {usuario.get('name')}: {r.text}")
        else:
            print(f"Registro para {usuario.get('name')} ya está actualizado.")
            registros_sin_cambios += 1
    else:
        # No existe, se crea el registro
        payload_create = {
            "data": {
                "type": "Accounts",
                "attributes": nuevos_atributos
            }
        }
        create_url = f"{BASE_URL}/legacy/Api/V8/module"
        r = requests.post(create_url, json=payload_create, headers=headers, verify=False)
        if r.status_code in [200, 201]:
            print(f"Registro creado para {usuario.get('name')}.")
            registros_creados += 1
        else:
            print(f"Error al crear registro para {usuario.get('name')}: {r.text}")
            break

# Comentario final con resumen de la operación
print("\nResumen final:")
print(f"Registros actualizados: {registros_actualizados}")
print(f"Registros creados: {registros_creados}")
print(f"Registros sin cambios: {registros_sin_cambios}")
