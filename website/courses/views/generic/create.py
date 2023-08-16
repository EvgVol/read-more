from django.forms.models import modelform_factory
from django.apps import apps
from django.views.generic.base import TemplateResponseMixin, View
from django.views.generic.edit import CreateView
from courses.views.mixins import OwnerCourseEditMixin
from django.shortcuts import redirect, get_object_or_404

from courses.models.module import Module, Content


class CourseCreateView(OwnerCourseEditMixin, CreateView):
    """A view for creating a new course."""

    permission_required = 'courses.add_course'


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
        self.module = get_object_or_404(Module,
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
                Content.objects.create(module=self.module, item=obj)
                return redirect('courses:content_list', self.module.id)
            return self.render_to_response({'form': form, 'object': self.obj})
