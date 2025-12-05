from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from .models import PontoColeta
import json

# Importamos nossos Forms e Models
from .forms import UserRegisterForm, ClienteProfileForm, ParceiroProfileForm, PontoColetaForm, ItemForm
from .models import PontoColeta, Item

# --- Páginas Públicas ---

def home(request):
    return render(request, 'home.html')

def quem_somos(request):
    return render(request, 'quem_somos.html')

def mapa_pontos(request):
    query = request.GET.get('q', '').lower()
    
    # Busca todos os pontos
    todos_pontos = PontoColeta.objects.all()
    pontos_list = []
    
    print(f"--- DEBUG: Total de pontos no banco: {todos_pontos.count()} ---") # Debug no terminal

    for p in todos_pontos:
        if not p.ativo:
            continue
            
        # Tratamento de erro seguro para o Parceiro (caso o ID não exista ou seja nulo)
        nome_parceiro = "Parceiro Desconhecido"
        try:
            if p.parceiro:
                nome_parceiro = p.parceiro.nome_fantasia
        except Exception as e:
            print(f"Erro ao buscar parceiro do ponto {p.nome_local}: {e}")

        # Filtros de busca
        adicionar = True
        if query:
            nome = str(p.nome_local).lower()
            end = str(p.endereco_completo).lower()
            parc = str(nome_parceiro).lower()
            
            if (query not in nome) and (query not in end) and (query not in parc):
                adicionar = False
        
        if adicionar:
            pontos_list.append({
                'name': p.nome_local,
                'lat': p.latitude,
                'lon': p.longitude,
                'desc': p.endereco_completo,
                'parceiro': nome_parceiro
            })
    
    # Serializa para JSON
    pontos_json = json.dumps(pontos_list)
    print(f"--- DEBUG: JSON enviado para o template: {pontos_json} ---") # Debug no terminal
    
    return render(request, 'pontos_coleta.html', {
        'pontos_json': pontos_json,
        'query': query
    })

# --- Lógica de Cadastro de Usuários ---

def register_cliente(request):
    if request.method == 'POST':
        user_form = UserRegisterForm(request.POST)
        # request.FILES é obrigatório para receber a foto!
        profile_form = ClienteProfileForm(request.POST, request.FILES)
        
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.save()
            
            cliente = profile_form.save(commit=False)
            cliente.user = user
            cliente.save()
            
            messages.success(request, 'Conta de Cliente criada! Faça login.')
            return redirect('login')
    else:
        user_form = UserRegisterForm()
        profile_form = ClienteProfileForm()
        
    return render(request, 'register_cliente.html', {
        'user_form': user_form, 
        'profile_form': profile_form
    })

def register_parceiro(request):
    if request.method == 'POST':
        user_form = UserRegisterForm(request.POST)
        profile_form = ParceiroProfileForm(request.POST, request.FILES)
        
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.save()
            
            parceiro = profile_form.save(commit=False)
            parceiro.user = user
            parceiro.save()
            
            messages.success(request, 'Conta de Parceiro criada! Faça login.')
            return redirect('login')
    else:
        user_form = UserRegisterForm()
        profile_form = ParceiroProfileForm()
        
    return render(request, 'register_parceiro.html', {
        'user_form': user_form, 
        'profile_form': profile_form
    })

# --- Área Logada e Gestão ---

@login_required
def dashboard(request):
    if hasattr(request.user, 'perfil_parceiro'):
        parceiro = request.user.perfil_parceiro
        # Traz todos os pontos desse parceiro
        meus_pontos = parceiro.pontos_coleta.all()
        return render(request, 'area_parceiro.html', {
            'parceiro': parceiro, 
            'pontos': meus_pontos
        })
    
    elif hasattr(request.user, 'perfil_cliente'):
        return render(request, 'area_usuario.html', {
            'cliente': request.user.perfil_cliente
        })
    
    return redirect('home')

@login_required
def cadastrar_ponto(request):
    # Verifica se é parceiro
    if not hasattr(request.user, 'perfil_parceiro'):
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = PontoColetaForm(request.POST)
        
        # --- AQUI ESTÁ A MUDANÇA PARA DEBUG ---
        if form.is_valid():
            try:
                ponto = form.save(commit=False)
                ponto.parceiro = request.user.perfil_parceiro
                ponto.save()
                messages.success(request, 'Ponto de coleta salvo com sucesso!')
                return redirect('dashboard')
            except Exception as e:
                # Se der erro no banco (Djongo), mostra aqui
                print(f"ERRO AO SALVAR NO BANCO: {e}")
                messages.error(request, f"Erro de Banco de Dados: {e}")
        else:
            # Se o formulário for inválido (ex: vírgula em vez de ponto), mostra aqui
            print("ERRO DE VALIDAÇÃO:", form.errors)
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Erro no campo '{field}': {error}")
        # --------------------------------------
            
    else:
        form = PontoColetaForm()
        
    return render(request, 'cadastrar_ponto.html', {'form': form})


@login_required
def adicionar_item(request):
    if not hasattr(request.user, 'perfil_parceiro'):
        return redirect('dashboard')
    
    parceiro = request.user.perfil_parceiro
    
    # Validação inicial usando .first() (seguro para Djongo)
    if not parceiro.pontos_coleta.first():
        messages.warning(request, "Você precisa criar um Ponto de Coleta antes de registrar itens!")
        return redirect('cadastrar_ponto')

    if request.method == 'POST':
        form = ItemForm(request.user, request.POST)
        
        if form.is_valid():
            try:
                # 1. Recupera o ID do ponto selecionado no formulário
                ponto_selecionado_id = form.cleaned_data['ponto_id']
                
                # 2. Busca o objeto PontoColeta manualmente
                # Usamos .filter().first() que o Djongo entende bem
                ponto = PontoColeta.objects.filter(id=ponto_selecionado_id, parceiro=parceiro).first()
                
                if not ponto:
                    raise Exception("Ponto de coleta não encontrado.")

                # 3. Prepara o item mas NÃO salva ainda (commit=False)
                item = form.save(commit=False)
                item.ponto_coleta = ponto  # Vincula o ponto manualmente
                item.save()                # Agora salva no banco
                
                print(f"--- DEBUG: Item '{item.modelo}' salvo no ponto '{ponto.nome_local}' ---")
                
                # 4. Atualiza contadores
                ponto.itens_coletados_total += 1
                ponto.save()
                
                parceiro.pontos_acumulados += 10 
                parceiro.save()
                    
                messages.success(request, f'Item "{item.modelo}" registrado com sucesso!')
                return redirect('dashboard')
                
            except Exception as e:
                print(f"❌ ERRO CRÍTICO: {e}")
                messages.error(request, f"Erro ao processar: {e}")
        else:
            print("❌ ERRO DE VALIDAÇÃO:", form.errors)
    else:
        form = ItemForm(request.user)
    
    return render(request, 'adicionar_item.html', {'form': form})

@login_required
def remover_item(request, item_id):
    try:
        item = Item.objects.get(pk=item_id)
        if item.ponto_coleta.parceiro.user == request.user:
            ponto = item.ponto_coleta
            item.delete()
            if ponto.itens_coletados_total > 0:
                ponto.itens_coletados_total -= 1
                ponto.save()
            messages.success(request, 'Item removido.')
        else:
            messages.error(request, 'Sem permissão.')
    except Item.DoesNotExist:
        messages.error(request, 'Item não encontrado.')
    
    return redirect('dashboard')
