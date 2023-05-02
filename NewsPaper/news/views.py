from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import (LoginRequiredMixin, PermissionRequiredMixin)
from news.filters import PostFilter
from django.db.models import Exists, OuterRef
from .forms import CreatePostForm
from .models import (Post, Category, Subscription)

class PostList(LoginRequiredMixin, ListView):
  raise_exception = True
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

  paginate_by = 10

  def get_queryset(self):
    queryset = super().get_queryset()
    self.filterset = PostFilter(self.request.GET, queryset)
    return self.filterset.qs
  
  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    # Добавляем в контекст объект фильтрации.
    context['filterset'] = self.filterset
    return context

class PostSearch(LoginRequiredMixin, ListView):
  raise_exception = True
  # Указываем модель, объекты которой мы будем выводить
  model = Post
  # Поле, которое будет использоваться для сортировки объектов
  ordering = '-created'
  # Указываем имя шаблона, в котором будут все инструкции о том,
  # как именно пользователю должны быть показаны наши объекты
  template_name = 'search.html'
  # Это имя списка, в котором будут лежать все объекты.
  # Его надо указать, чтобы обратиться к списку объектов в html-шаблоне.
  context_object_name = 'posts'

  paginate_by = 10

  def get_queryset(self):
    queryset = super().get_queryset()
    self.filterset = PostFilter(self.request.GET, queryset)
    return self.filterset.qs
  
  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    # Добавляем в контекст объект фильтрации.
    context['filterset'] = self.filterset
    return context

class PostDetail(LoginRequiredMixin, DetailView):
  raise_exception = True
  model = Post
  template_name = 'post.html'
  context_object_name = 'post'

class CreatePost(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
  raise_exception = True
  permission_required = ('news.add_post')
  form_class = CreatePostForm
  model = Post
  template_name = 'create_post.html'

  def form_valid(self, form):
    post = form.save(commit=False)
    post.isnews = False
    return super().form_valid(form)

class CreateNews(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
  raise_exception = True
  permission_required = ('news.add_post')
  form_class = CreatePostForm
  model = Post
  template_name = 'create_news.html'

  def form_valid(self, form):
    post = form.save(commit=False)
    post.isnews = True
    return super().form_valid(form)

class UpdatePost(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
  permission_required = ('news.change_post')
  raise_exception = True
  form_class = CreatePostForm
  model = Post
  template_name = 'edit_post.html'

class DeletePost(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
  permission_required = ('news.delete_post')
  raise_exception = True
  model = Post
  template_name = 'delete_post.html'
  success_url = reverse_lazy('post_list')

@login_required
@csrf_protect
def subscriptions(request):
  if request.method == 'POST':
    category_id = request.POST.get('category_id')
    category = Category.objects.get(id=category_id)
    action = request.POST.get('action')

    if action == 'subscribe':
      Subscription.objects.create(user=request.user, category=category)
    elif action == 'unsubscribe':
      Subscription.objects.filter(
        user=request.user,
        category=category,
        ).delete()

  categories_with_subscriptions = Category.objects.annotate(
    user_subscribed=Exists(
      Subscription.objects.filter(
        user=request.user,
        category=OuterRef('pk')
      )
    )
  ).order_by('name')

  return render(
    request,
    'subscriptions.html',
    {'categories': categories_with_subscriptions}
  )
