from django.shortcuts import redirect, get_object_or_404, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import AcademicYear, Term
from .forms import AcademicYearForm, TermForm

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.groups.filter(name__in=['Admin', 'Owner']).exists()

# Academic Year CRUD
class AcademicYearListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = AcademicYear
    template_name = "core/academic_year_list.html"
    context_object_name = "years"
    ordering = ["-start_date"]

class AcademicYearCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = AcademicYear
    form_class = AcademicYearForm
    template_name = "core/academic_year_form.html"
    success_url = reverse_lazy("core:academic_year_list")
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = "Add Academic Year"
        return ctx

class AcademicYearUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = AcademicYear
    form_class = AcademicYearForm
    template_name = "core/academic_year_form.html"
    success_url = reverse_lazy("core:academic_year_list")
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = "Edit Academic Year"
        return ctx

# Term CRUD
class TermListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = Term
    template_name = "core/term_list.html"
    context_object_name = "terms"
    ordering = ["-academic_year__start_date", "name"]
    
    def get_queryset(self):
        qs = super().get_queryset().select_related('academic_year')
        show_all = self.request.GET.get('all', '')
        if not (show_all == '1' and (self.request.user.is_superuser or 'Admin' in self.request.user.groups.all().values_list('name', flat=True))):
            current_year = AcademicYear.objects.filter(is_current=True).first()
            if current_year:
                qs = qs.filter(academic_year=current_year)
        return qs
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['current_year'] = AcademicYear.objects.filter(is_current=True).first()
        return ctx

class TermCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Term
    form_class = TermForm
    template_name = "core/term_form.html"
    success_url = reverse_lazy("core:term_list")
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = "Add Term"
        return ctx

class TermUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = Term
    form_class = TermForm
    template_name = "core/term_form.html"
    success_url = reverse_lazy("core:term_list")
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = "Edit Term"
        return ctx

class TermDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = Term
    template_name = "core/term_confirm_delete.html"
    success_url = reverse_lazy("core:term_list")


class AcademicYearDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = AcademicYear
    template_name = "core/academic_year_confirm_delete.html"
    success_url = reverse_lazy("core:academic_year_list")

@login_required
def activate_academic_year(request, pk):
    if not (request.user.is_superuser or request.user.groups.filter(name__in=['Admin', 'Owner']).exists()):
        messages.error(request, "Only admins can change academic year.")
        return redirect(request.META.get("HTTP_REFERER", "/"))
    
    year = get_object_or_404(AcademicYear, pk=pk)
    year.is_current = True
    year.save()
    messages.success(request, f"Academic year {year.name} is now active.")
    return redirect("core:academic_year_list")
