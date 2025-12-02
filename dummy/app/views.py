from django.shortcuts import render, redirect
from django.contrib import messages
from pymongo import MongoClient
from bson.objectid import ObjectId
import datetime

# --- 1. Configuração do MongoDB ---
# (String de conexão retirada do seu script prototype_crud.py)
try:
    client = MongoClient("mongodb+srv://e-user:bMJFcaInfgqDhXU4qt@e-cluster.cddvcah.mongodb.net/")
    db = client.get_database("e-saving")
    user_collection = db.get_collection("user")
    partner_collection = db.get_collection("partner")
    collection_point_collection = db.get_collection("collection_point")
    item_collection = db.get_collection("item") # <--- NOVO
    print("✅ Conexão com MongoDB estabelecida!")
except Exception as e:
    print(f"❌ Erro ao conectar ao MongoDB: {e}")

# --- 2. Views Comuns ---

def home(request):
    return render(request, 'home.html')

def pontos_coleta(request):
    # Renderiza a página do mapa (A lógica de carregamento do mapa está no front-end)
    return render(request, 'pontos_coleta.html')

# --- 3. Views de Cliente (User) ---

def register_user(request):
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            cpf = request.POST.get('cpf')
            phone = request.POST.get('phone')
            email = request.POST.get('email')
            zip_code = request.POST.get('zip_code')
            password_raw = request.POST.get('password')

            # Validação: Senha deve ser numérica (seguindo o protótipo original)
            try:
                password = int(password_raw)
            except ValueError:
                messages.error(request, "A senha deve conter apenas números.")
                return render(request, 'register.html')

            # Validação: Checar se o email já existe
            if user_collection.find_one({"email": email}):
                messages.warning(request, "Este e-mail já está cadastrado.")
                return render(request, 'register.html')

            user_data = {
                "name": name,
                "profile_picture": "",
                "email": email,
                "password": password,
                "phone": phone,
                "zip_code": zip_code,
                "cpf": cpf,
                "points": 0,
                "discarded_items": 0
            }

            user_collection.insert_one(user_data)
            
            messages.success(request, f"Bem-vindo(a), {name}! Cadastro realizado com sucesso.")
            return redirect('login_user')

        except Exception as e:
            messages.error(request, f"Ocorreu um erro no sistema: {e}")
            return render(request, 'register.html')

    return render(request, 'register.html')

def partner_area(request):
    if 'partner_id' not in request.session:
        messages.warning(request, "Acesso negado. Faça login como Parceiro.")
        return redirect('login_partner')
    
    partner_id = request.session['partner_id']
    
    try:
        # Busca dados atualizados no Mongo
        partner = partner_collection.find_one({"_id": ObjectId(partner_id)})
        
        if not partner:
            request.session.flush()
            messages.error(request, "Sessão inválida. Parceiro não encontrado.")
            return redirect('home')

        return render(request, 'partner_area.html', {'partner': partner})
    except Exception as e:
        messages.error(request, f"Erro ao carregar perfil do parceiro: {e}")
        return redirect('home')

def update_partner(request):
    if request.method == 'POST' and 'partner_id' in request.session:
        partner_id = request.session['partner_id']
        
        try:
            # Captura dados (Conforme o form do partner_area.html)
            updated_data = {
                "NomeParceiro": request.POST.get('NomeParceiro'),
                "EmailParceiro": request.POST.get('EmailParceiro'),
                # Incluir todos os outros campos editáveis aqui...
            }
            
            # Atualiza no Mongo
            partner_collection.update_one(
                {"_id": ObjectId(partner_id)},
                {"$set": updated_data}
            )
            
            request.session['partner_name'] = updated_data['NomeParceiro']
            
            messages.success(request, "Dados do Parceiro atualizados com sucesso!")
        except Exception as e:
            messages.error(request, f"Erro ao atualizar dados do Parceiro: {e}")
            
    return redirect('partner_area')

