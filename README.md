# Back-Consultas

Proyecto backend en Python para consultas a bases de datos SQL dinámicas, desplegado en Vercel.

## Descripción

Esta API funciona como una capa intermedia segura entre una aplicación Android y distintos motores de bases de datos SQL. Su propósito es permitir conexiones dinámicas a bases de datos remotas utilizando credenciales proporcionadas por el usuario, procesando las consultas desde el backend en Python y devolviendo resultados estructurados en formatos como JSON o Excel.

La arquitectura está diseñada para trabajar con múltiples motores SQL compatibles con SQLAlchemy, como MySQL y PostgreSQL, permitiendo realizar consultas de solo lectura sobre tablas específicas sin exponer directamente la base de datos al cliente móvil.

## Endpoints

- `POST /api/verify`: Verifica la conexión a la base de datos y genera un token JWT si es exitosa.
  - Request: JSON con `dbType`, `dbHost`, `dbUser`, `dbPass`, `dbName`
  - Response: `{"CONECCION": "Exitosa", "TOKEN": "jwt_token"}` o `{"CONECCION": "Error"}`

## Instalación

1. Clona el repositorio.
2. Instala dependencias: `pip install -r requirements.txt`
3. Configura Vercel: `vercel`

## Uso

Envía POST a los endpoints con JSON correspondiente.
