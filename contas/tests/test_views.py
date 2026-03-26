from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile


User = get_user_model()

class LoginViewTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.login_url = reverse('login')
        self.user = User.objects.create_user(
            email='teste@teste.com',
            password='123'
        )

    def tearDown(self):
        self.user.delete()

    def test_login_ok(self):
        """ Teste de login com credenciais corretas """
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'contas/login.html')
        data = {'email': self.user.email, 'senha': '123'}
        response = self.client.post(self.login_url, data)
        redirect_url = reverse(settings.LOGIN_REDIRECT_URL)
        self.assertRedirects(response, redirect_url)
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_error(self):
        """ Teste de login com credenciais incorretas """
        data = {'email': self.user.email, 'senha': '1234'}
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'contas/login.html')

class CadastroViewTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.register_url = reverse('cadastro')
        self.model_user = User

    def test_cadastro_ok(self):
        """ Teste de cadastro de usuário """
        data = {
            'first_name': 'primeiro nome', 'last_name': 'sobrenome',
            'email': 'meuemail@email.com', 'password1': 'senhasecret4', 'password2': 'senhasecret4'
        }
        response = self.client.post(self.register_url, data)
        index_url = reverse('perfil')
        self.assertRedirects(response, index_url)
        self.assertEqual(self.model_user.objects.count(), 1)

    def test_cadastro_senhas_diferentes(self):
        """ Teste de cadastro de usuário com senhas diferentes """
        data = {
            'first_name': 'primeiro nome', 'last_name': 'sobrenome',
            'email': 'meuemail2@email.com', 'password1': 'senhasecret4', 'password2': 'senhasecret3'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'contas/cadastro-usuario.html')
        self.assertEqual(self.model_user.objects.count(), 0)

    def test_cadastro_sem_email(self):
        """ Teste de cadastro de usuário com senhas diferentes """
        data = {
            'first_name': 'primeiro nome', 'last_name': 'sobrenome',
            'email': '', 'password1': 'senhasecret4', 'password2': 'senhasecret4'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'contas/cadastro-usuario.html')
        self.assertEqual(self.model_user.objects.count(), 0)


class CadastroUpdateTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse('perfil')
        self.user = User.objects.create_user(
            email='teste@teste.com',
            password='123'
        )

    def tearDown(self):
        self.user.delete()

    def test_update_perfil_ok(self):
        """ Teste atualizando dados de perfil do usuário """
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        foto = SimpleUploadedFile(
            'small.gif', small_gif, content_type='image/gif'
        )
        data = {
            'first_name': 'novo nome',
            'last_name': 'sobrenome novo',
            'email': 'teste_atualizado@teste.com',
            'biografia': 'Minha biografia de teste',
            'foto': foto,
            'facebook': 'https://facebook.com/perfil',
            'instagram': 'https://instagram.com/perfil',
            'twitter': 'https://twitter.com/perfil',
            'blog': 'https://meublog.com'
        }
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.client.login(email=self.user.email, password='123')
        response = self.client.post(self.url, data, format='multipart')
        self.assertRedirects(response, self.url)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'teste_atualizado@teste.com')
        self.assertEqual(self.user.first_name, 'novo nome')
        self.assertEqual(self.user.perfil.biografia, 'Minha biografia de teste')
        self.assertTrue(self.user.perfil.foto.url)
        self.assertEqual(self.user.perfil.facebook, 'https://facebook.com/perfil')
        self.assertEqual(self.user.perfil.instagram, 'https://instagram.com/perfil')
        self.assertEqual(self.user.perfil.twitter, 'https://twitter.com/perfil')
        self.assertEqual(self.user.perfil.blog, 'https://meublog.com')

    def test_update_user_error(self):
        """ Teste atualizando email com dados vazios """
        data = {'email': ''}
        self.client.login(email=self.user.email, password='123')
        response = self.client.post(self.url, data)
        self.assertFormError(response.context['form_user'], 'email', 'Este campo é obrigatório.')


class AlteracaoSenhaTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.url_alterar_senha = reverse('alterar_senha')
        self.user = User.objects.create_user(
            email='teste@teste.com',
            password='senha_secreta'
        )

    def tearDown(self):
        self.user.delete()

    def test_alteracao_senha_ok(self):
        """ Alteração de senha logado """
        self.client.login(email=self.user.email, password='senha_secreta')
        response = self.client.get(self.url_alterar_senha)
        self.assertTemplateUsed(response, 'contas/alterar-senha.html')
        self.assertEqual(response.status_code, 200)

        data = {
            'old_password' : 'senha_secreta',
            'new_password1': 'novaSenha123',
            'new_password2': 'novaSenha123'
        }
        response = self.client.post(self.url_alterar_senha, data)
        self.assertRedirects(response, reverse('home'))
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("novaSenha123"))

    def test_alteracao_senha_nao_autenticado(self):
        """ Acessando Alteração de senha sem estar logado """
        response = self.client.get(self.url_alterar_senha)
        self.assertRedirects(response, reverse('login') + f"?next={self.url_alterar_senha}")
        self.assertEqual(response.status_code, 302)

    def test_alterando_com_senha_antiga_incorreta(self):
        """ Alterando senha com senha antiga incorreta"""
        self.client.login(email=self.user.email, password='senha_secreta')
        data = {
            'old_password' : 'senha_secreta_errada',
            'new_password1': 'novaSenha123',
            'new_password2': 'novaSenha123'
        }
        response = self.client.post(self.url_alterar_senha, data)
        self.assertFormError(
            response.context['form'], 'old_password',
            'A senha antiga foi digitada incorretamente. Por favor, informe-a novamente.'
        )

    def test_alterando_senha_com_nova_senha_incorreta(self):
        """ Alterando senha com senha antiga incorreta"""
        self.client.login(email=self.user.email, password='senha_secreta')
        data = {
            'old_password' : 'senha_secreta',
            'new_password1': '123',
            'new_password2': '123'
        }
        response = self.client.post(self.url_alterar_senha, data)
        self.assertContains(response, "Esta senha é muito curta. Ela precisa conter pelo menos 8 caracteres.")
        self.assertContains(response, "Esta senha é muito comum.")
        self.assertContains(response, "Esta senha é inteiramente numérica.")


class RedefinirSenhaTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.url_login = reverse('login')
        self.user = User.objects.create_user(
            email='teste@teste.com',
            password='123'
        )

    def tearDown(self):
        self.user.delete()

    def test_redefinicao_senha_ok(self):
        """ Teste solicitar redefinicao de senha """

        # Testa rota e template
        response = self.client.get(reverse('redefinir_senha'))
        self.assertTemplateUsed(response, 'contas/redefinicao-senha/redefinir-senha.html')
        self.assertEqual(response.status_code, 200)
        data = {
            'email': 'teste@teste.com'
        }
        response = self.client.post(reverse('redefinir_senha'), data)
        self.assertRedirects(response, self.url_login)
        self.assertTemplateUsed(response, 'contas/redefinicao-senha/assunto-redefinir-senha')
        self.assertTemplateUsed(response, 'contas/redefinicao-senha/template-redefinir-senha.html')

        # Testa link de redefinição de senha gerado
        token = response.context[0]['token']
        uid = response.context[0]['uid']
        url_confirmar_redefinicao_senha = reverse('confirmar_redefinir_senha', kwargs={'token':token,'uidb64':uid})
        response = self.client.get(url_confirmar_redefinicao_senha, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'contas/redefinicao-senha/confirmar-redefinir-senha.html')

        # Testa redefinição de nova senha com dados incorretos
        reset_redirect = response.request["PATH_INFO"]
        self.assertEqual(reset_redirect, f"/confirmar_redefinir_senha/{uid}/set-password/")
        response = self.client.post(
            reset_redirect,
            {"new_password1": "123", "new_password2": "123"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Esta senha é muito curta. Ela precisa conter pelo menos 8 caracteres.")
        self.assertContains(response, "Esta senha é muito comum.")
        self.assertContains(response, "Esta senha é inteiramente numérica.")

        # Testa redefinição de nova senha com dados corretos
        response = self.client.post(
            reset_redirect,
            {"new_password1": "novaSenha123", "new_password2": "novaSenha123"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.url_login)

        # Testa acesso com nova senha
        response = self.client.post(
            self.url_login, {'email': self.user.email, 'senha': "novaSenha123"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("novaSenha123"))

        # Testa se link utilizado está inválido
        url_confirmar_redefinicao_senha = reverse('confirmar_redefinir_senha', kwargs={'token':token,'uidb64':uid})
        response = self.client.get(url_confirmar_redefinicao_senha, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "O link para validar senha é inválido")

    def test_redefinicao_senha_email_inexistente(self):
        """ Teste solicitar redefinicao de senha com email inexistente """
        data = {
            'email': 'email@teste.com'
        }
        response = self.client.post(reverse('redefinir_senha'), data)
        self.assertFormError(response.context['form'], 'email', 'Não existe um usuário com esse email')