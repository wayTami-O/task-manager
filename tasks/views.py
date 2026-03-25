from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from accounts.models import User

from .forms import TaskForm
from .mixins import AdminRequiredMixin
from .models import Task


class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    context_object_name = 'tasks'
    paginate_by = 10
    template_name = 'tasks/task_list.html'

    def get_queryset(self):
        qs = Task.objects.select_related('user')
        user = self.request.user
        if not user.is_admin:
            qs = qs.filter(user=user)

        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))

        status = self.request.GET.get('status')
        if status in (Task.Status.PENDING, Task.Status.DONE):
            qs = qs.filter(status=status)

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['search_q'] = self.request.GET.get('q', '')
        ctx['filter_status'] = self.request.GET.get('status', '')
        ctx['status_choices'] = Task.Status.choices
        return ctx


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'
    success_url = reverse_lazy('tasks:list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Задача создана.')
        return super().form_valid(form)


class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'
    success_url = reverse_lazy('tasks:list')

    def get_queryset(self):
        user = self.request.user
        qs = Task.objects.all()
        if not user.is_admin:
            qs = qs.filter(user=user)
        return qs

    def form_valid(self, form):
        messages.success(self.request, 'Задача сохранена.')
        return super().form_valid(form)


class TaskDeleteView(AdminRequiredMixin, DeleteView):
    model = Task
    template_name = 'tasks/task_confirm_delete.html'
    success_url = reverse_lazy('tasks:list')

    def form_valid(self, form):
        messages.success(self.request, 'Задача удалена.')
        return super().form_valid(form)


class TaskToggleDoneView(LoginRequiredMixin, View):
    http_method_names = ['post']

    def post(self, request, pk):
        user = request.user
        task = get_object_or_404(Task, pk=pk)
        if not user.is_admin and task.user_id != user.id:
            raise Http404()

        task.status = (
            Task.Status.PENDING
            if task.status == Task.Status.DONE
            else Task.Status.DONE
        )
        task.save(update_fields=['status'])
        messages.success(
            request,
            'Статус задачи обновлён.',
        )
        return redirect('tasks:list')


class UserManageListView(AdminRequiredMixin, ListView):
    model = User
    template_name = 'tasks/user_manage.html'
    context_object_name = 'users'
    paginate_by = 15


class UserToggleAdminView(AdminRequiredMixin, View):
    http_method_names = ['post']

    def post(self, request, pk):
        target = get_object_or_404(User, pk=pk)
        if target.pk == request.user.pk:
            messages.error(request, 'Нельзя снять с себя роль администратора.')
            return redirect('tasks:user_manage')

        if target.is_admin:
            target.role = User.Role.USER
            msg = f'Пользователь {target.email} больше не администратор.'
        else:
            target.role = User.Role.ADMIN
            msg = f'Пользователь {target.email} назначен администратором.'
        target.save(update_fields=['role'])
        messages.success(request, msg)
        return redirect('tasks:user_manage')
