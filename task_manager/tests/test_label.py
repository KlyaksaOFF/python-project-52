from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from task_manager.models import Labels, Tasks, Status


class LabelsCRUDTest(TestCase):
    """Тесты для CRUD операций с метками"""

    def setUp(self):
        # Создаем пользователя и логинимся (как в вашей реализации)
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.login(username='testuser', password='testpass123')

        # Создаем метку для тестов
        self.label = Labels.objects.create(name='Test Label')

        # URLs (как в вашем urls.py)
        self.labels_url = reverse('labels')
        self.create_url = reverse('create_label')
        self.update_url = reverse('label_update', args=[self.label.pk])
        self.delete_url = reverse('label_delete', args=[self.label.pk])

    # --- READ (список меток) ---
    def test_labels_list_view(self):
        """Тест просмотра списка меток (GET /labels/)"""
        response = self.client.get(self.labels_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'label/labels.html')
        self.assertContains(response, 'Test Label')

    # --- CREATE (создание метки) ---
    def test_create_label_get(self):
        """Тест GET запроса на создание метки (страница формы)"""
        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'label/create_label.html')

    def test_create_label_post_success(self):
        """Тест успешного создания метки (POST с именем)"""
        data = {'name': 'New Label'}
        response = self.client.post(self.create_url, data)

        self.assertRedirects(response, self.labels_url)
        self.assertTrue(Labels.objects.filter(name='New Label').exists())

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('create' in str(m).lower() for m in messages))

    def test_create_label_post_empty_name(self):
        """Тест создания метки с пустым именем (должно вернуть ошибку)"""
        data = {'name': ''}
        response = self.client.post(self.create_url, data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'label/create_label.html')
        self.assertFalse(Labels.objects.filter(name='').exists())

    # --- UPDATE (обновление метки) ---
    def test_update_label_get(self):
        """Тест GET запроса на обновление метки"""
        response = self.client.get(self.update_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'label/update_label.html')
        self.assertEqual(response.context['label'], self.label)

    def test_update_label_post_success(self):
        """Тест успешного обновления имени метки"""
        data = {'name': 'Updated Label Name'}
        response = self.client.post(self.update_url, data)

        self.assertRedirects(response, self.labels_url)
        self.label.refresh_from_db()
        self.assertEqual(self.label.name, 'Updated Label Name')

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('updated' in str(m).lower() for m in messages))

    def test_update_label_post_empty_name(self):
        """Тест обновления метки с пустым именем (должно вернуть ошибку)"""
        data = {'name': ''}
        response = self.client.post(self.update_url, data)

        self.assertEqual(response.status_code, 200)
        self.label.refresh_from_db()
        self.assertEqual(self.label.name, 'Test Label')  # Имя не должно измениться

    # --- DELETE (удаление метки) ---
    def test_delete_label_get(self):
        """Тест GET запроса на удаление метки"""
        response = self.client.get(self.delete_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'label/delete_label.html')
        self.assertEqual(response.context['label'], self.label)

    def test_delete_label_post_success(self):
        """Тест успешного удаления метки (если она не связана с задачами)"""
        response = self.client.post(self.delete_url)

        self.assertRedirects(response, self.labels_url)
        self.assertFalse(Labels.objects.filter(pk=self.label.pk).exists())

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('remove' in str(m).lower() for m in messages))

    def test_delete_label_post_with_task_protected(self):
        """
        Тест невозможности удалить метку, связанную с задачей (важное требование).
        Создаем задачу, привязываем к ней метку и пытаемся удалить метку.
        """
        # Создаем статус и задачу, привязываем нашу метку
        status = Status.objects.create(name='Test Status')
        task = Tasks.objects.create(
            name='Task with Label',
            description='Test',
            status=status,
            author=self.user
        )
        task.labels.add(self.label)

        # Пытаемся удалить метку
        response = self.client.post(self.delete_url)

        self.assertTrue(Labels.objects.filter(pk=self.label.pk).exists())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'label/delete_label.html')

        messages = list(get_messages(response.wsgi_request))
        # ИЗМЕНИТЬ под ваше реальное сообщение
        self.assertTrue(any('Cannot delete label' in str(m) for m in messages))

    # --- БЕЗ АВТОРИЗАЦИИ ---
    def test_access_without_login(self):
        """Тест доступа к CRUD меткам без авторизации (должен редиректить на логин)"""
        self.client.logout()

        urls = [self.labels_url, self.create_url, self.update_url, self.delete_url]
        for url in urls:
            response = self.client.get(url)
            self.assertRedirects(response, f'/login/?next={url}')

        # Проверка POST запросов
        for url in [self.create_url, self.update_url, self.delete_url]:
            response = self.client.post(url, {'name': 'test'})
            self.assertRedirects(response, f'/login/?next={url}')