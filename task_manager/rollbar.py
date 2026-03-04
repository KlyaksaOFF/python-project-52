import os
import rollbar


def init_rollbar():
    """Инициализация Rollbar"""
    rollbar.init(
        access_token=os.getenv('ROLLBAR_ACCESS_TOKEN'),
        environment=os.getenv('ROLLBAR_ENVIRONMENT', 'development'),
        code_version='1.0.0',  # Обновляйте при деплое
    )

    # Добавляем обработчик для обогащения данных
    def payload_handler(payload, **kw):
        # Добавляем информацию о пользователе если доступна
        from django.contrib.auth.models import User
        from django.utils.deprecation import MiddlewareMixin

        request = kw.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            payload['data']['person'] = {
                'id': str(request.user.id),
                'username': request.user.username,
                'email': request.user.email,
            }

        # Добавляем кастомные данные
        payload['data']['custom'] = {
            'environment': os.getenv('ROLLBAR_ENVIRONMENT', 'development'),
            'framework': 'django',
        }

        return payload

    rollbar.events.add_payload_handler(payload_handler)