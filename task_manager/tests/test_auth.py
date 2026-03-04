from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse


class UserRegistrationTest(TestCase):
    """Тесты регистрации пользователей (Create)"""

    def setUp(self):
        self.registration_url = reverse('registration_user')
        self.users_url = reverse('users')
        self.valid_user_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'username': 'johndoe',
            'password1': 'testpass123',
            'password2': 'testpass123',
        }

    def test_registration_page_status_code(self):
        """Тест доступности страницы регистрации"""
        response = self.client.get(self.registration_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auth/registrations.html')

    def test_successful_registration(self):
        """Тест успешной регистрации пользователя"""
        response = self.client.post(self.registration_url, self.valid_user_data)

        # Проверяем редирект на страницу входа
        self.assertRedirects(response, reverse('login'))

        # Проверяем что пользователь создан
        self.assertTrue(User.objects.filter(username='johndoe').exists())

        # Проверяем сообщение об успехе
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Registration successful' in str(m) for m in messages))

    def test_registration_with_mismatched_passwords(self):
        """Тест регистрации с несовпадающими паролями"""
        data = self.valid_user_data.copy()
        data['password2'] = 'wrongpassword'

        response = self.client.post(self.registration_url, data)

        # Не должно быть редиректа
        self.assertEqual(response.status_code, 200)

        # Пользователь не должен быть создан
        self.assertFalse(User.objects.filter(username='johndoe').exists())

        # Проверяем сообщение об ошибке
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("passwords don't match" in str(m).lower() for m in messages))

    def test_registration_with_short_password(self):
        """Тест регистрации с коротким паролем (меньше 3 символов)"""
        data = self.valid_user_data.copy()
        data['password1'] = '12'
        data['password2'] = '12'

        response = self.client.post(self.registration_url, data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auth/registrations.html')
        self.assertFalse(User.objects.filter(username='johndoe').exists())

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('password length must be more' in str(m).lower() for m in messages))

    def test_user_count_not_increased_after_failed_registration(self):
        from django.db import transaction
        """Тест что счетчик пользователей не увеличивается после неудачной регистрации"""
        # Создаем пользователя
        User.objects.create_user(username='johndoe', password='testpass123')

        # Считаем количество до
        initial_count = User.objects.count()

        # Пытаемся создать пользователя с тем же username во вложенной транзакции
        with transaction.atomic():
            response = self.client.post(self.registration_url, self.valid_user_data)
            # Транзакция автоматически откатится из-за ошибки

        # Проверяем что количество пользователей не изменилось
        self.assertEqual(User.objects.count(), initial_count)


