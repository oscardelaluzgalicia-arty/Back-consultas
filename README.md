# Back-Consultas

Proyecto backend en Python para consultas a bases de datos SQL dinámicas, desplegado en Vercel.

## Descripción

Esta API funciona como una capa intermedia segura entre una aplicación móvil y distintos motores de bases de datos SQL. Permite conexiones dinámicas usando credenciales proporcionadas por el cliente, valida la conexión, genera un token JWT y ofrece endpoints para:

- verificar la conexión,
- listar tablas,
- describir la estructura de una tabla,
- ejecutar consultas seguras de solo lectura.

La arquitectura utiliza SQLAlchemy y soporta motores como MySQL y PostgreSQL.

## Endpoints

### `GET /`
- Propósito: comprobar que el servicio está en línea.
- Respuesta: `{"status": "online"}`

### `POST /api/verify`
- Propósito: comprobar la conexión a la base de datos y generar un token JWT.
- Request JSON:
  - `dbType` (opcional, por defecto `mysql+pymysql`)
  - `dbHost`
  - `dbUser`
  - `dbPass`
  - `dbName`
- Respuesta exitosa:
  - `{"CONECCION": "Exitosa", "TOKEN": "jwt_token"}`
- Respuesta de error:
  - `{"CONECCION": "Error", "DETAIL": "..."}`

### `POST /api/tables`
- Propósito: listar las tablas disponibles en la base de datos.
- Autenticación: header `Authorization: Bearer <token>`.
- Respuesta exitosa:
  - `{"CONECCION": "Exitosa", "TABLES": ["tabla1", "tabla2", ...]}`
- Soporta MySQL y PostgreSQL.

### `POST /api/describe`
- Propósito: describir la estructura de una tabla específica.
- Autenticación: header `Authorization: Bearer <token>`.
- Request JSON:
  - `table_name`
- Respuesta exitosa:
  - `{
      "CONECCION": "Exitosa",
      "TABLE": "nombre_tabla",
      "COLUMNS": [
        {"name": "id", "type": "INT", "nullable": false, "default": null},
        ...
      ],
      "PRIMARY_KEY": ["id"],
      "COLUMN_COUNT": 5
    }`

### `POST /api/query`
- Propósito: ejecutar consultas de solo lectura por tabla con columnas, límite y orden.
- Autenticación: header `Authorization: Bearer <token>`.
- Request JSON:
  - `queries`: lista de objetos con:
    - `table`: nombre de la tabla
    - `columns`: lista de columnas a consultar
    - `limit`: número de filas a devolver (entero positivo)
    - `order`: `oldest` o `newest`
- Respuesta exitosa:
  - `{
      "CONECCION": "Exitosa",
      "RESULTS": [
        {
          "table": "tabla1",
          "CONECCION": "Exitosa",
          "COLUMNS": ["col1", "col2"],
          "ROWS": [
            {"col1": "valor1", "col2": "valor2"},
            ...
          ],
          "COUNT": 2
        }
      ],
      "TOTAL_QUERIES": 1,
      "SUCCESSFUL_QUERIES": 1
    }`
- Maneja errores por tabla si la tabla no existe, las columnas son inválidas o los filtros son incorrectos.

## Instalación

1. Clona el repositorio.
2. Instala dependencias: `pip install -r requirements.txt`
3. Configura Vercel o ejecuta localmente con `uvicorn app.main:app --reload`.

## Uso

1. Llama a `POST /api/verify` con credenciales válidas para obtener el `token`.
2. Usa `Authorization: Bearer <token>` en los headers de las solicitudes a `/api/tables`, `/api/describe` y `/api/query`.
3. Envía JSON válido según el endpoint.

## Notas

- El token JWT expira en 1 hora.
- El servicio es de solo lectura y protege las credenciales de base de datos dentro del backend.
