import json
import jwt
import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text

def handler(request):
    if request.method != 'POST':
        return {
            'statusCode': 405,
            'body': json.dumps({'CONECCION': 'Error'})
        }

    try:
        data = request.get_json()
    except:
        return {
            'statusCode': 400,
            'body': json.dumps({'CONECCION': 'Error'})
        }

    db_type = data.get('dbType', 'mysql+pymysql')
    db_host = data.get('dbHost')
    db_user = data.get('dbUser')
    db_pass = data.get('dbPass')
    db_name = data.get('dbName')

    if not all([db_host, db_user, db_pass, db_name]):
        return {
            'statusCode': 400,
            'body': json.dumps({'CONECCION': 'Error'})
        }

    try:
        engine = create_engine(f'{db_type}://{db_user}:{db_pass}@{db_host}/{db_name}')
        
        # Verificar conexión con una query simple
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        # Generar token JWT con los datos de conexión
        secret_key = os.getenv('JWT_SECRET', 'my_secret_key')  # Usar variable de entorno en Vercel
        payload = {
            'dbType': db_type,
            'dbHost': db_host,
            'dbUser': db_user,
            'dbPass': db_pass,
            'dbName': db_name,
            'exp': datetime.utcnow() + timedelta(hours=1)
        }
        token = jwt.encode(payload, secret_key, algorithm='HS256')
        
        return {
            'statusCode': 200,
            'body': json.dumps({'CONECCION': 'Exitosa', 'TOKEN': token})
        }
    except Exception as e:
        return {
            'statusCode': 200,
            'body': json.dumps({'CONECCION': 'Error'})
        }