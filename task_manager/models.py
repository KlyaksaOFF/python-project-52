from django.contrib.auth.models import User
from django.db import models


class Status(models.Model):
    name = models.CharField(max_length=50)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Labels(models.Model):
    name = models.CharField(max_length=50)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Tasks(models.Model):
    name = models.CharField(max_length=50)

    description = models.CharField(max_length=200)

    status = models.ForeignKey(Status, on_delete=models.PROTECT)

    author = models.ForeignKey(User, on_delete=models.PROTECT,
    related_name='authored_tasks')

    executor = models.ForeignKey(User, on_delete=models.PROTECT,
    related_name='executed_tasks', null=True, blank=True)

    labels = models.ManyToManyField(Labels)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name