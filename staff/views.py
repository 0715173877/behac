# staff/views.py
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Teacher
from .forms import TeacherForm
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Teacher, SalaryPayment
from .forms import SalaryPaymentForm
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render

def add_salary_payment(request, teacher_id):
    teacher = get_object_or_404(Teacher, pk=teacher_id)
    ct = ContentType.objects.get_for_model(Teacher)

    if request.method == 'POST':
        form = SalaryPaymentForm(request.POST)
        if form.is_valid():
            month = form.cleaned_data['month']
            amount = form.cleaned_data['amount']
            notes = form.cleaned_data['notes']
            update_base = form.cleaned_data.get('update_base_salary', False)

            # Try to get existing payment for this teacher and month
            payment, created = SalaryPayment.objects.get_or_create(
                content_type=ct,
                object_id=teacher.id,
                month=month,
                defaults={'amount': amount, 'notes': notes}
            )
            if not created:
                # Update existing payment
                payment.amount = amount
                payment.notes = notes
                payment.save()
                messages.success(request, f"Updated salary payment for {teacher.user.get_full_name()} ({month.strftime('%B %Y')})")
            else:
                messages.success(request, f"Added salary payment for {teacher.user.get_full_name()} ({month.strftime('%B %Y')})")

            if update_base:
                teacher.base_salary = amount
                teacher.save()
                messages.success(request, f"Base salary updated to {amount}")

            return redirect('staff:teacher_detail', pk=teacher.id)
    else:
        # Pre-fill with last payment amount or base salary
        last_payment = SalaryPayment.objects.filter(content_type=ct, object_id=teacher.id).order_by('-month').first()
        initial = {'amount': last_payment.amount if last_payment else teacher.base_salary}
        form = SalaryPaymentForm(initial=initial)

    return render(request, 'staff/salary_payment_form.html', {'form': form, 'teacher': teacher})

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.groups.filter(name__in=['Admin', 'Owner']).exists()

class TeacherListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = Teacher
    template_name = 'staff/teacher_list.html'
    context_object_name = 'teachers'

class TeacherCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Teacher
    form_class = TeacherForm
    template_name = 'staff/teacher_form.html'
    success_url = reverse_lazy('staff:teacher_list')

class TeacherUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = Teacher
    form_class = TeacherForm
    template_name = 'staff/teacher_form.html'
    success_url = reverse_lazy('staff:teacher_list')

class TeacherDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = Teacher
    template_name = 'staff/teacher_confirm_delete.html'
    success_url = reverse_lazy('staff:teacher_list')


class TeacherDetailView(DetailView):
    model = Teacher
    template_name = 'staff/teacher_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['salary_payments'] = SalaryPayment.objects.filter(
            content_type=ContentType.objects.get_for_model(Teacher),
            object_id=self.object.id
        )
        return context
# =========== USER MANAGEMENT ===========

from django.contrib.auth.models import User, Group

def admin_check(user):
    return user.is_superuser or user.groups.filter(name__in=['Admin', 'Owner']).exists()

class UserListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = User
    template_name = 'staff/user_list.html'
    context_object_name = 'users'
    paginate_by = 50

    def test_func(self):
        return admin_check(self.request.user)

    def get_queryset(self):
        qs = super().get_queryset().select_related('teacher_profile')
        q = self.request.GET.get('q', '')
        group = self.request.GET.get('group', '')
        if q:
            qs = qs.filter(username__icontains=q) | qs.filter(first_name__icontains=q) | qs.filter(last_name__icontains=q) | qs.filter(email__icontains=q)
        if group:
            qs = qs.filter(groups__name=group)
        return qs.distinct()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['groups'] = Group.objects.all()
        ctx['q'] = self.request.GET.get('q', '')
        ctx['selected_group'] = self.request.GET.get('group', '')
        return ctx


def reset_user_password(request, pk):
    """Reset a user's password to a random one"""
    if not admin_check(request.user):
        messages.error(request, "Access denied.")
        return redirect('staff:user_list')
    
    user = get_object_or_404(User, pk=pk)
    import secrets, string
    alphabet = string.ascii_letters + string.digits
    new_password = ''.join(secrets.choice(alphabet) for _ in range(10))
    user.set_password(new_password)
    user.save()
    
    messages.success(request, f"Password for {user.username} reset to: {new_password}")
    return redirect('staff:user_list')


def toggle_user_active(request, pk):
    """Activate/Deactivate a user"""
    if not admin_check(request.user):
        messages.error(request, "Access denied.")
        return redirect('staff:user_list')
    
    user = get_object_or_404(User, pk=pk)
    user.is_active = not user.is_active
    user.save()
    status = "activated" if user.is_active else "deactivated"
    messages.success(request, f"User {user.username} {status}.")
    return redirect('staff:user_list')


def create_user(request):
    """Create a new user and assign to groups"""
    if not admin_check(request.user):
        messages.error(request, "Access denied.")
        return redirect('staff:user_list')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        group_ids = request.POST.getlist('groups')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, f"Username '{username}' already exists.")
            return redirect('staff:create_user')
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password or 'changeme123',
            first_name=first_name,
            last_name=last_name
        )
        
        for gid in group_ids:
            try:
                group = Group.objects.get(pk=gid)
                user.groups.add(group)
            except Group.DoesNotExist:
                pass
        
        messages.success(request, f"User {username} created successfully! Password: {password or 'changeme123'}")
        return redirect('staff:user_list')
    
    groups = Group.objects.all()
    return render(request, 'staff/create_user.html', {'groups': groups})


def change_user_groups(request, pk):
    """Change groups for a user"""
    if not admin_check(request.user):
        messages.error(request, "Access denied.")
        return redirect('staff:user_list')
    
    user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        group_ids = request.POST.getlist('groups')
        user.groups.clear()
        for gid in group_ids:
            try:
                group = Group.objects.get(pk=gid)
                user.groups.add(group)
            except Group.DoesNotExist:
                pass
        messages.success(request, f"Groups updated for {user.username}.")
        return redirect('staff:user_list')
    
    groups = Group.objects.all()
    user_group_ids = user.groups.values_list('pk', flat=True)
    return render(request, 'staff/user_groups.html', {
        'target_user': user,
        'groups': groups,
        'user_group_ids': list(user_group_ids)
    })
