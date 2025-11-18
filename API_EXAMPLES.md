# API Examples

Esta guía proporciona ejemplos de uso de la API de Talkabout.

## Autenticación

### Registrar nuevo usuario

```bash
curl -X POST http://localhost:8000/api/auth/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "SecurePass123!",
    "password_confirm": "SecurePass123!",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

### Obtener token JWT

```bash
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "password": "SecurePass123!"
  }'
```

Respuesta:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Refrescar token

```bash
curl -X POST http://localhost:8000/api/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }'
```

### Obtener perfil actual

```bash
curl -X GET http://localhost:8000/api/auth/users/me/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Actividades

### Listar actividades

```bash
curl -X GET http://localhost:8000/api/activities/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Crear actividad (Teacher)

```bash
curl -X POST http://localhost:8000/api/activities/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Conversación en Español",
    "description": "Practica tu español con temas cotidianos",
    "max_participants_per_meeting": 6,
    "min_participants_per_meeting": 3
  }'
```

### Ver detalle de actividad

```bash
curl -X GET http://localhost:8000/api/activities/1/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Subir archivo a actividad

```bash
curl -X POST http://localhost:8000/api/activities/1/upload_file/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@/path/to/file.pdf"
```

## Eventos

### Listar eventos

```bash
# Todos los eventos
curl -X GET http://localhost:8000/api/events/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Solo eventos próximos
curl -X GET "http://localhost:8000/api/events/?upcoming=true" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Eventos de una actividad específica
curl -X GET "http://localhost:8000/api/events/?activity_id=1" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Crear evento (Teacher)

```bash
curl -X POST http://localhost:8000/api/events/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "activity": 1,
    "start_time": "2024-12-15T10:00:00Z",
    "end_time": "2024-12-15T11:00:00Z"
  }'
```

### Ver inscripciones de un evento (Teacher/Admin)

```bash
curl -X GET http://localhost:8000/api/events/1/enrollments/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Inscripciones

### Inscribirse a un evento

```bash
curl -X POST http://localhost:8000/api/enrollments/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "event": 1
  }'
```

### Ver mis inscripciones

```bash
# Todas
curl -X GET http://localhost:8000/api/enrollments/my_enrollments/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Solo próximas
curl -X GET "http://localhost:8000/api/enrollments/my_enrollments/?upcoming=true" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Cancelar inscripción

```bash
curl -X POST http://localhost:8000/api/enrollments/1/cancel/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Reuniones

### Listar reuniones

```bash
curl -X GET http://localhost:8000/api/meetings/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Ver detalle de reunión

```bash
curl -X GET http://localhost:8000/api/meetings/1/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Unirse a reunión

```bash
curl -X POST http://localhost:8000/api/meetings/1/join/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Salir de reunión

```bash
curl -X POST http://localhost:8000/api/meetings/1/leave/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Estadísticas

### Estadísticas de actividades (Teacher/Admin)

```bash
curl -X GET http://localhost:8000/api/statistics/activities/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Estadísticas de eventos (Teacher/Admin)

```bash
# Todos los eventos
curl -X GET http://localhost:8000/api/statistics/events/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Eventos de una actividad
curl -X GET "http://localhost:8000/api/statistics/events/?activity_id=1" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Estadísticas de usuarios (Admin)

```bash
curl -X GET http://localhost:8000/api/statistics/users/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Mis estadísticas

```bash
curl -X GET http://localhost:8000/api/statistics/my_stats/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Ejemplos con Python

### Usando requests

```python
import requests

# Base URL
BASE_URL = "http://localhost:8000/api"

# Login
response = requests.post(
    f"{BASE_URL}/auth/token/",
    json={
        "username": "johndoe",
        "password": "SecurePass123!"
    }
)
tokens = response.json()
access_token = tokens['access']

# Headers con autenticación
headers = {
    "Authorization": f"Bearer {access_token}"
}

# Listar actividades
response = requests.get(
    f"{BASE_URL}/activities/",
    headers=headers
)
activities = response.json()

# Crear inscripción
response = requests.post(
    f"{BASE_URL}/enrollments/",
    headers=headers,
    json={"event": 1}
)
enrollment = response.json()
```

### Usando httpx (async)

```python
import httpx
import asyncio

async def main():
    async with httpx.AsyncClient() as client:
        # Login
        response = await client.post(
            "http://localhost:8000/api/auth/token/",
            json={
                "username": "johndoe",
                "password": "SecurePass123!"
            }
        )
        tokens = response.json()

        # Headers
        headers = {
            "Authorization": f"Bearer {tokens['access']}"
        }

        # Get activities
        response = await client.get(
            "http://localhost:8000/api/activities/",
            headers=headers
        )
        activities = response.json()
        print(activities)

asyncio.run(main())
```

## Ejemplos con JavaScript

### Usando fetch

```javascript
const BASE_URL = 'http://localhost:8000/api';

// Login
async function login(username, password) {
    const response = await fetch(`${BASE_URL}/auth/token/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
    });
    return await response.json();
}

// Get activities
async function getActivities(accessToken) {
    const response = await fetch(`${BASE_URL}/activities/`, {
        headers: {
            'Authorization': `Bearer ${accessToken}`
        }
    });
    return await response.json();
}

// Enroll in event
async function enrollInEvent(accessToken, eventId) {
    const response = await fetch(`${BASE_URL}/enrollments/`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${accessToken}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ event: eventId })
    });
    return await response.json();
}

// Usage
(async () => {
    const tokens = await login('johndoe', 'SecurePass123!');
    const activities = await getActivities(tokens.access);
    console.log(activities);
})();
```

### Usando axios

```javascript
import axios from 'axios';

const api = axios.create({
    baseURL: 'http://localhost:8000/api'
});

// Login
const login = async (username, password) => {
    const response = await api.post('/auth/token/', {
        username,
        password
    });
    return response.data;
};

// Set token
const setAuthToken = (token) => {
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
};

// Get activities
const getActivities = async () => {
    const response = await api.get('/activities/');
    return response.data;
};

// Usage
(async () => {
    const tokens = await login('johndoe', 'SecurePass123!');
    setAuthToken(tokens.access);
    const activities = await getActivities();
    console.log(activities);
})();
```

## Códigos de Estado HTTP

- `200 OK` - Solicitud exitosa
- `201 Created` - Recurso creado exitosamente
- `204 No Content` - Solicitud exitosa sin contenido de respuesta
- `400 Bad Request` - Datos inválidos
- `401 Unauthorized` - No autenticado
- `403 Forbidden` - Sin permisos
- `404 Not Found` - Recurso no encontrado
- `500 Internal Server Error` - Error del servidor

## Paginación

Las listas están paginadas. Respuesta típica:

```json
{
  "count": 42,
  "next": "http://localhost:8000/api/activities/?page=2",
  "previous": null,
  "results": [...]
}
```

Parámetros de query:
- `page`: Número de página
- `page_size`: Elementos por página (máx 100)