class UserListTest(TestCase):
    """Тесты списка пользователей (Read)"""

    def setUp(self):
        self.users_url = reverse('users')

        # Создаем тестовых пользователей
        self.user1 = User.objects.create_user(
            username='user1',
            first_name='User',
            last_name='One',
            password='pass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            first_name='User',
            last_name='Two',
            password='pass123'
        )

    def test_users_list_status_code(self):
        """Тест доступности страницы со списком пользователей"""
        response = self.client.get(self.users_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auth/users.html')

    def test_users_list_content(self):
        """Тест содержимого страницы со списком пользователей"""
        response = self.client.get(self.users_url)

        # Проверяем что оба пользователя отображаются
        self.assertContains(response, 'user1')
        self.assertContains(response, 'user2')
        self.assertContains(response, 'User One')
        self.assertContains(response, 'User Two')

        # Проверяем количество пользователей в контексте
        self.assertEqual(len(response.context['users']), 2)


class UserUpdateTest(TestCase):
    """Тесты обновления пользователей (Update)"""

    def setUp(self):
        # Создаем пользователя
        self.user = User.objects.create_user(
            username='testuser',
            first_name='Test',
            last_name='User',
            password='testpass123'
        )
        self.update_url = reverse('update', args=[self.user.pk])
        self.login_url = reverse('login')

    def test_update_page_without_login(self):
        """Тест доступа к странице редактирования без авторизации"""
        response = self.client.get(self.update_url)
        expected_url = f'{self.login_url}?next={self.update_url}'
        self.assertRedirects(response, expected_url)

    def test_update_page_with_login(self):
        """Тест доступа к странице редактирования с авторизацией"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.update_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auth/update_user.html')

        # Проверяем что в контексте есть пользователь
        self.assertEqual(response.context['auth'], self.user)

    def test_successful_update(self):
        """Тест успешного обновления пользователя"""
        self.client.login(username='testuser', password='testpass123')

        updated_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'username': 'updateduser',
            'password1': '',
            'password2': '',
        }

        response = self.client.post(self.update_url, updated_data)

        # Должен быть редирект на список пользователей
        self.assertRedirects(response, reverse('users'))

        # Обновляем пользователя из БД
        self.user.refresh_from_db()

        # Проверяем что данные обновились
        self.assertEqual(self.user.first_name, 'Updated')
        self.assertEqual(self.user.last_name, 'Name')
        self.assertEqual(self.user.username, 'updateduser')

        # Проверяем сообщение об успехе
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('User updated' in str(m) for m in messages))

    def test_update_with_new_password(self):
        """Тест обновления пароля пользователя"""
        self.client.login(username='testuser', password='testpass123')

        updated_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'username': 'testuser',
            'password1': 'newpassword123',
            'password2': 'newpassword123',
        }

        response = self.client.post(self.update_url, updated_data)
        self.assertRedirects(response, reverse('users'))

        # Проверяем что можно залогиниться с новым паролем
        self.client.logout()
        login_success = self.client.login(
            username='testuser',
            password='newpassword123'
        )
        self.assertTrue(login_success)

    def test_update_with_mismatched_passwords(self):
        """Тест обновления с несовпадающими паролями"""
        self.client.login(username='testuser', password='testpass123')

        updated_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'username': 'testuser',
            'password1': 'newpassword123',
            'password2': 'differentpassword',
        }

        response = self.client.post(self.update_url, updated_data)

        # Нет редиректа, остаемся на странице
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auth/update_user.html')

        # Пароль не должен измениться
        self.client.logout()
        login_success = self.client.login(
            username='testuser',
            password='testpass123'
        )
        self.assertTrue(login_success)


class UserDeleteTest(TestCase):
    """Тесты удаления пользователей (Delete)"""

    def setUp(self):
        # Создаем пользователя
        self.user = User.objects.create_user(
            username='testuser',
            first_name='Test',
            last_name='User',
            password='testpass123'
        )
        self.delete_url = reverse('delete', args=[self.user.pk])
        self.login_url = reverse('login')

        # Создаем второго пользователя для тестов прав
        self.other_user = User.objects.create_user(
            username='otheruser',
            password='otherpass123'
        )

    def test_delete_page_without_login(self):
        """Тест доступа к странице удаления без авторизации"""
        response = self.client.get(self.delete_url)
        expected_url = f'{self.login_url}?next={self.delete_url}'
        self.assertRedirects(response, expected_url)

    def test_delete_page_with_login(self):
        """Тест доступа к странице удаления с авторизацией"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.delete_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auth/confirm_delete.html')

    def test_successful_delete(self):
        """Тест успешного удаления пользователя"""
        self.client.login(username='testuser', password='testpass123')

        response = self.client.post(self.delete_url)

        # Проверяем редирект
        self.assertRedirects(response, reverse('users'))

        # Проверяем что пользователь удален
        self.assertFalse(User.objects.filter(username='testuser').exists())

        # Проверяем сообщение
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('remove' in str(m).lower() for m in messages))

    def test_cannot_delete_other_user(self):
        """Тест что нельзя удалить другого пользователя"""
        self.client.login(username='otheruser', password='otherpass123')

        # Пытаемся удалить первого пользователя
        response = self.client.post(self.delete_url)

        # Проверяем что пользователь не удален
        self.assertTrue(User.objects.filter(username='testuser').exists())

        # Должен быть редирект или сообщение об ошибке
        self.assertEqual(response.status_code, 302)  # или 200 в зависимости от реализации


class UserAuthenticationTest(TestCase):
    """Тесты аутентификации (Login/Logout)"""

    def setUp(self):
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.index_url = reverse('index')

        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_login_page_status_code(self):
        """Тест доступности страницы входа"""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auth/login.html')

    def test_successful_login(self):
        """Тест успешного входа"""
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpass123'
        })

        self.assertRedirects(response, self.index_url)

        # Проверяем что пользователь авторизован
        self.assertTrue('_auth_user_id' in self.client.session)

    def test_login_with_invalid_credentials(self):
        """Тест входа с неверными данными"""
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'wrongpassword'
        })

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auth/login.html')

        # Проверяем что пользователь не авторизован
        self.assertFalse('_auth_user_id' in self.client.session)

        # Проверяем сообщение об ошибке
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('invalid username or password' in str(m).lower() for m in messages))

    def test_login_with_nonexistent_user(self):
        """Тест входа с несуществующим пользователем"""
        response = self.client.post(self.login_url, {
            'username': 'nonexistent',
            'password': 'testpass123'
        })

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auth/login.html')
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_logout(self):
        """Тест выхода из системы"""
        # Сначала логинимся
        self.client.login(username='testuser', password='testpass123')
        self.assertTrue('_auth_user_id' in self.client.session)

        # Выходим
        response = self.client.post(self.logout_url)

        self.assertRedirects(response, self.index_url)

        # Проверяем что пользователь вышел
        self.assertFalse('_auth_user_id' in self.client.session)