import os
import hvac

def get_db_credentials():
    client = hvac.Client(url=os.environ.get('VAULT_ADDR'), token='roottoken')
    if not client.is_authenticated():
        raise Exception("Vault client is not authenticated!")
    try:
        secret = client.secrets.kv.read_secret_version(path='database/creds')
    except hvac.exceptions.InvalidRequest as e:
        raise Exception("Failed to read secret from Vault: {}".format(e))
    
    db_user = secret['data']['data']['SQL_USER']
    db_password = secret['data']['data']['SQL_PASSWORD']
    db_service = os.environ.get('DATABASE')
    db_port = os.environ.get('SQL_PORT')
    db_name = os.environ.get('SQL_DATABASE')
    os.environ['SQL_USER'] = db_user
    os.environ['SQL_PASSWORD'] = db_password
    os.environ['DATABASE_URL'] = f'postgres://{db_user}:{db_password}@{db_service}:{db_port}/{db_name}'