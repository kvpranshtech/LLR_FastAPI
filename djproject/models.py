# app/books/models.py
from django.db import models


class Author(models.Model):
    name = models.CharField(max_length=200)


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    pages = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
