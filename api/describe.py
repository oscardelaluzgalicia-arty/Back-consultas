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


@router.post('/describe')
async def describe_table(request: Request):
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

    table_name = data.get('table_name')

    if not table_name:
        return JSONResponse(
            status_code=400,
            content={"CONECCION": "Error", "DETAIL": "Missing table_name"}
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
        
        if table_name not in inspector.get_table_names():
            return JSONResponse(
                status_code=404,
                content={"CONECCION": "Error", "DETAIL": f"Table '{table_name}' not found"}
            )

        columns_info = []
        for column in inspector.get_columns(table_name):
            columns_info.append({
                "name": column['name'],
                "type": str(column['type']),
                "nullable": column['nullable'],
                "default": str(column['default']) if column['default'] is not None else None
            })

        primary_keys = inspector.get_pk_constraint(table_name)

        return {
            "CONECCION": "Exitosa",
            "TABLE": table_name,
            "COLUMNS": columns_info,
            "PRIMARY_KEY": primary_keys.get('constrained_columns', []),
            "COLUMN_COUNT": len(columns_info)
        }
    except Exception as e:
        return {"CONECCION": "Error", "DETAIL": str(e)}
