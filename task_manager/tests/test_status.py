from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from task_manager.models import Status
from django.contrib.messages import get_messages


class StatusCRUDTest(TestCase):

    def setUp(self):
        # Создаем пользователя и логинимся (как в вашей реализации)
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.login(username='testuser', password='testpass123')

        # Создаем статус для тестов
        self.status = Status.objects.create(name='Test Status')

        # URLs (как в вашем urls.py)
        self.statuses_url = reverse('statuses')
        self.create_url = reverse('status_create')
        self.update_url = reverse('status_update', args=[self.status.pk])
        self.delete_url = reverse('status_delete', args=[self.status.pk])

    # READ - список статусов
    def test_status_list_view(self):
        """Тест просмотра списка статусов"""
        response = self.client.get(self.statuses_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'status/statuses.html')
        self.assertContains(response, 'Test Status')

    # CREATE - создание статуса
    def test_create_status_get(self):
        """Тест GET запрос на создание статуса"""
        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'status/create_status.html')

    def test_create_status_post_success(self):
        """Тест успешного создания статуса"""
        data = {'name': 'New Status'}
        response = self.client.post(self.create_url, data)

        self.assertRedirects(response, self.statuses_url)
        self.assertTrue(Status.objects.filter(name='New Status').exists())

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('create' in str(m).lower() for m in messages))

    def test_create_status_post_empty(self):
        """Тест создания статуса с пустым именем"""
        data = {'name': ''}
        response = self.client.post(self.create_url, data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'status/create_status.html')
        self.assertFalse(Status.objects.filter(name='').exists())

    # UPDATE - обновление статуса
    def test_update_status_get(self):
        """Тест GET запрос на обновление статуса"""
        response = self.client.get(self.update_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'status/update_status.html')
        self.assertEqual(response.context['status'], self.status)

    def test_update_status_post_success(self):
        """Тест успешного обновления статуса"""
        data = {'name': 'Updated Status'}
        response = self.client.post(self.update_url, data)

        self.assertRedirects(response, self.statuses_url)
        self.status.refresh_from_db()
        self.assertEqual(self.status.name, 'Updated Status')

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('updated' in str(m).lower() for m in messages))

    def test_update_status_post_empty(self):
        """Тест обновления статуса с пустым именем"""
        data = {'name': ''}
        response = self.client.post(self.update_url, data)

        self.assertEqual(response.status_code, 200)
        self.status.refresh_from_db()
        self.assertEqual(self.status.name, 'Test Status')

    # DELETE - удаление статуса
    def test_delete_status_get(self):
        """Тест GET запрос на удаление статуса"""
        response = self.client.get(self.delete_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'status/delete_status.html')
        self.assertEqual(response.context['status'], self.status)

    def test_delete_status_post_success(self):
        """Тест успешного удаления статуса"""
        response = self.client.post(self.delete_url)

        self.assertRedirects(response, self.statuses_url)
        self.assertFalse(Status.objects.filter(pk=self.status.pk).exists())

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('remove' in str(m).lower() for m in messages))

    # Без авторизации
    def test_access_without_login(self):
        """Тест доступа без авторизации"""
        self.client.logout()

        # Проверяем все URL
        urls = [self.statuses_url, self.create_url, self.update_url, self.delete_url]
        for url in urls:
            response = self.client.get(url)
            self.assertRedirects(response, f'/login/?next={url}')