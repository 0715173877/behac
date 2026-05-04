from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from .models import BehaviorRecord, Achievement
from core.models import AcademicYear
from .forms import BehaviorRecordForm, AchievementForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

class BehaviorRecordListView(LoginRequiredMixin, ListView):
    model = BehaviorRecord
    template_name = 'behavior/behavior_list.html'
    context_object_name = 'records'

    def get_queryset(self):
        qs = super().get_queryset()
        
        # If teacher, filter by their assigned students
        if hasattr(self.request.user, 'teacher_profile'):
            teacher = self.request.user.teacher_profile
            assigned_classes = teacher.classes.all()
            if assigned_classes.exists():
                qs = qs.filter(student__current_class__in=assigned_classes)
        
        # Academic year filter
        show_all = self.request.GET.get('all', '')
        if not (show_all == '1' and (self.request.user.is_superuser or 'Admin' in self.request.user.groups.all().values_list('name', flat=True))):
            current_year = AcademicYear.objects.filter(is_current=True).first()
            if current_year:
                qs = qs.filter(date__gte=current_year.start_date, date__lte=current_year.end_date)
        
        q = self.request.GET.get('q', '')
        btype = self.request.GET.get('type', '')
        resolved = self.request.GET.get('resolved', '')
        if q:
            qs = qs.filter(student__first_name__icontains=q) | qs.filter(student__last_name__icontains=q) | qs.filter(description__icontains=q)
        if btype:
            qs = qs.filter(behavior_type=btype)
        if resolved:
            qs = qs.filter(resolved=(resolved == 'yes'))
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['q'] = self.request.GET.get('q', '')
        ctx['selected_type'] = self.request.GET.get('type', '')
        ctx['selected_resolved'] = self.request.GET.get('resolved', '')
        return ctx

class BehaviorRecordCreateView(LoginRequiredMixin, CreateView):
    model = BehaviorRecord
    form_class = BehaviorRecordForm
    template_name = 'behavior/behavior_form.html'
    success_url = reverse_lazy('behavior:behavior_list')

class BehaviorRecordUpdateView(LoginRequiredMixin, UpdateView):
    model = BehaviorRecord
    form_class = BehaviorRecordForm
    template_name = 'behavior/behavior_form.html'
    success_url = reverse_lazy('behavior:behavior_list')

class BehaviorRecordDeleteView(LoginRequiredMixin, DeleteView):
    model = BehaviorRecord
    template_name = 'behavior/behavior_confirm_delete.html'
    success_url = reverse_lazy('behavior:behavior_list')
    context_object_name = 'record'

class BehaviorRecordDetailView(LoginRequiredMixin, DetailView):
    model = BehaviorRecord
    template_name = 'behavior/behavior_detail.html'
    context_object_name = 'record'

class AchievementListView(LoginRequiredMixin, ListView):
    model = Achievement
    template_name = 'behavior/achievement_list.html'
    context_object_name = 'achievements'

    def get_queryset(self):
        qs = super().get_queryset()
        
        # If teacher, filter by their assigned students
        if hasattr(self.request.user, 'teacher_profile'):
            teacher = self.request.user.teacher_profile
            assigned_classes = teacher.classes.all()
            if assigned_classes.exists():
                qs = qs.filter(student__current_class__in=assigned_classes)
        
        # Academic year filter
        show_all = self.request.GET.get('all', '')
        if not (show_all == '1' and (self.request.user.is_superuser or 'Admin' in self.request.user.groups.all().values_list('name', flat=True))):
            current_year = AcademicYear.objects.filter(is_current=True).first()
            if current_year:
                qs = qs.filter(date_awarded__gte=current_year.start_date, date_awarded__lte=current_year.end_date)
        
        q = self.request.GET.get('q', '')
        if q:
            qs = qs.filter(student__first_name__icontains=q) | qs.filter(student__last_name__icontains=q) | qs.filter(title__icontains=q)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['q'] = self.request.GET.get('q', '')
        return ctx

class AchievementCreateView(LoginRequiredMixin, CreateView):
    model = Achievement
    form_class = AchievementForm
    template_name = 'behavior/achievement_form.html'
    success_url = reverse_lazy('behavior:achievement_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

class AchievementUpdateView(LoginRequiredMixin, UpdateView):
    model = Achievement
    form_class = AchievementForm
    template_name = 'behavior/achievement_form.html'
    success_url = reverse_lazy('behavior:achievement_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

class AchievementDeleteView(LoginRequiredMixin, DeleteView):
    model = Achievement
    template_name = 'behavior/achievement_confirm_delete.html'
    success_url = reverse_lazy('behavior:achievement_list')
    context_object_name = 'achievement'

class AchievementDetailView(LoginRequiredMixin, DetailView):
    model = Achievement
    template_name = 'behavior/achievement_detail.html'
    context_object_name = 'achievement'
