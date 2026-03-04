from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from task_manager.models import Tasks, Status, Labels

class TasksFilterTest(TestCase):
    """Тесты для фильтрации задач"""

    def setUp(self):
        # Создаем пользователей
        self.user1 = User.objects.create_user(
            username='user1',
            password='pass123',
            first_name='User',
            last_name='One'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            password='pass123',
            first_name='User',
            last_name='Two'
        )

        # Логинимся
        self.client.login(username='user1', password='pass123')

        # Создаем статусы
        self.status1 = Status.objects.create(name='Status 1')
        self.status2 = Status.objects.create(name='Status 2')

        # Создаем метки
        self.label1 = Labels.objects.create(name='Label 1')
        self.label2 = Labels.objects.create(name='Label 2')

        # Создаем задачи
        self.task1 = Tasks.objects.create(
            name='Task 1',
            description='Description 1',
            status=self.status1,
            author=self.user1,
            executor=self.user1
        )

        self.task2 = Tasks.objects.create(
            name='Task 2',
            description='Description 2',
            status=self.status1,
            author=self.user1,
            executor=self.user2
        )

        self.task3 = Tasks.objects.create(
            name='Task 3',
            description='Description 3',
            status=self.status2,
            author=self.user2,
            executor=self.user1
        )

        self.task4 = Tasks.objects.create(
            name='Task 4',
            description='Description 4',
            status=self.status2,
            author=self.user2,
            executor=self.user2
        )

        # Добавляем метки к задачам
        self.task1.labels.add(self.label1)
        self.task2.labels.add(self.label2)
        self.task3.labels.add(self.label1, self.label2)
        # task4 без меток

        self.tasks_url = reverse('tasks')

    def test_filter_by_status(self):
        """Тест фильтрации по статусу"""
        response = self.client.get(self.tasks_url, {'status': self.status1.id})
        self.assertEqual(response.status_code, 200)

        tasks = response.context['tasks']
        self.assertEqual(tasks.count(), 2)
        self.assertIn(self.task1, tasks)
        self.assertIn(self.task2, tasks)

    def test_filter_by_executor(self):
        """Тест фильтрации по исполнителю"""
        response = self.client.get(self.tasks_url, {'executor': self.user1.id})
        self.assertEqual(response.status_code, 200)

        tasks = response.context['tasks']
        self.assertEqual(tasks.count(), 2)
        self.assertIn(self.task1, tasks)
        self.assertIn(self.task3, tasks)

    def test_filter_by_label(self):
        """Тест фильтрации по метке"""
        response = self.client.get(self.tasks_url, {'label': self.label1.id})
        self.assertEqual(response.status_code, 200)

        tasks = response.context['tasks']
        self.assertEqual(tasks.count(), 2)
        self.assertIn(self.task1, tasks)
        self.assertIn(self.task3, tasks)

    def test_filter_self_tasks(self):
        """Тест фильтрации 'только свои задачи' (по исполнителю)"""
        response = self.client.get(self.tasks_url, {'self_tasks': 'on'})
        self.assertEqual(response.status_code, 200)

        tasks = response.context['tasks']
        # В вашей реализации фильтр по executor=user1
        # Должны быть task1 (executor=user1) и task3 (executor=user1)
        self.assertEqual(tasks.count(), 2)
        self.assertIn(self.task1, tasks)
        self.assertIn(self.task3, tasks)

    def test_combined_filters_status_and_self(self):
        """Тест комбинации фильтров: статус + свои задачи"""
        response = self.client.get(self.tasks_url, {
            'status': self.status1.id,
            'self_tasks': 'on'
        })
        self.assertEqual(response.status_code, 200)

        tasks = response.context['tasks']
        # Статус 1: task1, task2
        # Свои (executor=user1): task1, task3
        # Пересечение: task1
        self.assertEqual(tasks.count(), 1)
        self.assertIn(self.task1, tasks)

    def test_combined_filters_status_and_label(self):
        """Тест комбинации фильтров: статус + метка"""
        response = self.client.get(self.tasks_url, {
            'status': self.status2.id,
            'label': self.label1.id
        })
        self.assertEqual(response.status_code, 200)

        tasks = response.context['tasks']
        # Статус 2: task3, task4
        # Метка 1: task1, task3
        # Пересечение: task3
        self.assertEqual(tasks.count(), 1)
        self.assertIn(self.task3, tasks)

    def test_filter_no_results(self):
        """Тест фильтрации без результатов"""
        # Статус 1 + метка 2 + свои задачи (executor=user1)
        response = self.client.get(self.tasks_url, {
            'status': self.status1.id,
            'label': self.label2.id,
            'self_tasks': 'on'
        })
        self.assertEqual(response.status_code, 200)

        tasks = response.context['tasks']
        # Статус 1: task1, task2
        # Метка 2: task2, task3
        # Свои: task1, task3
        # Пересечение всех трех: нет
        self.assertEqual(tasks.count(), 0)

    def test_filter_preserves_get_params(self):
        """Тест что параметры фильтрации сохраняются"""
        response = self.client.get(self.tasks_url, {
            'status': self.status1.id,
            'executor': self.user1.id
        })
        self.assertEqual(response.status_code, 200)

        # Проверяем что параметры в GET запросе сохранились
        self.assertEqual(
            response.context['request'].GET.get('status'),
            str(self.status1.id)
        )
        self.assertEqual(
            response.context['request'].GET.get('executor'),
            str(self.user1.id)
        )

    def test_filter_without_login(self):
        """Тест доступа к странице задач без авторизации"""
        self.client.logout()
        response = self.client.get(self.tasks_url, {'status': self.status1.id})
        # Проверяем редирект с сохранением query параметров
        expected_url = f'/login/?next={self.tasks_url}%3Fstatus%3D{self.status1.id}'
        self.assertRedirects(response, expected_url)


class TasksFilterFormTest(TestCase):
    """Тесты для формы фильтрации в шаблоне"""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass123')
        self.client.login(username='testuser', password='pass123')

        # Создаем данные для фильтров
        Status.objects.create(name='Status A')
        Status.objects.create(name='Status B')
        Labels.objects.create(name='Label X')
        Labels.objects.create(name='Label Y')

        self.tasks_url = reverse('tasks')

    def test_filter_form_fields_present(self):
        """Тест что все поля фильтрации присутствуют в форме"""
        response = self.client.get(self.tasks_url)
        self.assertEqual(response.status_code, 200)

        # Проверяем наличие полей фильтрации
        self.assertContains(response, 'name="status"')
        self.assertContains(response, 'name="executor"')
        self.assertContains(response, 'name="label"')
        self.assertContains(response, 'name="self_tasks"')

        # Проверяем наличие кнопки Show
        self.assertContains(response, 'type="submit"')
        self.assertContains(response, 'Show')

    def test_filter_form_has_css_classes(self):
        """Тест что поля фильтрации имеют правильные CSS классы"""
        response = self.client.get(self.tasks_url)

        # Проверяем классы из filters.py
        self.assertContains(response, 'class="form-select"')
        self.assertContains(response, 'class="form-check-input"')