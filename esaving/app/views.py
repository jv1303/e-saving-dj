from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.db import models  # <--- ADICIONE ESSA LINHA AQUI
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
    # Pega o termo de busca da URL (ex: /mapa/?q=centro)
    query = request.GET.get('q')
    
    # Começa pegando todos os pontos ativos
    pontos = PontoColeta.objects.all()
    
    # Se tiver busca, filtra por nome do local, endereço ou nome do parceiro
    if query:
        pontos = pontos.filter(
            models.Q(nome_local__icontains=query) | 
            models.Q(endereco_completo__icontains=query) |
            models.Q(parceiro__nome_fantasia__icontains=query)
        )
    
    # Serializa para o Mapa
    pontos_list = []
    for p in pontos:
        pontos_list.append({
            'name': p.nome_local,
            'lat': p.latitude,
            'lon': p.longitude,
            'desc': p.endereco_completo,
            'parceiro': p.parceiro.nome_fantasia
        })
    
    pontos_json = json.dumps(pontos_list)
    
    return render(request, 'pontos_coleta.html', {
        'pontos_json': pontos_json,
        'query': query or '' # Devolve o termo para preencher o input
    })

# --- Lógica de Cadastro ---

def register_cliente(request):
    if request.method == 'POST':
        user_form = UserRegisterForm(request.POST)
        profile_form = ClienteProfileForm(request.POST, request.FILES)
        
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.save()
            
            cliente = profile_form.save(commit=False)
            cliente.user = user
            cliente.save()
            
            messages.success(request, 'Conta de Cliente criada com sucesso! Faça login.')
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

# --- Área Logada (Dashboard) ---

@login_required
def dashboard(request):
    if hasattr(request.user, 'perfil_parceiro'):
        parceiro = request.user.perfil_parceiro
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
    if not hasattr(request.user, 'perfil_parceiro'):
        messages.error(request, "Apenas parceiros podem cadastrar pontos.")
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = PontoColetaForm(request.POST)
        if form.is_valid():
            ponto = form.save(commit=False)
            ponto.parceiro = request.user.perfil_parceiro
            ponto.save()
            messages.success(request, 'Ponto de coleta adicionado!')
            return redirect('dashboard')
    else:
        form = PontoColetaForm()
        
    return render(request, 'cadastrar_ponto.html', {'form': form})

# --- Gestão de Itens (Novo) ---

@login_required
def adicionar_item(request):
    if not hasattr(request.user, 'perfil_parceiro'):
        return redirect('dashboard')

    if request.method == 'POST':
        form = ItemForm(request.user, request.POST)
        if form.is_valid():
            item = form.save()
            
            ponto = item.ponto_coleta
            if ponto:
                ponto.itens_coletados_total += 1
                ponto.save()
                
            messages.success(request, f'Item "{item.modelo}" registrado com sucesso!')
            return redirect('dashboard')
    else:
        form = ItemForm(request.user)
    
    return render(request, 'adicionar_item.html', {'form': form})

@login_required
def remover_item(request, item_id):
    try:
        item = Item.objects.get(pk=item_id)
        # Verifica se o item pertence a este parceiro
        if item.ponto_coleta.parceiro.user == request.user:
            ponto = item.ponto_coleta
            item.delete()
            
            if ponto.itens_coletados_total > 0:
                ponto.itens_coletados_total -= 1
                ponto.save()
                
            messages.success(request, 'Item removido do estoque.')
        else:
            messages.error(request, 'Permissão negada.')
    except Item.DoesNotExist:
        messages.error(request, 'Item não encontrado.')
    
    return redirect('dashboard')
