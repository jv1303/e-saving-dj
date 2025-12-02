from django.shortcuts import render, redirect
from django.contrib import messages
from pymongo import MongoClient
from bson.objectid import ObjectId # <--- Adicione esta importação

# --- Configuração do MongoDB ---
# (Baseado no seu arquivo prototype_crud.py)
try:
    client = MongoClient("mongodb+srv://e-user:bMJFcaInfgqDhXU4qt@e-cluster.cddvcah.mongodb.net/")
    db = client.get_database("e-saving")
    user_collection = db.get_collection("user")
    print("✅ Conexão com MongoDB estabelecida!")
except Exception as e:
    print(f"❌ Erro ao conectar ao MongoDB: {e}")

# --- Views ---

def home(request):
    return render(request, 'home.html')

def register_user(request):
    if request.method == 'POST':
        try:
            # 1. Capturar dados do formulário HTML
            # Os nomes aqui (ex: 'name', 'cpf') devem bater com o 'name="..."' do input no HTML
            name = request.POST.get('name')
            cpf = request.POST.get('cpf')
            phone = request.POST.get('phone')
            email = request.POST.get('email')
            zip_code = request.POST.get('zip_code')
            password_raw = request.POST.get('password')

            # 2. Validações Básicas
            # No seu protótipo, a senha era tratada como INT
            try:
                password = int(password_raw)
            except ValueError:
                messages.error(request, "A senha deve conter apenas números.")
                return render(request, 'register.html')

            # Verifica se o e-mail já existe
            if user_collection.find_one({"email": email}):
                messages.warning(request, "Este e-mail já está cadastrado.")
                return render(request, 'register.html')

            # 3. Preparar o objeto para salvar (igual ao prototype_crud.py)
            user_data = {
                "name": name,
                "profile_picture": "", # Campo não existe no form ainda, enviando vazio
                "email": email,
                "password": password,
                "phone": phone,
                "zip_code": zip_code,
                "cpf": cpf
            }

            # 4. Inserir no Banco
            user_collection.insert_one(user_data)
            
            # 5. Sucesso!
            messages.success(request, f"Bem-vindo(a), {name}! Cadastro realizado com sucesso.")
            return redirect('home')

        except Exception as e:
            messages.error(request, f"Ocorreu um erro no sistema: {e}")
            return render(request, 'register.html')

    # Se for GET (apenas abrir a página), mostra o formulário vazio
    return render(request, 'register.html')

# ... (imports existentes)

def login_user(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password_input = request.POST.get('password')

        try:
            # Converter senha para int para bater com o formato do banco
            password = int(password_input)
        except ValueError:
            messages.error(request, "A senha deve conter apenas números.")
            return render(request, 'login.html')

        # Procura usuário com esse email e senha
        user = user_collection.find_one({"email": email, "password": password})

        if user:
            # SUCESSO: Salva os dados na sessão do navegador
            # Convertemos o ID para string pois o Django não guarda ObjectId nativamente
            request.session['user_id'] = str(user['_id'])
            request.session['user_name'] = user['name']
            
            messages.success(request, f"Bem-vindo de volta, {user['name']}!")
            return redirect('home')
        else:
            messages.error(request, "E-mail ou senha incorretos.")

    return render(request, 'login.html')

def logout_user(request):
    # Limpa a sessão (desloga o usuário)
    request.session.flush()
    return redirect('home')

def user_area(request):
    # Verifica se usuário está logado
    if 'user_id' not in request.session:
        return redirect('login_user')
    
    user_id = request.session['user_id']
    
    try:
        # Busca dados atualizados no Mongo
        user = user_collection.find_one({"_id": ObjectId(user_id)})
        return render(request, 'user_area.html', {'user': user})
    except Exception as e:
        messages.error(request, f"Erro ao carregar perfil: {e}")
        return redirect('home')

def update_user(request):
    if request.method == 'POST' and 'user_id' in request.session:
        user_id = request.session['user_id']
        
        try:
            # Captura dados
            updated_data = {
                "name": request.POST.get('name'),
                "email": request.POST.get('email'),
                "cpf": request.POST.get('cpf'),
                "phone": request.POST.get('phone'),
                "zip_code": request.POST.get('zip_code'),
                "password": int(request.POST.get('password'))
            }
            
            # Atualiza no Mongo
            user_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": updated_data}
            )
            
            # Atualiza nome na sessão caso tenha mudado
            request.session['user_name'] = updated_data['name']
            
            messages.success(request, "Dados atualizados com sucesso!")
        except ValueError:
            messages.error(request, "A senha deve ser numérica.")
        except Exception as e:
            messages.error(request, f"Erro ao atualizar: {e}")
            
    return redirect('user_area')

def delete_user(request):
    if request.method == 'POST' and 'user_id' in request.session:
        user_id = request.session['user_id']
        
        try:
            # Remove do banco
            user_collection.delete_one({"_id": ObjectId(user_id)})
            
            # Limpa sessão (Logout)
            request.session.flush()
            messages.success(request, "Sua conta foi excluída com sucesso.")
        except Exception as e:
            messages.error(request, f"Erro ao excluir conta: {e}")
            return redirect('user_area')
            
    return redirect('home')
