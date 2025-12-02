from django.shortcuts import render, redirect
from django.contrib import messages
from pymongo import MongoClient

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
