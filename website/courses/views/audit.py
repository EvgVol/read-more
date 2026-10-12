from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.views.generic import DetailView

from courses.management.commands.audit_ml_learning_content import collect_audit_report
from courses.models.course import Course


class CourseAuditView(LoginRequiredMixin, DetailView):
    model = Course
    template_name = 'courses/manage/course/audit.html'
    context_object_name = 'course'

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(Q(owner=self.request.user)).distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        report = collect_audit_report(self.object)
        filter_mode = self.request.GET.get('filter', 'all')
        if filter_mode not in {'all', 'issues'}:
            filter_mode = 'all'
        if filter_mode == 'issues':
            report['lessons'] = [lesson for lesson in report['lessons'] if lesson['issues']]
        context['audit_report'] = report
        context['audit_filter'] = filter_mode
        return context
