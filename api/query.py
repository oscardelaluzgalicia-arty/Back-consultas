from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
import jwt
import os
from sqlalchemy import create_engine, text, inspect
from jwt import ExpiredSignatureError, InvalidTokenError

router = APIRouter()


def verify_token(token: str):
    secret_key = os.getenv('JWT_SECRET', 'my_secret_key')
    try:
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        return payload
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='Token expired')
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail='Invalid token')


@router.post('/query')
async def execute_queries(request: Request):
    auth_header = request.headers.get('authorization') or request.headers.get('Authorization')
    
    if not auth_header or not auth_header.lower().startswith('bearer '):
        return JSONResponse(
            status_code=401,
            content={"CONECCION": "Error", "DETAIL": "Missing or invalid Authorization header"}
        )
    
    token = auth_header.split(' ', 1)[1].strip()

    try:
        payload = verify_token(token)
    except HTTPException as exc:
        return JSONResponse(
            status_code=exc.status_code,
            content={"CONECCION": "Error", "DETAIL": exc.detail}
        )

    try:
        data = await request.json()
    except:
        return JSONResponse(
            status_code=400,
            content={"CONECCION": "Error", "DETAIL": "Invalid JSON"}
        )

    queries = data.get('queries', [])

    if not queries or not isinstance(queries, list):
        return JSONResponse(
            status_code=400,
            content={"CONECCION": "Error", "DETAIL": "Missing or invalid 'queries' array"}
        )

    db_type = payload.get('dbType', 'mysql+pymysql')
    db_host = payload.get('dbHost')
    db_user = payload.get('dbUser')
    db_pass = payload.get('dbPass')
    db_name = payload.get('dbName')

    if not all([db_host, db_user, db_pass, db_name]):
        return JSONResponse(
            status_code=400,
            content={"CONECCION": "Error", "DETAIL": "Invalid token payload"}
        )

    try:
        engine = create_engine(f'{db_type}://{db_user}:{db_pass}@{db_host}/{db_name}')
        inspector = inspect(engine)
        available_tables = inspector.get_table_names()

        results = []

        for query_obj in queries:
            table = query_obj.get('table')
            columns = query_obj.get('columns', [])
            limit = query_obj.get('limit', 10)
            order = query_obj.get('order', 'oldest')

            error = None

            if not table:
                error = "Missing table name"
            elif table not in available_tables:
                error = f"Table '{table}' not found"
            elif not columns or not isinstance(columns, list):
                error = "Missing or invalid 'columns' array"
            elif not isinstance(limit, int) or limit <= 0:
                error = "limit must be a positive integer"
            elif order not in ['oldest', 'newest']:
                error = "order must be 'oldest' or 'newest'"

            if error:
                results.append({
                    "table": table,
                    "CONECCION": "Error",
                    "DETAIL": error
                })
                continue

            try:
                table_columns = [col['name'] for col in inspector.get_columns(table)]
                invalid_columns = [col for col in columns if col not in table_columns]

                if invalid_columns:
                    results.append({
                        "table": table,
                        "CONECCION": "Error",
                        "DETAIL": f"Invalid columns: {', '.join(invalid_columns)}"
                    })
                    continue

                columns_str = ', '.join([f'`{col}`' for col in columns])
                order_direction = 'ASC' if order == 'oldest' else 'DESC'
                primary_key = inspector.get_pk_constraint(table).get('constrained_columns', [0])[0]
                sql_query = f"SELECT {columns_str} FROM `{table}` ORDER BY `{primary_key}` {order_direction} LIMIT {limit}"

                with engine.connect() as conn:
                    result = conn.execute(text(sql_query))
                    rows = [dict(zip(columns, row)) for row in result]

                results.append({
                    "table": table,
                    "CONECCION": "Exitosa",
                    "COLUMNS": columns,
                    "ROWS": rows,
                    "COUNT": len(rows)
                })

            except Exception as e:
                results.append({
                    "table": table,
                    "CONECCION": "Error",
                    "DETAIL": str(e)
                })

        return {
            "CONECCION": "Exitosa",
            "RESULTS": results,
            "TOTAL_QUERIES": len(queries),
            "SUCCESSFUL_QUERIES": sum(1 for r in results if r.get('CONECCION') == 'Exitosa')
        }

    except Exception as e:
        return {"CONECCION": "Error", "DETAIL": str(e)}
