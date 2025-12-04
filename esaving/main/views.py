from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CadastroPontoColetaForm, LoginForm, ConfiguracoesForm
from .mongo_db import MongoDBManager
from datetime import datetime
from functools import wraps
import json


def index(request):
    """Página inicial com mapa"""
    pontos = MongoDBManager.listar_pontos_coleta()
    
    context = {
        'pontos': pontos,
        'pontos_json': json.dumps(pontos, default=str, ensure_ascii=False)
    }
    return render(request, 'main/index.html', context)

def login_required_custom(view_func):
    """Decorator personalizado para verificar se o usuário está na sessão"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if 'user' not in request.session or not request.session['user']:
            messages.error(request, 'Faça login para acessar esta área.')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def cadastro(request):
    """Cadastro de ponto de coleta"""
    if request.method == 'POST':
        form = CadastroPontoColetaForm(request.POST)
        if form.is_valid():
            user_data = {
                'username': form.cleaned_data['username'],
                'email': form.cleaned_data['email'],
                'telefone': form.cleaned_data['telefone'],
                'cep': form.cleaned_data['cep'],
                'cpf_cnpj': form.cleaned_data['cpf_cnpj'],
                'endereco': form.cleaned_data['endereco'],
                'password': form.cleaned_data['password'],
                'tipos_residuos': [],
                'horario_funcionamento': 'Segunda a Sexta, 8h às 18h',
                'is_active': True
            }
            
            try:
                user_id = MongoDBManager.criar_usuario(user_data)
                if user_id:
                    messages.success(request, 'Cadastro realizado com sucesso! Faça login para acessar sua área.')
                    return redirect('login')
            except ValueError as e:
                messages.error(request, str(e))
    else:
        form = CadastroPontoColetaForm()
    
    return render(request, 'main/cadastro.html', {'form': form})

def login_view(request):
    """Página de login"""
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            user = MongoDBManager.autenticar_usuario(username, password)
            if user:
                # Converter objetos datetime para string ISO
                user_serializable = converter_datetime_para_string(user)
                
                # Configurar sessão
                request.session['user'] = user_serializable
                messages.success(request, f'Bem-vindo, {username}!')
                return redirect('area_parceiro')
            else:
                messages.error(request, 'Usuário ou senha inválidos.')
        else:
            messages.error(request, 'Por favor, corrija os erros no formulário.')
    else:
        form = LoginForm()
    
    return render(request, 'main/login.html', {'form': form})

def converter_datetime_para_string(obj):
    """Converte objetos datetime em um dicionário para strings ISO"""
    if isinstance(obj, dict):
        result = {}
        for key, value in obj.items():
            if isinstance(value, datetime):
                result[key] = value.isoformat()
            elif isinstance(value, dict):
                result[key] = converter_datetime_para_string(value)
            elif isinstance(value, list):
                result[key] = [converter_datetime_para_string(item) if isinstance(item, dict) else 
                              (item.isoformat() if isinstance(item, datetime) else item) 
                              for item in value]
            else:
                result[key] = value
        return result
    return obj

def logout_view(request):
    """Logout"""
    if 'user' in request.session:
        del request.session['user']
    messages.success(request, 'Logout realizado com sucesso.')
    return redirect('index')

@login_required_custom
def area_parceiro(request):
    """Área do parceiro (requer login)"""
    if 'user' not in request.session:
        messages.error(request, 'Faça login para acessar esta área.')
        return redirect('login')
    
    user = request.session['user']
    coletas = MongoDBManager.buscar_coletas_por_ponto(user['username'])
    
    # Calcular estatísticas básicas
    total_coletado = sum(float(coleta.get('quantidade', 0)) for coleta in coletas)
    
    context = {
        'user': user,
        'coletas': coletas[:5],  # Últimas 5 coletas
        'total_coletado': total_coletado,
        'total_coletas': len(coletas)
    }
    
    return render(request, 'main/area_parceiro.html', context)

def quem_somos(request):
    """Página institucional"""
    return render(request, 'main/quem_somos.html')

@login_required_custom
def estatisticas(request):
    """Estatísticas detalhadas"""
    if 'user' not in request.session:
        return redirect('login')
    
    user = request.session['user']
    coletas = MongoDBManager.buscar_coletas_por_ponto(user['username'])
    
    # Agrupar por tipo
    por_tipo = {}
    for coleta in coletas:
        tipo = coleta.get('tipo_residuo', 'Outros')
        quantidade = float(coleta.get('quantidade', 0))
        if tipo in por_tipo:
            por_tipo[tipo] += quantidade
        else:
            por_tipo[tipo] = quantidade
    
    context = {
        'user': user,
        'coletas': coletas,
        'por_tipo': por_tipo,
        'total_coletado': sum(float(c.get('quantidade', 0)) for c in coletas),
        'total_registros': len(coletas)
    }
    
    return render(request, 'main/estatisticas.html', context)

@login_required_custom
def area_parceiro(request):
    """Área do parceiro (requer login)"""
    user = request.session.get('user')
    if not user:
        messages.error(request, 'Faça login para acessar esta área.')
        return redirect('login')
    
    coletas = MongoDBManager.buscar_coletas_por_ponto(user['username'])
    
    # Calcular estatísticas básicas
    total_coletado = sum(float(coleta.get('quantidade', 0)) for coleta in coletas)
    
    # Converter datetime nas coletas para string
    coletas_serializaveis = []
    for coleta in coletas:
        coleta_serializavel = converter_datetime_para_string(coleta)
        coletas_serializaveis.append(coleta_serializavel)
    
    context = {
        'user': user,
        'coletas': coletas_serializaveis[:5],  # Últimas 5 coletas
        'total_coletado': total_coletado,
        'total_coletas': len(coletas)
    }
    
    return render(request, 'main/area_parceiro.html', context)

@login_required_custom
def configuracoes(request):
    """Configurações do ponto"""
    user = request.session.get('user')
    if not user:
        return redirect('login')
    
    if request.method == 'POST':
        form = ConfiguracoesForm(request.POST)
        if form.is_valid():
            dados_atualizacao = {
                'telefone': form.cleaned_data['telefone'],
                'cep': form.cleaned_data['cep'],
                'endereco': form.cleaned_data['endereco'],
                'horario_funcionamento': form.cleaned_data['horario_funcionamento'],
                'tipos_residuos': form.cleaned_data['tipos_residuos']
            }
            
            if MongoDBManager.atualizar_usuario(user['username'], dados_atualizacao):
                messages.success(request, 'Configurações atualizadas com sucesso!')
                # Atualizar sessão - mesclar dados
                user.update(dados_atualizacao)
                # Garantir que não há objetos datetime
                user_serializable = converter_datetime_para_string(user)
                request.session['user'] = user_serializable
                return redirect('configuracoes')
    else:
        # Carregar dados atuais
        initial_data = {
            'telefone': user.get('telefone', ''),
            'cep': user.get('cep', ''),
            'endereco': user.get('endereco', ''),
            'horario_funcionamento': user.get('horario_funcionamento', ''),
            'tipos_residuos': user.get('tipos_residuos', [])
        }
        form = ConfiguracoesForm(initial=initial_data)
    
    return render(request, 'main/configuracoes.html', {'form': form, 'user': user})
