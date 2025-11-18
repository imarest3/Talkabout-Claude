# Talkabout Frontend

Frontend de la aplicación Talkabout construido con React y Material-UI.

## Tecnologías

- **React 18** - Framework UI
- **Material-UI 5** - Librería de componentes
- **React Router 6** - Navegación
- **Axios** - Cliente HTTP
- **date-fns** - Manejo de fechas

## Estructura del Proyecto

```
frontend/
├── public/
│   ├── index.html
│   └── manifest.json
├── src/
│   ├── components/      # Componentes reutilizables
│   │   ├── Navbar.js
│   │   └── PrivateRoute.js
│   ├── contexts/        # Context API
│   │   └── AuthContext.js
│   ├── pages/           # Páginas de la aplicación
│   │   ├── Login.js
│   │   ├── Register.js
│   │   ├── Home.js
│   │   ├── Activities.js
│   │   ├── ActivityDetail.js
│   │   ├── MyActivities.js
│   │   ├── MyEnrollments.js
│   │   └── Statistics.js
│   ├── services/        # Servicios API
│   │   └── api.js
│   ├── App.js           # Componente principal
│   ├── index.js         # Punto de entrada
│   └── index.css        # Estilos globales
├── Dockerfile
├── package.json
└── README.md
```

## Configuración

### Variables de Entorno

Crear archivo `.env` en la raíz del frontend:

```env
REACT_APP_API_URL=http://localhost:8000/api
```

## Desarrollo

### Con Docker

```bash
docker-compose up frontend
```

### Sin Docker

```bash
# Instalar dependencias
npm install

# Iniciar servidor de desarrollo
npm start

# Build para producción
npm run build
```

La aplicación estará disponible en http://localhost:3000

## Páginas

### Públicas
- **/login** - Inicio de sesión
- **/register** - Registro de usuario

### Privadas (Requieren autenticación)
- **/** - Página principal
- **/activities** - Listado de actividades
- **/activities/:id** - Detalle de actividad y eventos
- **/my-enrollments** - Inscripciones del usuario
- **/statistics** - Estadísticas personales

### Para Profesores
- **/my-activities** - Gestión de actividades propias

### Para Administradores
- **/admin** - Panel de administración

## Características

### Autenticación
- Login/Registro
- JWT con refresh token automático
- Roles de usuario (Admin, Teacher, Student)
- Rutas protegidas por rol

### Estudiantes
- Ver actividades disponibles
- Inscribirse a eventos
- Acceder a reuniones virtuales
- Ver estadísticas personales
- Cancelar inscripciones

### Profesores
- Crear y gestionar actividades
- Programar eventos
- Ver inscripciones
- Acceder a estadísticas detalladas
- Subir archivos a actividades

### Administradores
- Acceso completo a todas las funcionalidades
- Panel de administración
- Estadísticas globales

## API Service

El servicio de API (`src/services/api.js`) proporciona:

- Interceptores para agregar tokens automáticamente
- Refresh automático de tokens expirados
- Métodos organizados por recurso:
  - `authAPI` - Autenticación
  - `activitiesAPI` - Actividades
  - `eventsAPI` - Eventos
  - `enrollmentsAPI` - Inscripciones
  - `meetingsAPI` - Reuniones
  - `statisticsAPI` - Estadísticas

## Context API

### AuthContext

Proporciona:
- Estado de autenticación
- Usuario actual
- Funciones de login/logout
- Funciones de registro
- Helpers de rol (`isAdmin`, `isTeacher`, `isStudent`)

Uso:
```javascript
import { useAuth } from '../contexts/AuthContext';

function MyComponent() {
  const { user, isTeacher, logout } = useAuth();
  // ...
}
```

## Componentes

### PrivateRoute
Protege rutas que requieren autenticación o roles específicos

### PublicRoute
Rutas accesibles solo para usuarios no autenticados

### Navbar
Barra de navegación con enlaces contextuales según rol

## Navegación

La navegación se adapta según el rol del usuario:

**Estudiante:**
- Inicio
- Actividades
- Mis Inscripciones
- Estadísticas
- Perfil

**Profesor:**
- Todo lo anterior +
- Mis Actividades
- Gestión de eventos

**Administrador:**
- Todo lo anterior +
- Panel Admin
- Estadísticas globales

## Build

Para crear un build de producción:

```bash
npm run build
```

Esto creará una carpeta `build/` con los archivos optimizados.

## Testing

```bash
npm test
```

## Notas

- El frontend usa proxy para desarrollo (configurado en package.json)
- Los tokens se almacenan en localStorage
- Las fechas se muestran en español (date-fns locale)
- Material-UI proporciona tema personalizable
- Responsive design para móviles y tablets
