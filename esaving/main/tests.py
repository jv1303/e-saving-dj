from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Coleta

User = get_user_model()

class CadastroTestCase(TestCase):
    def setUp(self):
        self.user_data = {
            'username': 'testpoint',
            'email': 'test@example.com',
            'telefone': '(11) 99999-9999',
            'cep': '01234-567',
            'cpf_cnpj': '12345678901',
            'endereco': 'Rua Teste, 123',
            'password1': 'TestPass123',
            'password2': 'TestPass123',
        }
    
    def test_cadastro_page(self):
        response = self.client.get(reverse('cadastro'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Cadastro de Ponto de Coleta')
    
    def test_cadastro_success(self):
        response = self.client.post(reverse('cadastro'), self.user_data)
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertTrue(User.objects.filter(username='testpoint').exists())

class LoginTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_login_page(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Login')
    
    def test_login_success(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass123',
            'remember_me': False
        })
        self.assertEqual(response.status_code, 302)

class AreaParceiroTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
    
    def test_area_parceiro_protected(self):
        response = self.client.get(reverse('area_parceiro'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Área do Parceiro')