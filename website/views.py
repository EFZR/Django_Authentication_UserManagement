from django import template
from django.db.models import Count
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.views.generic.edit import FormView, CreateView, DeleteView
from django.views.generic.list import ListView
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import Group, User
from django.contrib.auth.mixins import PermissionRequiredMixin, UserPassesTestMixin, LoginRequiredMixin
from website.forms import RegisterForm, PostForm
from website.models import Post
from Logging.logger_base import log

# Create your views here.

class HomeView(UserPassesTestMixin, TemplateView):
    template_name = 'website/home.html'
    group_required = ['default', 'mod']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posts'] = Post.objects.all()
        context['check'] = self.request.user.groups.filter(name='mod').exists()
        return context

    def test_func(self):
        return self.request.user.groups.filter(name__in=self.group_required).exists()


class RegisterView(FormView):
    template_name = 'registration/register.html'
    form_class = RegisterForm
    success_url = reverse_lazy('home')
    redirect_authenticated_user = True

    def form_valid(self, form):
        user = form.save()
        group = Group.objects.get(name='default')
        user.groups.add(group)
        if user is not None:
            login(self.request, user)
            log.info(f'New user {user.username} registered')
            messages.success(self.request, 'Registration successful')
        return super().form_valid(form)

    def get(self, request, *args: str, **kwargs):
        if self.redirect_authenticated_user and request.user.is_authenticated:
            return redirect(self.success_url)
        return super().get(request, *args, **kwargs)


class PostView(PermissionRequiredMixin, CreateView):
    template_name = 'website/post.html'
    form_class = PostForm
    context_object_name = 'post'
    permission_required = 'website.add_post'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, 'Post created successfully')
        log.info(f'New post created by {self.request.user.username}')
        return super().form_valid(form)


class DeletePostView(PermissionRequiredMixin, DeleteView):
    model = Post
    template_name = 'website/delete_post.html'
    permission_required = 'website.delete_post'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        messages.success(self.request, 'Post deleted successfully')
        log.info(f'Post deleted by {self.request.user.username}')
        return super().form_valid(form)


class BanUserView(UserPassesTestMixin, TemplateView):
    template_name = 'website/ban.html'

    def test_func(self):
        return self.request.user.groups.filter(name='mod').exists()

    def get(self, request, *args: str, **kwargs):
        if self.test_func():
            return super().get(request, *args, **kwargs)
        return redirect('home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_to_ban'] = User.objects.get(pk=self.kwargs['pk'])
        return context

    def post(self, request, *args: str, **kwargs):
        user = User.objects.get(pk=self.kwargs['pk'])
        try:
            group = Group.objects.get(name='default')
            group.user_set.remove(user)
        except:
            pass

        try:
            group = Group.objects.get(name='mod')
            group.user_set.remove(user)
        except:
            pass

        messages.success(self.request, 'User banned successfully')
        log.info(
            f'User {user.username} banned by {self.request.user.username}')
        return redirect('home')


class UnbanUserView(UserPassesTestMixin, TemplateView):
    template_name = 'website/unban.html'

    def test_func(self):
        return self.request.user.groups.filter(name='mod').exists()

    def get(self, request, *args: str, **kwargs):
        if self.test_func():
            return super().get(request, *args, **kwargs)
        return redirect('home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_to_unban'] = User.objects.get(pk=self.kwargs['pk'])
        return context

    def post(self, request, *args: str, **kwargs):
        user = User.objects.get(pk=self.kwargs['pk'])
        group = Group.objects.get(name='default')
        user.groups.add(group)

        messages.success(self.request, 'User unbanned successfully')
        log.info(
            f'User {user.username} unbanned by {self.request.user.username}')
        return redirect('home')


class UsersView(UserPassesTestMixin, ListView):
    template_name = 'website/users.html'
    model = User

    def test_func(self):
        return self.request.user.groups.filter(name='mod').exists()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users_list'] = User.objects.select_related(
            'groups').values('username', 'groups__name', 'id')
        return context


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'website/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        posts_per_user = Post.objects.select_related('author').values(
            'author__username').annotate(posts=Count('author__username'))
        user_group = User.objects.select_related('groups').values(
            'groups__name', 'groups__id').annotate(users=Count('groups__id'))
        context['posts'] = Post.objects.count()
        context['users'] = User.objects.count()

        context['labelPosts'] = []
        context['dataPosts'] = []
        for post in posts_per_user:
            context['labelPosts'].append(post['author__username'])
            context['dataPosts'].append(post['posts'])
            
        context['labelGroups'] = []
        context['dataGroups'] = []
        for group in user_group:
            context['labelGroups'].append(group['groups__name'])
            context['dataGroups'].append(group['users'])

        return context
