from django.contrib import admin

# Como estamos usando MongoDB, não usaremos o admin padrão do Django
# para os modelos MongoDB. Vamos apenas configurar o admin site.

admin.site.site_header = 'E-Saving - Administração'
admin.site.site_title = 'E-Saving Admin'
admin.site.index_title = 'Dashboard'