from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from task_manager.models import Tasks, Status, Labels


class TasksCRUDTest(TestCase):

    def setUp(self):
        # Создаем пользователя и логинимся
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.login(username='testuser', password='testpass123')

        # Создаем дополнительные данные
        self.status = Status.objects.create(name='Test Status')
        self.label1 = Labels.objects.create(name='Label 1')
        self.label2 = Labels.objects.create(name='Label 2')

        # Создаем задачу для тестов
        self.task = Tasks.objects.create(
            name='Test Task',
            description='Test Description',
            status=self.status,
            author=self.user,
            executor=self.user
        )
        self.task.labels.set([self.label1, self.label2])

        # URLs
        self.tasks_url = reverse('tasks')
        self.create_url = reverse('task_create')
        self.detail_url = reverse('task_detail', args=[self.task.pk])
        self.update_url = reverse('task_update', args=[self.task.pk])
        self.delete_url = reverse('task_delete', args=[self.task.pk])

    # LIST - список задач
    def test_tasks_list_view(self):
        """Тест просмотра списка задач"""
        response = self.client.get(self.tasks_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'task/tasks.html')
        self.assertContains(response, 'Test Task')

    # DETAIL - просмотр задачи
    def test_task_detail_view(self):
        """Тест просмотра конкретной задачи"""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'task/task_detail.html')
        self.assertEqual(response.context['task'], self.task)
        self.assertContains(response, 'Test Task')
        self.assertContains(response, 'Test Description')

    # CREATE - создание задачи
    def test_create_task_get(self):
        """Тест GET запрос на создание задачи"""
        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'task/create_task.html')
        self.assertIn('statuses', response.context)
        self.assertIn('users', response.context)
        self.assertIn('labels', response.context)

    def test_create_task_post_success(self):
        """Тест успешного создания задачи"""
        data = {
            'name': 'New Task',
            'description': 'New Description',
            'status': self.status.id,
            'executor': self.user.id,
            'labels': [self.label1.id, self.label2.id]
        }
        response = self.client.post(self.create_url, data)

        self.assertRedirects(response, self.tasks_url)
        self.assertTrue(Tasks.objects.filter(name='New Task').exists())

        task = Tasks.objects.get(name='New Task')
        self.assertEqual(task.description, 'New Description')
        self.assertEqual(task.status, self.status)
        self.assertEqual(task.author, self.user)
        self.assertEqual(task.executor, self.user)
        self.assertEqual(task.labels.count(), 2)

    def test_create_task_post_without_executor(self):
        """Тест создания задачи без исполнителя"""
        data = {
            'name': 'Task No Executor',
            'description': 'Description',
            'status': self.status.id,
            'executor': '',
            'labels': []
        }
        response = self.client.post(self.create_url, data)

        self.assertRedirects(response, self.tasks_url)
        task = Tasks.objects.get(name='Task No Executor')
        self.assertIsNone(task.executor)

    def test_create_task_post_without_labels(self):
        """Тест создания задачи без меток"""
        data = {
            'name': 'Task No Labels',
            'description': 'Description',
            'status': self.status.id,
            'executor': self.user.id,
            'labels': []
        }
        response = self.client.post(self.create_url, data)

        self.assertRedirects(response, self.tasks_url)
        task = Tasks.objects.get(name='Task No Labels')
        self.assertEqual(task.labels.count(), 0)

    # UPDATE - обновление задачи
    def test_update_task_get(self):
        """Тест GET запрос на обновление задачи"""
        response = self.client.get(self.update_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'task/update_task.html')
        self.assertEqual(response.context['task'], self.task)

    def test_update_task_post_success(self):
        """Тест успешного обновления задачи"""
        data = {
            'name': 'Updated Task',
            'description': 'Updated Description',
            'status': self.status.id,
            'executor': '',
            'labels': [self.label1.id]
        }
        response = self.client.post(self.update_url, data)

        self.assertRedirects(response, reverse('task_detail', args=[self.task.pk]))

        self.task.refresh_from_db()
        self.assertEqual(self.task.name, 'Updated Task')
        self.assertEqual(self.task.description, 'Updated Description')
        self.assertIsNone(self.task.executor)
        self.assertEqual(self.task.labels.count(), 1)

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('изменена' in str(m).lower() for m in messages))

    def test_update_task_post_partial(self):
        """Тест частичного обновления задачи"""
        data = {
            'name': 'Partially Updated',
            'description': self.task.description,
            'status': self.status.id,
            'executor': self.user.id,
            'labels': []
        }
        response = self.client.post(self.update_url, data)

        self.assertRedirects(response, self.detail_url)
        self.task.refresh_from_db()
        self.assertEqual(self.task.name, 'Partially Updated')
        self.assertEqual(self.task.labels.count(), 0)

    # DELETE - удаление задачи
    def test_delete_task_get(self):
        """Тест GET запрос на удаление задачи"""
        response = self.client.get(self.delete_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'task/delete_task.html')
        self.assertEqual(response.context['task'], self.task)

    def test_delete_task_post_success(self):
        """Тест успешного удаления задачи"""
        response = self.client.post(self.delete_url)

        self.assertRedirects(response, self.tasks_url)
        self.assertFalse(Tasks.objects.filter(pk=self.task.pk).exists())

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('remove' in str(m).lower() for m in messages))

    def test_delete_task_by_non_author(self):
        """Тест удаления задачи не автором"""
        # Создаем другого пользователя
        other_user = User.objects.create_user(username='other', password='otherpass')
        self.client.login(username='other', password='otherpass')

        response = self.client.post(self.delete_url)

        # Задача должна остаться
        self.assertTrue(Tasks.objects.filter(pk=self.task.pk).exists())
        # Должно быть сообщение об ошибке (проверка зависит от вашей реализации)

    # PERMISSIONS - права доступа
    def test_update_task_by_non_author(self):
        """Тест обновления задачи не автором"""
        other_user = User.objects.create_user(username='other', password='otherpass')
        self.client.login(username='other', password='otherpass')

        data = {
            'name': 'Hacked Task',
            'description': 'Hacked',
            'status': self.status.id,
            'executor': '',
            'labels': []
        }
        response = self.client.post(self.update_url, data)

        # Задача не должна измениться (зависит от вашей реализации)
        self.task.refresh_from_db()
        self.assertEqual(self.task.name, 'Test Task')

    # FILTER - фильтрация задач (если есть в tasks_list)
    def test_tasks_list_filter_by_status(self):
        """Тест фильтрации задач по статусу"""
        response = self.client.get(self.tasks_url, {'status': self.status.id})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Task')

    def test_tasks_list_filter_self_tasks(self):
        """Тест фильтрации 'только свои задачи'"""
        response = self.client.get(self.tasks_url, {'self_tasks': 'on'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Task')

    # WITHOUT LOGIN - без авторизации
    def test_access_without_login(self):
        """Тест доступа без авторизации"""
        self.client.logout()

        urls = [
            self.tasks_url,
            self.create_url,
            self.update_url,
            self.delete_url,
            self.detail_url
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertRedirects(response, f'/login/?next={url}')