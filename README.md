# E-Saving - Plataforma de Gestão de Resíduos Eletrônicos

Este projeto é uma aplicação **Full Stack Django** desenvolvida com foco em sustentabilidade e economia circular.

O **E-Saving** conecta cidadãos conscientes a empresas de reciclagem (Parceiros), facilitando o descarte correto de lixo eletrônico, gerenciamento de pontos de coleta e gamificação do processo de reciclagem.

---

## ♻️ Contexto e Arquitetura

Diferente de sistemas tradicionais baseados em bancos relacionais, este projeto utiliza uma abordagem moderna com **NoSQL (MongoDB)** integrado ao ORM do Django, permitindo flexibilidade no armazenamento de dados de coleta.

**Nesta versão, entregamos:**

1.  **Sistema Híbrido (MVT):** Utilização do padrão Model-View-Template do Django para renderização dinâmica.
2.  **Geolocalização:** Integração com **Leaflet.js** e OpenStreetMap para visualização de pontos de coleta.
3.  **Gamificação:** Sistema de pontuação para cidadãos baseado no volume e tipo de itens descartados.
4.  **Gestão de Inventário:** Dashboard para parceiros gerenciarem o fluxo de entrada de materiais (Metais, Plásticos, Eletrônicos).

---

## 🚀 Principais Funcionalidades

* **Mapa Interativo de Coleta**: Visualização de pinos no mapa baseada em latitude/longitude, com filtragem por bairro ou local.
* **Perfis Distintos**:
    * **Cidadão:** Acesso a histórico de descartes e saldo de pontos.
    * **Parceiro (Empresa):** Gestão de pontos de coleta e registro de entrada de itens.
* **Interface Responsiva**: Layout construído com **Bootstrap 5** e **Crispy Forms**.
* **Persistência NoSQL**: Conexão com MongoDB via **Djongo** para alta escalabilidade de registros.
* **Segurança**: Autenticação nativa do Django com extensão de perfil para CPF (Cidadão) e CNPJ (Parceiro).

---

## 🏛️ Arquitetura do Sistema

A aplicação segue a arquitetura **MVT (Model-View-Template)**, padrão do Django, estruturada da seguinte forma:

### 1. Model (Camada de Dados)
Definição das entidades e regras de negócio no banco de dados MongoDB.
* **Models:** `Cliente`, `Parceiro`, `PontoColeta`, `Item`.
* *Destaque:* Uso de relacionamentos e campos específicos para gamificação (`pontos`, `itens_descartados`).

### 2. View (Camada Lógica)
Controladores que processam as requisições HTTP.
* **Public Views:** Home, Quem Somos, Mapa (lógica de filtragem).
* **Auth Views:** Login, Logout, Registro de Cliente e Parceiro.
* **Dashboard Logic:** Lógica de área restrita para gestão de estoque e pontos.

### 3. Template (Camada de Apresentação)
Interface gráfica renderizada no servidor.
* Uso de herança de templates (`base.html`).
* Integração com bibliotecas estáticas (CSS/JS) e mapas.

---

## 🛠️ Tecnologias Utilizadas

* **Python 3**: Linguagem base.
* **Django 4.1.13**: Framework web principal.
* **MongoDB**: Banco de dados NoSQL.
* **Djongo 1.3.6**: Conector MongoDB para Django ORM.
* **Bootstrap 5**: Framework de UI/UX.
* **Leaflet.js**: Biblioteca de mapas interativos.
* **Crispy Forms**: Manipulação elegante de formulários.

---

## ⚙️ Como Executar

### Pré-requisitos

* Python 3.10+ instalado.
* MongoDB rodando localmente (porta 27017) ou string de conexão remota.

### Passos

1.  Clone o repositório:
    ```bash
    git clone [https://github.com/seu-usuario/e-saving-dj.git](https://github.com/seu-usuario/e-saving-dj.git)
    cd e-saving-dj
    ```

2.  Crie e ative um ambiente virtual:
    ```bash
    # Windows
    python -m venv venv
    .\venv\Scripts\activate

    # Linux/Mac
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```

4.  Configure o Banco de Dados:
    * Certifique-se de que o MongoDB está rodando.
    * O projeto espera um banco chamado `esaving_db` em `localhost:27017`.

5.  Aplique as migrações:
    ```bash
    python manage.py migrate
    ```

6.  (Opcional) Crie um superusuário:
    ```bash
    python manage.py createsuperuser
    ```

7.  Execute o servidor:
    ```bash
    python manage.py runserver
    ```

8.  Acesse: `http://127.0.0.1:8000`

---

## 🔌 Rotas Principais

| URL | Descrição | Permissão |
| :--- | :--- | :--- |
| `/` | Página Inicial | Pública |
| `/mapa/` | Busca e visualização de pontos | Pública |
| `/login/` | Autenticação de usuários | Pública |
| `/cadastro/cliente/` | Registro de Cidadão | Pública |
| `/cadastro/parceiro/` | Registro de Empresa | Pública |
| `/minha-area/` | Dashboard (Kpis e Gráficos) | Logado |
| `/parceiro/novo-ponto/` | Criar ponto de coleta | Parceiro |
| `/parceiro/novo-item/` | Registrar descarte/estoque | Parceiro |

---

## 📂 Estrutura de Pastas Relevante

```text
esaving/
├── app/
│   ├── migrations/  # Histórico de banco
│   ├── static/      # Imagens, CSS e JS (Leaflet, ícones)
│   ├── templates/   # Arquivos HTML (Bootstrap)
│   ├── forms.py     # Definição de formulários
│   ├── models.py    # Modelagem de dados (MongoDB)
│   ├── urls.py      # Rotas da aplicação
│   └── views.py     # Lógica de negócio
├── esaving/
│   ├── settings.py  # Configurações globais (Djongo, Apps)
│   └── urls.py      # Roteamento principal
├── media/           # Uploads de usuários (Fotos de perfil)
└── manage.py        # Utilitário de comando Django
