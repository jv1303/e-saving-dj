from django.contrib import admin
from .models import Cliente, Parceiro, PontoColeta, Item

# Registrando os modelos para aparecerem no painel admin
admin.site.register(Cliente)
admin.site.register(Parceiro)
admin.site.register(PontoColeta)
admin.site.register(Item)
