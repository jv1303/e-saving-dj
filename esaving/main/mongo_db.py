from django.conf import settings
from datetime import datetime
import hashlib

class MongoDBManager:
    """Gerenciador de operações no MongoDB"""
    
    @staticmethod
    def get_db():
        """Retorna a conexão com o MongoDB"""
        # Comparar explicitamente com None, não usar "if not db"
        return getattr(settings, 'MONGO_DB', None)
    
    @staticmethod
    def criar_usuario(user_data):
        """Cria um novo usuário no MongoDB"""
        db = MongoDBManager.get_db()
        if db is None:
            return None
        
        users = db['users']
        
        # Verificar se já existe
        if users.find_one({"username": user_data['username']}):
            raise ValueError("Nome de usuário já existe")
        if users.find_one({"email": user_data['email']}):
            raise ValueError("E-mail já cadastrado")
        if users.find_one({"cpf_cnpj": user_data['cpf_cnpj']}):
            raise ValueError("CPF/CNPJ já cadastrado")
        
        # Adicionar timestamps
        user_data['created_at'] = datetime.now()
        user_data['updated_at'] = datetime.now()
        
        # Hash da senha
        if 'password' in user_data:
            user_data['password'] = hashlib.sha256(user_data['password'].encode()).hexdigest()
        
        result = users.insert_one(user_data)
        return str(result.inserted_id)
    
    @staticmethod
    def buscar_usuario_por_username(username):
        """Busca usuário por username"""
        db = MongoDBManager.get_db()
        if db is None:
            return None
        
        users = db['users']
        user = users.find_one({"username": username})
        
        if user and '_id' in user:
            user['id'] = str(user['_id'])
            del user['_id']
        
        return user
    
    @staticmethod
    def autenticar_usuario(username, password):
        """Autentica usuário"""
        db = MongoDBManager.get_db()
        if db is None:
            return None
        
        users = db['users']
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        user = users.find_one({
            "username": username,
            "password": password_hash
        })
        
        if user and '_id' in user:
            user['id'] = str(user['_id'])
            del user['_id']
        
        return user
    
    @staticmethod
    def listar_pontos_coleta():
        """Lista todos os pontos de coleta"""
        db = MongoDBManager.get_db()
        if db is None:
            return []
        
        users = db['users']
        pontos = list(users.find({}, {
            'username': 1,
            'email': 1,
            'telefone': 1,
            'cep': 1,
            'endereco': 1,
            'tipos_residuos': 1,
            'horario_funcionamento': 1,
            'latitude': 1,
            'longitude': 1,
            'created_at': 1
        }))
        
        for ponto in pontos:
            if '_id' in ponto:
                ponto['id'] = str(ponto['_id'])
                del ponto['_id']
            if 'created_at' in ponto and isinstance(ponto['created_at'], datetime):
                ponto['created_at'] = ponto['created_at'].strftime('%d/%m/%Y %H:%M')
        
        return pontos
    
    @staticmethod
    def criar_coleta(coleta_data):
        """Registra uma nova coleta"""
        db = MongoDBManager.get_db()
        if db is None:
            return None
        
        coletas = db['coletas']
        coleta_data['created_at'] = datetime.now()
        
        result = coletas.insert_one(coleta_data)
        return str(result.inserted_id)
    
    @staticmethod
    def buscar_coletas_por_ponto(username):
        """Busca coletas de um ponto específico"""
        db = MongoDBManager.get_db()
        if db is None:
            return []
        
        coletas = db['coletas']
        resultados = list(coletas.find({"ponto_username": username}).sort("created_at", -1))
        
        for coleta in resultados:
            if '_id' in coleta:
                coleta['id'] = str(coleta['_id'])
                del coleta['_id']
            if 'created_at' in coleta and isinstance(coleta['created_at'], datetime):
                coleta['created_at'] = coleta['created_at'].strftime('%d/%m/%Y %H:%M')
        
        return resultados
    
    @staticmethod
    def atualizar_usuario(username, dados_atualizacao):
        """Atualiza dados de um usuário"""
        db = MongoDBManager.get_db()
        if db is None:
            return False
        
        users = db['users']
        dados_atualizacao['updated_at'] = datetime.now()
        
        result = users.update_one(
            {"username": username},
            {"$set": dados_atualizacao}
        )
        
        return result.modified_count > 0