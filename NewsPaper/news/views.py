from django.shortcuts import render
from django.views.generic import ListView
from django.views.generic import DetailView
from .models import Post

class PostList(ListView):
  # Указываем модель, объекты которой мы будем выводить
  model = Post
  # Поле, которое будет использоваться для сортировки объектов
  ordering = '-created'
  # Указываем имя шаблона, в котором будут все инструкции о том,
  # как именно пользователю должны быть показаны наши объекты
  template_name = 'postlist.html'
  # Это имя списка, в котором будут лежать все объекты.
  # Его надо указать, чтобы обратиться к списку объектов в html-шаблоне.
  context_object_name = 'posts'

class PostDetail(DetailView):
  model = Post
  template_name = 'post.html'
  context_object_name = 'post'
