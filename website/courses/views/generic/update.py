from django.views.generic.base import TemplateResponseMixin, View
from django.views.generic.edit import UpdateView
from django.shortcuts import redirect, get_object_or_404

from courses.views.mixins import OwnerCourseEditMixin
from courses.views.forms import ModuleFormSet
from courses.models.course import Course


class CourseUpdateView(OwnerCourseEditMixin, UpdateView):
    """A view for updating an existing course."""

    permission_required = 'courses.change_course'


class ModuleUpdateView(TemplateResponseMixin, View):
    """A view for updating a module the course."""

    template_name = 'courses/manage/module/formset.html'
    course = None

    # возвращает форму дочерних модулей курса
    def get_formset(self, data=None):
        return ModuleFormSet(instance=self.course,
                             data=data)

    # получает объект курса для редактирования модулей
    def dispatch(self, request, pk):
        self.course = get_object_or_404(Course,
                                        id=pk,
                                        owner=request.user)
        return super().dispatch(request, pk)

    # отображает форму для редактирования курса и всех его дочерних модулей
    def get(self, request, *args, **kwargs):
        formset = self.get_formset()
        return self.render_to_response({'course': self.course,
                                        'formset': formset})

    # обрабатывает POST запрос и сохраняет изменения, если форма действительна
    def post(self, request, *args, **kwargs):
        formset = self.get_formset(data=request.POST)
        if formset.is_valid():
            formset.save()
            return redirect('courses:manage_course_list', self.course.subject.slug)
        else:
            return self.render_to_response({'course': self.course,
                                            'formset': formset})