def login_user(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password_input = request.POST.get('password')

        try:
            password = int(password_input)
        except ValueError:
            messages.error(request, "Senha inválida (deve ser numérica).")
            return render(request, 'login.html')

        user = user_collection.find_one({"email": email, "password": password})

        if user:
            # Salva ID e Nome na sessão para manter o login
            request.session['user_id'] = str(user['_id'])
            request.session['user_name'] = user['name']
            
            messages.success(request, f"Bem-vindo de volta, {user['name']}!")
            return redirect('home')
        else:
            messages.error(request, "E-mail ou senha incorretos.")

    return render(request, 'login.html')

def login_partner(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password_input = request.POST.get('password')

        try:
            password = int(password_input)
        except ValueError:
            messages.error(request, "Senha inválida (deve ser numérica).")
            return render(request, 'partner_login.html')

        # Busca na coleção de parceiros
        partner = partner_collection.find_one({"EmailParceiro": email, "SenhaParceiro": password})

        if partner:
            # Salva o tipo de usuário e o nome na sessão
            request.session['partner_id'] = str(partner['_id'])
            request.session['partner_name'] = partner['NomeParceiro']
            
            messages.success(request, f"Bem-vindo(a) Parceiro, {partner['NomeParceiro']}!")
            return redirect('partner_area') # Redireciona para a nova área de parceiro
        else:
            messages.error(request, "E-mail ou senha incorretos para Parceiro.")

    return render(request, 'partner_login.html')

def logout_user(request):
    request.session.flush()
    messages.info(request, "Você saiu da sua conta.")
    return redirect('home')

def user_area(request):
    if 'user_id' not in request.session:
        messages.warning(request, "Acesso negado. Faça login para ver seu perfil.")
        return redirect('login_user')
    
    user_id = request.session['user_id']
    
    try:
        user = user_collection.find_one({"_id": ObjectId(user_id)})
        
        if not user:
            request.session.flush()
            messages.error(request, "Sessão inválida. Usuário não encontrado.")
            return redirect('home')

        return render(request, 'user_area.html', {'user': user})
    except Exception as e:
        messages.error(request, f"Erro ao carregar perfil: {e}")
        return redirect('home')

def update_user(request):
    if request.method == 'POST' and 'user_id' in request.session:
        user_id = request.session['user_id']
        
        try:
            updated_data = {
                "name": request.POST.get('name'),
                "email": request.POST.get('email'),
                "cpf": request.POST.get('cpf'),
                "phone": request.POST.get('phone'),
                "zip_code": request.POST.get('zip_code'),
                "password": int(request.POST.get('password'))
            }
            
            user_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": updated_data}
            )
            
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
            user_collection.delete_one({"_id": ObjectId(user_id)})
            
            request.session.flush()
            messages.success(request, "Sua conta foi excluída com sucesso.")
        except Exception as e:
            messages.error(request, f"Erro ao excluir conta: {e}")
            return redirect('user_area')
            
    return redirect('home')


# --- 4. Views de Parceiro (Partner) ---

def partner_register(request):
    if request.method == 'POST':
        try:
            # 1. Capturar dados (Conforme Parceiro.cs)
            data = {
                "NomeParceiro": request.POST.get('NomeParceiro'),
                "CpfParceiro": request.POST.get('CpfParceiro'),
                "EmailParceiro": request.POST.get('EmailParceiro'),
                "CepParceiro": request.POST.get('CepParceiro'),
                "LogradouroParceiro": request.POST.get('LogradouroParceiro'),
                "ComplementoParceiro": request.POST.get('ComplementoParceiro'),
                "SenhaParceiro": int(request.POST.get('SenhaParceiro')),
                "PontosParceiro": 0,
                "FotoPerfilParceiro": ""
            }
            
            # 2. Inserção no Mongo (coleção 'partner')
            partner_collection.insert_one(data)
            
            messages.success(request, f"Parceiro {data['NomeParceiro']} registado com sucesso! Faça login para começar.")
            return redirect('home')

        except ValueError:
            messages.error(request, "A senha deve conter apenas números.")
        except Exception as e:
            messages.error(request, f"Ocorreu um erro: {e}")
            
    return render(request, 'partner_register.html')

# ... (após todas as views existentes, como update_partner)

# --- 5. Views de Ponto de Coleta (PontoColeta) ---

def manage_collection_points(request):
    if 'partner_id' not in request.session:
        messages.warning(request, "Acesso negado. Faça login como Parceiro.")
        return redirect('login_partner')

    partner_id = request.session['partner_id']
    
    try:
        # Busca todos os pontos de coleta que pertencem a este Parceiro.
        # No seu modelo PontoColeta.cs, a chave para o Parceiro é CpfParceiro.
        # Precisamos encontrar o CPF do parceiro logado primeiro para filtrar.
        
        partner_obj = partner_collection.find_one({"_id": ObjectId(partner_id)})
        
        if not partner_obj or 'CpfParceiro' not in partner_obj:
            messages.error(request, "Dados do Parceiro incompletos.")
            return redirect('partner_area')
            
        partner_cpf = partner_obj['CpfParceiro']

        points_list = list(collection_point_collection.find({"CpfParceiro": partner_cpf}))

        context = {
            'points': points_list,
            'partner_cpf': partner_cpf # Passamos para o template de criação
        }
        return render(request, 'partner_collection_points.html', context)
    
    except Exception as e:
        messages.error(request, f"Erro ao carregar gestão de pontos: {e}")
        return redirect('partner_area')


def create_collection_point(request):
    if 'partner_id' not in request.session:
        messages.warning(request, "Acesso negado.")
        return redirect('login_partner')

    if request.method == 'POST':
        try:
            # 1. Obter CPF do Parceiro (chave estrangeira)
            partner_obj = partner_collection.find_one({"_id": ObjectId(request.session['partner_id'])})
            partner_cpf = partner_obj.get('CpfParceiro')

            # 2. Capturar dados do formulário (Baseado no PontoColeta.cs)
            data = {
                "CnpjParceiro": request.POST.get('CnpjParceiro'),
                "ItensColetados": 0, # Inicia com 0
                "Pontuacao": 0,      # Inicia com 0
                "CpfParceiro": partner_cpf, # Chave Estrangeira
                
                # Campos extras necessários (como endereço, que devem vir do form)
                "EnderecoPonto": request.POST.get('EnderecoPonto'),
                "HorarioAbertura": request.POST.get('HorarioAbertura'),
                "CapacidadeKg": int(request.POST.get('CapacidadeKg')) # Assumindo campo numérico
            }

            # 3. Inserir no Mongo (coleção 'collection_point')
            collection_point_collection.insert_one(data)
            
            messages.success(request, "Ponto de Coleta criado com sucesso!")
            return redirect('manage_collection_points')

        except ValueError:
            messages.error(request, "O campo de Capacidade deve ser um número inteiro.")
        except Exception as e:
            messages.error(request, f"Erro ao criar ponto de coleta: {e}")

    # Retorna para a página de gestão se o POST falhar
    return redirect('manage_collection_points')

def update_collection_point(request, point_id):
    if request.method == 'POST' and 'partner_id' in request.session:
        try:
            # 1. Fetch data
            updated_data = {
                "CnpjParceiro": request.POST.get('CnpjParceiro'),
                "EnderecoPonto": request.POST.get('EnderecoPonto'),
                "HorarioAbertura": request.POST.get('HorarioAbertura'),
                # Garantindo que campos numéricos sejam tratados como int
                "CapacidadeKg": int(request.POST.get('CapacidadeKg')),
                "Pontuacao": int(request.POST.get('Pontuacao', 0)), 
                "ItensColetados": int(request.POST.get('ItensColetados', 0)),
            }
            
            # 2. Update in Mongo
            collection_point_collection.update_one(
                {"_id": ObjectId(point_id)},
                {"$set": updated_data}
            )
            
            messages.success(request, "Ponto de Coleta atualizado com sucesso!")

        except ValueError:
            messages.error(request, "Capacidade, Pontuação e Itens Coletados devem ser números inteiros.")
        except Exception as e:
            messages.error(request, f"Erro ao atualizar ponto de coleta: {e}")
            
    return redirect('manage_collection_points')


def delete_collection_point(request, point_id):
    if request.method == 'POST' and 'partner_id' in request.session:
        try:
            # 1. Delete from Mongo
            result = collection_point_collection.delete_one({"_id": ObjectId(point_id)})
            
            if result.deleted_count == 1:
                messages.success(request, "Ponto de Coleta excluído com sucesso.")
            else:
                messages.warning(request, "Ponto de Coleta não encontrado.")
                
        except Exception as e:
            messages.error(request, f"Erro ao excluir ponto de coleta: {e}")
            
    return redirect('manage_collection_points')

# --- 6. Views de Item (Inventário) ---

def register_item(request):
    if 'partner_id' not in request.session:
        messages.warning(request, "Acesso negado.")
        return redirect('login_partner')

    # A página pode ser acessada via GET (para mostrar o formulário)
    # ou via POST (para salvar o item)

    # 1. Buscar Pontos de Coleta do Parceiro para usar no formulário
    partner_obj = partner_collection.find_one({"_id": ObjectId(request.session['partner_id'])})
    partner_cpf = partner_obj.get('CpfParceiro')
    
    # Lista de Pontos de Coleta do Parceiro
    available_points = list(collection_point_collection.find({"CpfParceiro": partner_cpf}))

    if request.method == 'POST':
        try:
            # Capturar ID do Ponto de Coleta
            id_ponto_coleta = request.POST.get('IdPontoColeta')
            
            # Validação básica
            if not id_ponto_coleta:
                messages.error(request, "Selecione um Ponto de Coleta válido.")
                return redirect('register_item')

            # 2. Capturar dados do Item (Baseado no Item.cs)
            data_item = {
                "Valor": float(request.POST.get('Valor')), # Valor monetário
                "ModeloItem": request.POST.get('ModeloItem'),
                "Tipo": request.POST.get('Tipo'),
                "IdPontoColeta": ObjectId(id_ponto_coleta), # Referência ao Ponto de Coleta
                "IdEstoque": None, # Fica nulo até ser vendido/movimentado
                "DataRegistro": datetime.now() # Adicionando data para controle
            }
            
            # 3. Inserir Item no Mongo
            item_collection.insert_one(data_item)
            
            # 4. (OPCIONAL) Atualizar contador de itens no Ponto de Coleta
            collection_point_collection.update_one(
                 {"_id": ObjectId(id_ponto_coleta)},
                 {"$inc": {"ItensColetados": 1}} # Incrementa o contador em 1
            )
            
            messages.success(request, f"Item '{data_item['ModeloItem']}' registado com sucesso no Ponto de Coleta.")
            return redirect('register_item')

        except ValueError:
            messages.error(request, "O Valor deve ser um número válido.")
        except Exception as e:
            messages.error(request, f"Erro ao registar item: {e}")
            
    context = {
        'points': available_points
    }
    return render(request, 'item_register.html', context)
