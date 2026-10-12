import csv

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponse
from django.views.generic import DetailView
from django.shortcuts import redirect
from django.urls import reverse

from courses.management.commands.audit_ml_learning_content import collect_audit_report
from courses.models.audit import CourseAuditRun
from courses.models.course import Course


def compare_audit_reports(left_report, right_report):
    left_lessons = {item['lesson_id']: item for item in left_report.get('lessons', [])}
    right_lessons = {item['lesson_id']: item for item in right_report.get('lessons', [])}
    changes = []
    for lesson_id in sorted(set(left_lessons) | set(right_lessons)):
        left = left_lessons.get(lesson_id)
        right = right_lessons.get(lesson_id)
        if left is None or right is None:
            changes.append({
                'module': (right or left)['module'],
                'lesson': (right or left)['lesson'],
                'change': 'Добавлен или удалён урок',
                'added_issues': (right or {}).get('issues', []),
                'resolved_issues': [],
                'added_categories': (right or {}).get('issue_categories', []),
                'resolved_categories': [],
            })
            continue
        added_issues = sorted(set(right['issues']) - set(left['issues']))
        resolved_issues = sorted(set(left['issues']) - set(right['issues']))
        added_categories = sorted(
            set(right.get('issue_categories', [])) - set(left.get('issue_categories', []))
        )
        resolved_categories = sorted(
            set(left.get('issue_categories', [])) - set(right.get('issue_categories', []))
        )
        metrics_changed = (
            left['material'] != right['material']
            or left['quiz'] != right['quiz']
            or left.get('issue_categories') != right.get('issue_categories')
        )
        if metrics_changed or added_issues or resolved_issues:
            changes.append({
                'module': right['module'],
                'lesson': right['lesson'],
                'change': 'Изменены метрики или содержимое',
                'added_issues': added_issues,
                'resolved_issues': resolved_issues,
                'added_categories': added_categories,
                'resolved_categories': resolved_categories,
            })
    return {
        'changes': changes,
        'changed_lessons': len(changes),
                'added_issues': sum(len(item['added_issues']) for item in changes),
        'resolved_issues': sum(len(item['resolved_issues']) for item in changes),
    }


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

    def render_to_response(self, context, **response_kwargs):
        if self.request.GET.get('format') == 'csv':
            response = HttpResponse('\ufeff', content_type='text/csv; charset=utf-8')
            response['Content-Disposition'] = (
                f'attachment; filename="{self.object.slug}-audit.csv"'
            )
            writer = csv.writer(response)
            writer.writerow(('Модуль', 'Урок', 'Категории', 'Замечания'))
            for lesson in context['audit_report']['lessons']:
                writer.writerow((
                    lesson['module'],
                    lesson['lesson'],
                    ', '.join(lesson['issue_categories']),
                    ' | '.join(lesson['issues']),
                ))
            return response
        return super().render_to_response(context, **response_kwargs)


class CourseAuditRunView(CourseAuditView):
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        report = collect_audit_report(self.object)
        CourseAuditRun.objects.create(
            course=self.object,
            passed=not report['issues'],
            modules_count=report['summary']['modules'],
            lessons_count=report['summary']['lessons'],
            published_questions_count=report['summary']['published_questions'],
            issues_count=report['summary']['issues'],
            report=report,
        )
        return redirect(
            reverse('courses:course_audit_history', kwargs={'slug': self.object.slug})
        )


class CourseAuditHistoryView(CourseAuditView):
    template_name = 'courses/manage/course/audit_history.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['audit_runs'] = CourseAuditRun.objects.filter(
            course=self.object,
        )[:30]
        return context


class CourseAuditCompareView(CourseAuditView):
    template_name = 'courses/manage/course/audit_compare.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        runs = list(CourseAuditRun.objects.filter(course=self.object)[:30])
        left_id = self.request.GET.get('left')
        right_id = self.request.GET.get('right')
        left = CourseAuditRun.objects.filter(course=self.object, id=left_id).first() if left_id else None
        right = CourseAuditRun.objects.filter(course=self.object, id=right_id).first() if right_id else None
        if left is None or right is None:
            right, left = (runs + [None, None])[:2]
        context.update({
            'audit_runs': runs,
            'left_run': left,
            'right_run': right,
            'audit_comparison': (
                compare_audit_reports(left.report, right.report)
                if left and right else None
            ),
        })
        return context
