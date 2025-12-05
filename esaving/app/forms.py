from django import forms
from django.contrib.auth.models import User
from .models import Cliente, Parceiro, PontoColeta, Item

# --- Formulário Base de Registro (Login/Senha) ---
class UserRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Senha")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirmar Senha")
    email = forms.EmailField(required=True, label="E-mail")
    first_name = forms.CharField(required=True, label="Nome Completo")

    class Meta:
        model = User
        fields = ['username', 'first_name', 'email', 'password']
        help_texts = {
            'username': 'Usuário para login (sem espaços).',
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("As senhas não coincidem.")
        return cleaned_data

# --- Perfil do Cliente (CPF, Endereço) ---
class ClienteProfileForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['cpf', 'cep', 'logradouro', 'complemento', 'foto_perfil']
        widgets = {
            'foto_perfil': forms.FileInput(),
        }

# --- Perfil do Parceiro (CNPJ, Empresa) ---
class ParceiroProfileForm(forms.ModelForm):
    class Meta:
        model = Parceiro
        fields = ['cnpj_cpf', 'nome_fantasia', 'cep', 'logradouro', 'complemento', 'foto_perfil']
        widgets = {
            'foto_perfil': forms.FileInput(),
        }

# --- Cadastro de Ponto de Coleta ---
class PontoColetaForm(forms.ModelForm):
    class Meta:
        model = PontoColeta
        fields = ['nome_local', 'endereco_completo', 'latitude', 'longitude']
        widgets = {
            'latitude': forms.TextInput(attrs={'placeholder': 'Ex: -23.5505'}),
            'longitude': forms.TextInput(attrs={'placeholder': 'Ex: -46.6333'}),
        }

# --- Cadastro de Item (Novo) ---
class ItemForm(forms.ModelForm):
    # Substituímos o campo automático por um ChoiceField simples
    # Isso evita o erro de validação "SELECT 1" do Djongo
    ponto_id = forms.ChoiceField(label='Local de Recebimento', required=True)

    class Meta:
        model = Item
        # Removemos 'ponto_coleta' daqui para gerenciar manualmente na view
        fields = ['modelo', 'tipo', 'valor'] 
    
    def __init__(self, user, *args, **kwargs):
        super(ItemForm, self).__init__(*args, **kwargs)
        
        # Carrega as opções manualmente para o campo Select
        if hasattr(user, 'perfil_parceiro'):
            pontos = user.perfil_parceiro.pontos_coleta.all()
            # Cria a lista de tuplas (ID, Nome) para o formulário
            opcoes = [(str(p.id), p.nome_local) for p in pontos]
            self.fields['ponto_id'].choices = opcoes
            