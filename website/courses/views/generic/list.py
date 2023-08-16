from django.views.generic.base import TemplateResponseMixin, View
from django.views.generic.list import ListView
from django.shortcuts import get_object_or_404

from courses.models.subject import Subject
from courses.models.course import Course
from courses.models.module import Module
from courses.models.lessons import Lesson
from courses.views.mixins import OwnerCourseMixin


class SubjectView(ListView):
    model = Subject
    template_name = 'courses/subject_list.html'


class CourseListView(OwnerCourseMixin, ListView):
    """A view for displaying a list of courses."""

    template_name = 'courses/manage/course/list.html'
    permission_required = 'courses.view_course'
    
    def get_queryset(self):
        subject_name = self.kwargs['subject_name']
        return super().get_queryset().filter(subject__slug=subject_name)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        subject_name = self.kwargs['subject_name']
        subject_id = get_object_or_404(Subject, slug=subject_name)
        

        all_courses = Course.objects.filter(subject=subject_id)
        junior_courses = Course.objects.filter(
            subject=subject_id, complexity=Course.Complexity.JUNIOR
        )
        middle_courses = Course.objects.filter(
            subject=subject_id, complexity=Course.Complexity.MIDDLE
        )
        senior_courses = Course.objects.filter(
            subject=subject_id, complexity=Course.Complexity.SENIOR
        )

        total_count = all_courses.count()
        junior_count = junior_courses.count()
        middle_count = middle_courses.count()
        senior_count = senior_courses.count()

        # Calculate percentages
        if total_count > 0:
            percent_junior = (junior_count / total_count) * 100
            percent_middle = (middle_count / total_count) * 100
            percent_senior = (senior_count / total_count) * 100
        else:
            percent_junior = 0
            percent_middle = 0
            percent_senior = 0

        context['subject_id'] = subject_id
        context['all_courses'] = all_courses
        context['junior_courses'] = junior_courses
        context['middle_courses'] = middle_courses
        context['senior_courses'] = senior_courses
        context['percent_junior'] = percent_junior
        context['percent_middle'] = percent_middle
        context['percent_senior'] = percent_senior
        return context


class ModuleListView(ListView):
    model = Module
    template_name = 'courses/manage/module/module_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course_id = self.kwargs.get('pk')
        course = get_object_or_404(Course, id=course_id)
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
