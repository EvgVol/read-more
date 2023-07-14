from django.apps import apps
from django.forms.models import modelform_factory
from django.contrib.auth.mixins import (LoginRequiredMixin,
                                        PermissionRequiredMixin)
from django.views.generic import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.shortcuts import redirect, get_object_or_404
from django.views.generic.base import TemplateResponseMixin, View
from .forms import ModuleFormSet
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType

from courses.models import subject, course, module, content
from reviews.models import Review


class SubjectView(ListView):
    model = subject.Subject
    template_name = 'courses/subject_list.html'


class OwnerMixin:
    """
    A mixin that limits queryset to those created by the requesting user.
    """
    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user)


class OwnerEditMixin:
    """
    A mixin that sets the requesting user as the owner of the object 
    being created or updated.
    """
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class OwnerCourseMixin(OwnerMixin,
                       LoginRequiredMixin,
                       PermissionRequiredMixin):
    """A mixin for views that deal with Course instances."""

    model = course.Course
    fields = ['subject', 'title', 'overview']

    def get_success_url(self):
        subject_name = self.object.subject.slug
        return reverse('courses:manage_course_list',
                       kwargs={'subject_name': subject_name})


class OwnerCourseEditMixin(OwnerCourseMixin, OwnerEditMixin):
    """A mixin for views that edit Course instances."""

    template_name = 'courses/manage/course/form.html'

    def form_valid(self, form):
        super().form_valid(form)
        return redirect(self.get_success_url())

    
class ManageCourseListView(OwnerCourseMixin, ListView):
    """A view for displaying a list of courses."""

    template_name = 'courses/manage/course/list.html'
    permission_required = 'courses.view_course'
    
    def get_queryset(self):
        subject_name = self.kwargs['subject_name']
        return super().get_queryset().filter(subject__slug=subject_name)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        subject_name = self.kwargs['subject_name']
        subject_id = get_object_or_404(subject.Subject, slug=subject_name)
        

        all_courses = course.Course.objects.filter(subject=subject_id)
        junior_courses = course.Course.objects.filter(subject=subject_id, complexity=course.Course.Complexity.JUNIOR)
        middle_courses = course.Course.objects.filter(subject=subject_id, complexity=course.Course.Complexity.MIDDLE)
        senior_courses = course.Course.objects.filter(subject=subject_id, complexity=course.Course.Complexity.SENIOR)

        total_count = all_courses.count()
        junior_count = junior_courses.count()
        middle_count = middle_courses.count()
        senior_count = senior_courses.count()

        # Calculate percentages
        percent_junior = (junior_count / total_count) * 100
        percent_middle = (middle_count / total_count) * 100
        percent_senior = (senior_count / total_count) * 100

        context['all_courses'] = all_courses
        context['junior_courses'] = junior_courses
        context['middle_courses'] = middle_courses
        context['senior_courses'] = senior_courses
        context['percent_junior'] = percent_junior
        context['percent_middle'] = percent_middle
        context['percent_senior'] = percent_senior
        return context


class CourseCreateView(OwnerCourseEditMixin, CreateView):
    """A view for creating a new course."""

    permission_required = 'courses.add_course'


class CourseUpdateView(OwnerCourseEditMixin, UpdateView):
    """A view for updating an existing course."""

    permission_required = 'courses.change_course'


class CourseDeleteView(OwnerCourseMixin, DeleteView):
    """A view for deleting an existing course."""

    template_name = 'courses/manage/course/delete.html'
    permission_required = 'courses.delete_course'


class CourseDetailView(DetailView):
    """A view a detail course."""

    model = course.Course
    template_name = 'courses/manage/course/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course_content_type = ContentType.objects.get_for_model(course.Course)
        reviews = Review.objects.filter(content_type=course_content_type,
                                        object_id=self.object.pk)
        context['reviews'] = reviews
        return context


class CourseModuleUpdateView(TemplateResponseMixin, View):
    """A view for updating a module the course."""

    template_name = 'courses/manage/module/formset.html'
    course = None

    # возвращает форму дочерних модулей курса
    def get_formset(self, data=None):
        return ModuleFormSet(instance=self.course,
                             data=data)

    # получает объект курса для редактирования модулей
    def dispatch(self, request, pk):
        self.course = get_object_or_404(course.Course,
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
            return redirect('courses:manage_course_list')
        else:
            return self.render_to_response({'course': self.course,
                                            'formset': formset})


class ContentCreateUpdateView(TemplateResponseMixin, View):
    module = None
    model = None
    obj = None
    template_name = 'courses/manage/content/form.html'

    # получение модели контента по имени
    def get_model(self, model_name):
        if model_name in ['text', 'video', 'image', 'file']:
            return apps.get_model(app_label='courses',
                                  model_name=model_name)
        return None

    # создание формы на основе модели контента
    def get_form(self, model, *args, **kwargs):
        Form = modelform_factory(model, exclude=['owner',
                                                 'order',
                                                 'created',
                                                 'updated'])
        return Form(*args, **kwargs)

    # обработка GET и POST запросов
    def dispatch(self, request, module_id, model_name, id=None):
        # получаем объект модуля
        self.module = get_object_or_404(module.Module,
                                        id=module_id,
                                        course__owner=request.user)
        # получаем модель контента
        self.model = self.get_model(model_name)
        # если передан id:
        if id:
            # получаем объект контента, который нужно обновить
            self.obj = get_object_or_404(self.model,
                                         id=id,
                                         owner=request.user)
        # вызываем метод dispatch родительского класса и передаем аргументы
        return super().dispatch(request, module_id, model_name, id)

    def get(self, request, module_id, model_name, id=None):
        form = self.get_form(self.model, instance=self.obj)
        return self.render_to_response({'form': form, 'object': self.obj})

    def post(self, request, module_id, model_name, id=None):
        form = self.get_form(self.model,
                             instance=self.obj,
                             data=request.POST,
                             files=request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            obj.save()
            if not id:
                # new content
                content.Content.objects.create(module=self.module, item=obj)
                return redirect('courses:content_list', self.module.id)
            return self.render_to_response({'form': form, 'object': self.obj})


class ContentDeleteView(View):
    def post(self, request, id):
        content_id = get_object_or_404(content.Content,
                                       id=id,
                                       module__course__owner=request.user)
        module = content_id.module
        content_id.item.delete()
        content_id.delete()
        return redirect('courses:content_list', module.id)


class ModuleContentListView(TemplateResponseMixin, View):
    template_name = 'courses/manage/module/content_list.html'

    def get(self, request, id):
        module_id = get_object_or_404(module.Module,
                                      id=id,
                                      course__owner=request.user)
        return self.render_to_response({'module': module_id})
