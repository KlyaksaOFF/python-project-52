from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from task_manager.models import Labels, Status, Tasks

from .filters import TasksFilter
from .rollbar import rollbar


@require_http_methods(['GET'])
def index(request):
    return render(request, 'index.html')


# Пользователи
@csrf_exempt
@require_http_methods(['GET', 'POST'])
def registration_user(request):
    if request.method == 'POST':
        data = {
            'first_name': request.POST['first_name'],
            'last_name': request.POST['last_name'],
            'username': request.POST['username'],
            'password': request.POST['password1'],
        }
        if len(request.POST['password1']) < 3:
            messages.error(request, 'The password length must be more '
                                   'than 3 characters.')
            return render(request, 'auth/registrations.html')

        if request.POST['password1'] != request.POST['password2']:
            messages.error(request, "The passwords don't match")
            return render(request, 'auth/registrations.html')

        try:
            User.objects.create_user(**data)
            messages.success(request, 'Пользователь успешно зарегистрирован')
            return redirect('login')

        except IntegrityError:
            messages.error(request, "уже существует")

    return render(request, 'auth/registrations.html')


@csrf_exempt
@require_http_methods(['GET', 'POST'])
def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            messages.success(request, 'Вы залогинены')
            login(request, user)
            return redirect('index')

        else:
            messages.error(request, 'Неправильное имя или пароль')

    return render(request, 'auth/login.html')


@require_http_methods(['GET'])
def users(request):
    users = User.objects.all().order_by('username')
    return render(request, 'auth/users.html', {'users': users})


@login_required
@require_http_methods(['POST'])
def logout(request):
    request.session.flush()
    messages.success(request, 'Вы разлогинены')
    return redirect('index')


@login_required
@csrf_exempt
@require_http_methods(['GET', 'POST'])
def update_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.user != user:
        messages.error(request, "You can only edit your own profile")
        return redirect('users')

    if request.method == 'POST':
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.username = request.POST.get('username')
        if request.POST['password1']:
            if request.POST.get('password1') == request.POST.get('password2'):
                user.set_password(request.POST.get('password1'))
            else:
                messages.error(request, "The passwords don't match!")
                return render(request, 'auth/update_user.html', {'auth': user})
        user.save()
        messages.success(request, 'Пользователь успешно изменен')
        request.session.flush()
        return redirect('users')
    return render(request, 'auth/update_user.html', {'auth': user})


@login_required
@csrf_exempt
@require_http_methods(['GET', 'POST'])
def delete_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.user != user:
        messages.error(request, "You can only edit your own profile")
        return redirect('users')

    if request.method == 'POST':
        user.delete()
        messages.success(request, 'Пользователь успешно удален')
        return redirect('users')
    return render(request, 'auth/confirm_delete.html', {'auth': user})


@login_required
@csrf_exempt
@require_http_methods(['GET'])
def status(request):
    statuses = Status.objects.all()
    return render(request, 'status/statuses.html', {'statuses': statuses})


@login_required
@csrf_exempt
@require_http_methods(['GET', 'POST'])
def delete_status(request, pk):
    status = get_object_or_404(Status, pk=pk)

    if status.tasks_set.exists():
        messages.error(request, 'Невозможно удалить статус')
        return render(request, 'status/delete_status.html', {'status': status})

    if request.method == 'POST':
        status.delete()
        messages.success(request, 'Статус успешно удален')
        return redirect('statuses')
    return render(request, 'status/delete_status.html', {'status': status})


@login_required
@csrf_exempt
@require_http_methods(['GET', 'POST'])
def status_create(request):
    try:
        if request.method == 'POST':
            name = request.POST.get('name')
            if name:
                Status.objects.create(name=name)
                messages.success(request, 'Статус успешно создан')
                return redirect('statuses')
    except IntegrityError:
        messages.error(request, "уже существует")
    return render(request, 'status/create_status.html')


@login_required
@csrf_exempt
@require_http_methods(['GET', 'POST'])
def update_status(request, pk):
    status = get_object_or_404(Status, pk=pk)
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            status.name = name
            status.save()
            messages.success(request, 'Статус успешно изменен')
            return redirect('statuses')
        else:
            messages.error(request, 'Error')

    return render(request, 'status/update_status.html', {'status': status})


@login_required
@csrf_exempt
@require_http_methods(['GET'])
def label(request):
    labels = Labels.objects.all()
    return render(request, 'label/labels.html', {'labels': labels})


