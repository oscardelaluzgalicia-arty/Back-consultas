# Back-Consultas

Proyecto backend en Python para consultas a bases de datos SQL dinámicas, desplegado en Vercel.

## Descripción

Esta aplicación recibe configuraciones de conexión a base de datos vía POST desde una app Android y realiza operaciones como verificación de conexión y consultas para generar archivos Excel.

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
