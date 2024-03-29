from django.views.generic import DetailView
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.mixins import LoginRequiredMixin

from courses.forms import CourseEnrollForm
from courses.models.course import Course
from reviews.models import Review
from blog.models import Post


class CourseDetailView(LoginRequiredMixin, DetailView):
    """A view a detail course."""

    model = Course
    template_name = 'courses/manage/course/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course_content_type = ContentType.objects.get_for_model(Course)
        reviews = Review.objects.filter(content_type=course_content_type,
                                        object_id=self.object.pk)
        posts = Post.objects.all()[:4]
        context['enroll_form'] = CourseEnrollForm(initial={'course':self.object})
        context['reviews'] = reviews
        context['posts'] = posts
        return context


class CourseTrainerView(LoginRequiredMixin, DetailView):
    model = Course
    template_name = 'courses/manage/course/trainer.html'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(students__in=[self.request.user])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.get_object()
        
        
        if 'module_id' in self.kwargs:
            context['module'] = course.modules.get(id=self.kwargs['module_id'])
        else:
        # взять первый модуль
            context['module'] = course.modules.all()[0]
        return context