@login_required
@csrf_exempt
@require_http_methods(['GET', 'POST'])
def create_label(request):
    try:
        if request.method == 'POST':
            name = request.POST.get('name')
            if name:
                Labels.objects.create(name=name)
                messages.success(request, 'Метка успешно создана')
                return redirect('labels')
    except IntegrityError:
        messages.error(request, "уже существует")
    return render(request, 'label/create_label.html')


@login_required
@csrf_exempt
@require_http_methods(['GET', 'POST'])
def update_label(request, pk):
    label = get_object_or_404(Labels, pk=pk)
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            label.name = name
            label.save()
            messages.success(request, 'Метка успешно изменена')
            return redirect('labels')
        else:
            messages.error(request, 'Error')
    return render(request, 'label/update_label.html', {'label': label})


@login_required
@csrf_exempt
@require_http_methods(['GET', 'POST'])
def delete_label(request, pk):
    label = get_object_or_404(Labels, pk=pk)
    if label.tasks_set.exists():
        messages.error(request, 'Невозможно удалить метку')
        return render(request, 'label/delete_label.html', {'label': label})
    if request.method == 'POST':
        label.delete()
        messages.success(request, 'Метка успешно удалена')
        return redirect('labels')
    return render(request, 'label/delete_label.html', {'label': label})


# Задачи
@csrf_exempt
@login_required
@require_http_methods(['GET', 'POST'])
def create_task(request):
    try:
        if request.method == 'POST':
            status = Status.objects.get(id=request.POST.get('status'))

            executor = User.objects.get(id=request.POST.get('executor')) if (
                request.POST.get('executor')) else None

            task = Tasks.objects.create(
                name=request.POST.get('name'),
                description=request.POST.get('description'),
                status=status,
                author=request.user,
                executor=executor
            )

            labels_ids = request.POST.getlist('labels')
            if labels_ids:
                labels = Labels.objects.filter(id__in=labels_ids)
                task.labels.set(labels)
            messages.success(request, 'Задача успешно создана')
            return redirect('tasks')
    except IntegrityError:
        messages.error(request, "уже существует")
    labels = Labels.objects.all()
    statuses = Status.objects.all()
    users = User.objects.all()

    return render(request, 'task/create_task.html', {
        'labels': labels,
        'statuses': statuses,
        'users': users
    })


@csrf_exempt
@require_http_methods(['GET'])
@login_required
def tasks_list(request):
    tasks = Tasks.objects.all()
    task_filter = TasksFilter(request.GET, queryset=tasks, request=request)

    context = {
        'filter': task_filter,
        'tasks': task_filter.qs
    }
    return render(request, 'task/tasks.html', context)


@login_required
@csrf_exempt
@require_http_methods(['GET', 'POST'])
def delete_task(request, pk):
    task = get_object_or_404(Tasks, pk=pk)
    if request.user != task.author:
        messages.error(request, "Задачу может удалить только ее автор")
        return redirect('tasks')
    if request.method == 'POST':
        messages.success(request, 'Задача успешно удалена')
        task.delete()
        return redirect('tasks')
    return render(request, 'task/delete_task.html', {'task': task})


@csrf_exempt
@require_http_methods(['GET', 'POST'])
@login_required
def task_update(request, pk):
    task = get_object_or_404(Tasks, pk=pk)
    if request.user != task.author:
        messages.error(request, "Задачу может обновить только ее автор")
        return redirect('tasks')
    if request.method == 'POST':
        task.name = request.POST.get('name')
        task.description = request.POST.get('description')
        task.status_id = request.POST.get('status')
        task.executor_id = request.POST.get('executor') or None

        task.save()

        label_ids = request.POST.getlist('labels')
        task.labels.set(label_ids)

        messages.success(request, 'Задача успешно изменена')
        return redirect('task_detail', pk=task.pk)

    context = {
        'task': task,
        'statuses': Status.objects.all(),
        'users': User.objects.all(),
        'labels': Labels.objects.all(),
    }
    return render(request, 'task/update_task.html', context)


@csrf_exempt
@require_http_methods(['GET', 'POST'])
@login_required
def task_detail(request, pk):
    task = get_object_or_404(Tasks, pk=pk)

    context = {
        'task': task
    }
    return render(request, 'task/task_detail.html', context)


@login_required
def test_rollbar(request):
    rollbar.report_message(
        'Rollbar test from task_manager',
        'info',
        request=request,
        extra_data={'test': True}
    )

    # Создаем тестовое исключение
    try:
        raise ValueError('This is a test exception for Rollbar')
    except Exception:
        rollbar.report_exc_info(request=request)

    messages.success(request, 'Test error sent to Rollbar!')
    return redirect('index')
