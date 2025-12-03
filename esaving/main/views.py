from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CadastroPontoColetaForm, LoginForm, ConfiguracoesForm
from .mongo_db import MongoDBManager
import json
from datetime import datetime

def index(request):
    """Página inicial com mapa"""
    pontos = MongoDBManager.listar_pontos_coleta()
    
    context = {
        'pontos': pontos,
        'pontos_json': json.dumps(pontos, default=str, ensure_ascii=False)
    }
    return render(request, 'main/index.html', context)

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
                # Configurar sessão
                request.session['user'] = user
                messages.success(request, f'Bem-vindo, {user["username"]}!')
                return redirect('area_parceiro')
            else:
                messages.error(request, 'Usuário ou senha inválidos.')
        else:
            messages.error(request, 'Por favor, corrija os erros no formulário.')
    else:
        form = LoginForm()
    
    return render(request, 'main/login.html', {'form': form})

def logout_view(request):
    """Logout"""
    if 'user' in request.session:
        del request.session['user']
    messages.success(request, 'Logout realizado com sucesso.')
    return redirect('index')

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

def configuracoes(request):
    """Configurações do ponto"""
    if 'user' not in request.session:
        return redirect('login')
    
    user = request.session['user']
    
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
                # Atualizar sessão
                user.update(dados_atualizacao)
                request.session['user'] = user
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