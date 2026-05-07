from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
import jwt
import os
from sqlalchemy import create_engine, text
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


@router.post('/rows')
async def get_table_rows(request: Request):
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
    limit = data.get('limit', 10)
    order = data.get('order', 'oldest')  # 'oldest' o 'newest'

    if not table_name:
        return JSONResponse(
            status_code=400,
            content={"CONECCION": "Error", "DETAIL": "Missing table_name"}
        )

    if not isinstance(limit, int) or limit <= 0:
        return JSONResponse(
            status_code=400,
            content={"CONECCION": "Error", "DETAIL": "limit must be a positive integer"}
        )

    if order not in ['oldest', 'newest']:
        return JSONResponse(
            status_code=400,
            content={"CONECCION": "Error", "DETAIL": "order must be 'oldest' or 'newest'"}
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
        order_direction = 'ASC' if order == 'oldest' else 'DESC'
        query = f"SELECT * FROM `{table_name}` ORDER BY 1 {order_direction} LIMIT {limit}"

        engine = create_engine(f'{db_type}://{db_user}:{db_pass}@{db_host}/{db_name}')
        with engine.connect() as conn:
            result = conn.execute(text(query))
            columns = [column for column in result.keys()]
            rows = [dict(zip(columns, row)) for row in result]

        return {
            "CONECCION": "Exitosa",
            "TABLE": table_name,
            "COLUMNS": columns,
            "ROWS": rows,
            "COUNT": len(rows)
        }
    except Exception as e:
        return {"CONECCION": "Error", "DETAIL": str(e)}
