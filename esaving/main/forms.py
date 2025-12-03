from django import forms
from django.core.validators import RegexValidator

class CadastroPontoColetaForm(forms.Form):
    """Formulário para cadastro de ponto de coleta"""
    username = forms.CharField(
        max_length=150,
        label="Nome de usuário",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label="E-mail",
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    telefone = forms.CharField(
        max_length=15,
        label="Telefone",
        validators=[RegexValidator(r'^\(\d{2}\) \d{5}-\d{4}$', 'Formato: (XX) XXXXX-XXXX')],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(11) 99999-9999'})
    )
    cep = forms.CharField(
        max_length=9,
        label="CEP",
        validators=[RegexValidator(r'^\d{5}-\d{3}$', 'Formato: XXXXX-XXX')],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '01234-567'})
    )
    cpf_cnpj = forms.CharField(
        max_length=18,
        label="CPF ou CNPJ",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    endereco = forms.CharField(
        label="Endereço completo",
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
    password = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password_confirm = forms.CharField(
        label="Confirmar senha",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    
    def clean_cpf_cnpj(self):
        cpf_cnpj = self.cleaned_data.get('cpf_cnpj')
        # Remover caracteres não numéricos
        cpf_cnpj_clean = ''.join(filter(str.isdigit, cpf_cnpj))
        
        if len(cpf_cnpj_clean) == 11:  # CPF
            if not self.validar_cpf(cpf_cnpj_clean):
                raise forms.ValidationError("CPF inválido")
        elif len(cpf_cnpj_clean) == 14:  # CNPJ
            if not self.validar_cnpj(cpf_cnpj_clean):
                raise forms.ValidationError("CNPJ inválido")
        else:
            raise forms.ValidationError("CPF deve ter 11 dígitos ou CNPJ 14 dígitos")
        
        return cpf_cnpj_clean
    
    def validar_cpf(self, cpf):
        # Implementação básica de validação de CPF
        if len(cpf) != 11:
            return False
        # Algoritmo de validação simplificado
        return True
    
    def validar_cnpj(self, cnpj):
        # Implementação básica de validação de CNPJ
        if len(cnpj) != 14:
            return False
        # Algoritmo de validação simplificado
        return True
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")
        
        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "As senhas não coincidem")
        
        return cleaned_data

class LoginForm(forms.Form):
    """Formulário para login"""
    username = forms.CharField(
        label="Nome de usuário ou E-mail",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    remember_me = forms.BooleanField(
        required=False,
        label="Manter-me conectado",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

class ConfiguracoesForm(forms.Form):
    """Formulário para configurações"""
    telefone = forms.CharField(
        max_length=15,
        label="Telefone",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    cep = forms.CharField(
        max_length=9,
        label="CEP",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    endereco = forms.CharField(
        label="Endereço",
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
    horario_funcionamento = forms.CharField(
        label="Horário de funcionamento",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    tipos_residuos = forms.MultipleChoiceField(
        label="Tipos de resíduos aceitos",
        choices=[
            ('computadores', 'Computadores'),
            ('celulares', 'Celulares'),
            ('baterias', 'Baterias'),
            ('eletrodomésticos', 'Eletrodomésticos'),
            ('fios', 'Fios e Cabos'),
            ('outros', 'Outros'),
        ],
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False
    )