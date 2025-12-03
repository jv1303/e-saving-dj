from django import forms
from django.core.validators import RegexValidator

class PontoColetaForm(forms.Form):
    """Formulário para pontos de coleta (MongoDB)"""
    username = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    telefone = forms.CharField(
        max_length=15,
        validators=[RegexValidator(r'^\(\d{2}\) \d{5}-\d{4}$', 'Formato: (XX) XXXXX-XXXX')]
    )
    cep = forms.CharField(
        max_length=9,
        validators=[RegexValidator(r'^\d{5}-\d{3}$', 'Formato: XXXXX-XXX')]
    )
    cpf_cnpj = forms.CharField(max_length=18, label="CPF/CNPJ")
    endereco = forms.CharField(max_length=255)
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Confirmar Senha")
    
    def clean_cpf_cnpj(self):
        cpf_cnpj = self.cleaned_data.get('cpf_cnpj')
        cpf_cnpj_clean = ''.join(filter(str.isdigit, cpf_cnpj))
        
        if len(cpf_cnpj_clean) not in [11, 14]:
            raise forms.ValidationError("CPF deve ter 11 dígitos ou CNPJ 14 dígitos")
        return cpf_cnpj_clean
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")
        
        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "As senhas não coincidem")
        return cleaned_data

# Classes para MongoDB
class PontoColeta:
    """Classe que representa um ponto de coleta no MongoDB"""
    
    def __init__(self, username, email, telefone, cep, cpf_cnpj, endereco, password=None):
        self.username = username
        self.email = email
        self.telefone = telefone
        self.cep = cep
        self.cpf_cnpj = cpf_cnpj
        self.endereco = endereco
        self.password = password
        self.tipos_residuos = []
        self.horario_funcionamento = 'Segunda a Sexta, 8h às 18h'
        self.latitude = None
        self.longitude = None
        self.is_active = True
    
    def to_dict(self):
        return {
            'username': self.username,
            'email': self.email,
            'telefone': self.telefone,
            'cep': self.cep,
            'cpf_cnpj': self.cpf_cnpj,
            'endereco': self.endereco,
            'password': self.password,
            'tipos_residuos': self.tipos_residuos,
            'horario_funcionamento': self.horario_funcionamento,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'is_active': self.is_active
        }

class Coleta:
    """Classe que representa uma coleta no MongoDB"""
    
    def __init__(self, ponto_username, data, tipo_residuo, quantidade, unidade='kg'):
        self.ponto_username = ponto_username
        self.data = data
        self.tipo_residuo = tipo_residuo
        self.quantidade = quantidade
        self.unidade = unidade
    
    def to_dict(self):
        return {
            'ponto_username': self.ponto_username,
            'data': self.data,
            'tipo_residuo': self.tipo_residuo,
            'quantidade': self.quantidade,
            'unidade': self.unidade
        }