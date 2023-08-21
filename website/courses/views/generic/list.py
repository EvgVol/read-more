from django.views.generic.base import TemplateResponseMixin, View
from django.views.generic.list import ListView
from django.shortcuts import get_object_or_404
from braces.views import CsrfExemptMixin, JsonRequestResponseMixin
from django.db.models import Count

from courses.models.subject import Subject
from courses.models.course import Course
from courses.models.module import Module
from courses.models.content import Content
from courses.models.lessons import Lesson
from courses.views.mixins import OwnerCourseMixin


class SubjectView(ListView):
    model = Subject
    template_name = 'courses/subject_list.html'


class CourseListView(OwnerCourseMixin, ListView):
    """A view for displaying a list of courses."""

    template_name = 'courses/manage/course/list.html'
    permission_required = 'courses.view_course'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        subject_name = self.kwargs.get('subject_name', None)
        complexity_name = self.kwargs.get('complexity_name', None)
        subjects = Subject.objects.annotate(total_courses=Count('courses'))
        all_course = Course.objects.all()
        courses = Course.objects.all()

        if subject_name:
            subject_id = get_object_or_404(Subject, slug=subject_name)
            courses = courses.filter(subject=subject_id)
            context['subject_id'] = subject_id

        if complexity_name:
            courses = Course.objects.filter(complexity=complexity_name)
            complexity = all_course.first().Complexity(complexity_name).label
            context['complexity_full_name'] = complexity
            

        context['complexity_name'] = complexity_name
        
        context['all_course'] = all_course
        context['courses'] = courses
        context['subjects'] = subjects
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
