from django.db import models
from django.contrib.auth.models import User

# --- Cliente (Cidadão/Comprador) ---
# Estende o usuário padrão do Django para adicionar CPF e endereço
class Cliente(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil_cliente')
    cpf = models.CharField(max_length=14, unique=True, verbose_name="CPF")
    cep = models.CharField(max_length=9, verbose_name="CEP")
    logradouro = models.CharField(max_length=255, verbose_name="Endereço", blank=True)
    complemento = models.CharField(max_length=255, blank=True, null=True)
    
    # Gamificação
    pontos = models.IntegerField(default=0)
    itens_descartados = models.IntegerField(default=0)
    
    foto_perfil = models.ImageField(upload_to='clientes/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.first_name} ({self.cpf})"

# --- Parceiro (Empresas/Cooperativas) ---
class Parceiro(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil_parceiro')
    cnpj_cpf = models.CharField(max_length=18, unique=True, verbose_name="CNPJ ou CPF")
    nome_fantasia = models.CharField(max_length=255, verbose_name="Nome da Empresa")
    
    cep = models.CharField(max_length=9)
    logradouro = models.CharField(max_length=255)
    complemento = models.CharField(max_length=255, blank=True, null=True)
    
    pontos_acumulados = models.IntegerField(default=0)
    foto_perfil = models.ImageField(upload_to='parceiros/', blank=True, null=True)

    def __str__(self):
        return self.nome_fantasia

# --- Ponto de Coleta (Mapa) ---
class PontoColeta(models.Model):
    parceiro = models.ForeignKey(Parceiro, on_delete=models.CASCADE, related_name='pontos_coleta')
    nome_local = models.CharField(max_length=100, help_text="Ex: Ecoponto Central")
    
    # Latitude e Longitude para o mapa (Leaflet)
    latitude = models.FloatField()
    longitude = models.FloatField()
    
    endereco_completo = models.CharField(max_length=255)
    itens_coletados_total = models.IntegerField(default=0)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nome_local} - {self.parceiro.nome_fantasia}"

# --- Item (Estoque/Descarte) ---
class Item(models.Model):
    TIPOS = (
        ('Metal', 'Metal'),
        ('Plastico', 'Plástico'),
        ('Vidro', 'Vidro'),
        ('Eletronico', 'Eletrônico'),
        ('Papel', 'Papel'),
    )
    
    modelo = models.CharField(max_length=50)
    tipo = models.CharField(max_length=50, choices=TIPOS)
    valor = models.FloatField(default=0.0)
    
    # O item pertence a um ponto de coleta específico
    ponto_coleta = models.ForeignKey(PontoColeta, on_delete=models.SET_NULL, null=True, blank=True)
    
    data_entrada = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.modelo} ({self.tipo})"
    