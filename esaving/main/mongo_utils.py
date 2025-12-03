from django.conf import settings
from bson import ObjectId
from datetime import datetime

def get_mongo_collection(collection_name):
    """Retorna uma coleção do MongoDB"""
    if hasattr(settings, 'MONGO_DB') and settings.MONGO_DB:
        return settings.MONGO_DB[collection_name]
    return None

def object_id_to_str(obj):
    """Converte ObjectId para string em dicionários"""
    if isinstance(obj, dict):
        if '_id' in obj and isinstance(obj['_id'], ObjectId):
            obj['_id'] = str(obj['_id'])
        return obj
    return obj

# Coleções do MongoDB
USERS_COLLECTION = 'users'
COLETAS_COLLECTION = 'coletas'