from django.views.generic import DetailView
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import redirect_to_login
from django.db.models import Q
from django.shortcuts import get_object_or_404

from courses.forms import CourseEnrollForm
from courses.models.course import Course
from courses.models.lessons import Lesson
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

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path(), self.get_login_url())
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(
            Q(students=self.request.user) | Q(owner=self.request.user)
        ).distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.get_object()
        
        
        if 'module_id' in self.kwargs:
            context['module'] = course.modules.get(id=self.kwargs['module_id'])
        else:
            # Open the first module when no module was selected yet.
            context['module'] = course.modules.all()[0]
        if 'lesson_id' in self.kwargs:
            context['active_lesson'] = get_object_or_404(
                Lesson,
                module=context['module'],
                id=self.kwargs['lesson_id'],
            )
            context['material'] = getattr(context['active_lesson'], 'material', None)
        return context
