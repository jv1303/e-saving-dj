from pymongo import MongoClient
from django.conf import settings
import os

def init_mongodb():
    """Inicializa conexão com MongoDB"""
    mongodb_uri = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/')
    db_name = os.environ.get('MONGODB_DB_NAME', 'e_saving_db')
    
    try:
        client = MongoClient(mongodb_uri)
        db = client[db_name]
        
        # Criar coleções se não existirem
        collections = db.list_collection_names()
        if 'users' not in collections:
            db.create_collection('users')
            db.users.create_index('username', unique=True)
            db.users.create_index('email', unique=True)
            db.users.create_index('cpf_cnpj', unique=True)
        
        if 'coletas' not in collections:
            db.create_collection('coletas')
            db.coletas.create_index('ponto_username')
            db.coletas.create_index([('ponto_username', 1), ('data', -1)])
        
        print(f"MongoDB inicializado: {db_name}")
        return db
    except Exception as e:
        print(f"Erro ao conectar ao MongoDB: {e}")
        return None

mongodb_db = init_mongodb()