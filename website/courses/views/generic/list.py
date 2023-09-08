from django.views.generic.base import TemplateResponseMixin, View
from django.views.generic.list import ListView
from django.shortcuts import get_object_or_404
from braces.views import CsrfExemptMixin, JsonRequestResponseMixin
from django.db.models import Count
from django.core.cache import cache
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from core.forms import QuestionForm
from core.email import send_email_message
from courses.models.subject import Subject
from courses.models.course import Course
from courses.models.module import Module
from courses.models.content import Content
from courses.models.lessons import Lesson
from courses.views.mixins import OwnerCourseMixin


class SubjectView(ListView):
    model = Subject
    template_name = 'courses/subject_list.html'

    def dispatch(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = QuestionForm()
        context['success'] = kwargs.get('success', False)
        return context

    def post(self, request, *args, **kwargs):
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save()
            send_email_message(question)
            messages.success(request,
                             _('Your question has been sent'))
            return self.render_to_response(
                self.get_context_data(form=QuestionForm(), success=True)
            )

        return self.render_to_response(self.get_context_data(form=form))


class CourseListView(ListView):
    """A view for displaying a list of courses."""

    template_name = 'courses/manage/course/list.html'
    permission_required = 'courses.view_course'

    def get_filters_from_request(self):
        subject_name = self.request.GET.get('subject_name')
        complexity_name = self.request.GET.get('complexity_name')
        return subject_name, complexity_name

    def apply_filter(self, subject_name, complexity_name):
        queryset_filters = {}

        if subject_name:
            subject_id = get_object_or_404(Subject, slug=subject_name)
            queryset_filters['subject'] = subject_id

        if complexity_name:
            queryset_filters['complexity'] = complexity_name

        return queryset_filters

    def get_queryset(self):
        subject_name, complexity_name = self.get_filters_from_request()

        queryset_filters = self.apply_filter(subject_name, complexity_name)

        cache_key = f'courses_subject_{subject_name}_complexity_{complexity_name}'
        queryset = cache.get(cache_key)

        if queryset is None:
            queryset = Course.objects.filter(**queryset_filters)
            cache.set(cache_key, queryset, 300)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        subject_name, complexity_name = self.get_filters_from_request()
        
        subjects = Subject.objects.annotate(
            total_courses=Count('courses')
        ).prefetch_related('courses')
        cache.set('all_subjects', subjects)
        all_course = Course.objects.all().select_related('subject').prefetch_related('modules')

        context['subjects'] = subjects
        context['all_course'] = all_course

        cache_key = f'courses_subject_{subject_name}_complexity_{complexity_name}'
        courses = cache.get(cache_key)

        queryset_filters = {}

        if courses is None:
            queryset_filters = self.apply_filter(subject_name, complexity_name)
            courses = Course.objects.filter(**queryset_filters)
            cache.set(cache_key, courses, 300)
        
        context['courses'] = courses

        if subject_name and 'subject' in queryset_filters:
            subject_id = queryset_filters['subject']
            context['subject_id'] = subject_id

        if complexity_name:
            complexity = all_course.first().Complexity(complexity_name).label
            context['complexity_full_name'] = complexity
            context['complexity_name'] = complexity_name
        return context


class ModuleListView(ListView):
    model = Module
    template_name = 'courses/manage/module/module_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course_id = self.kwargs.get('pk')
        subject_name = self.kwargs.get('subject_name', None)
        course = get_object_or_404(Course, id=course_id, subject=subject_name)
        context["course_title"] = course.title
        context["subject"] = course.subject
        context['modules_lessons'] = []
        for module in context["object_list"]:
            lessons = Lesson.objects.filter(module=module).order_by('order')
            lesson_count = lessons.count()
            context['modules_lessons'].append({'module': module,
                                               'lessons': lessons,
                                               'lesson_count': lesson_count})
        return context
    

class ContentListView(TemplateResponseMixin, View):
    template_name = 'courses/manage/course/manager_courses.html'

    def get(self, request, module_id):
        module = get_object_or_404(Module,
                                   id=module_id,
                                   course__owner=request.user)
        return self.render_to_response({'module': module})


class ModuleOrderView(CsrfExemptMixin, JsonRequestResponseMixin, View):
    def post(self, request):
        for id, order in self.request_json.items():
            Module.objects.filter(
                id=id,
                course__owner=request.user
            ).update(order=order)
        return self.render_json_response({'saved': 'OK'})


class ContentOrderView(CsrfExemptMixin, JsonRequestResponseMixin, View):
    def post(self, request):
        for id, order in self.request_json.items():
            Content.objects.filter(
                id=id,
                module__course__owner=request.user
            ).update(order=order)
        return self.render_json_response({'saved': 'OK'})
