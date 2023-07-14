from django.views.generic import DetailView
from django.contrib.contenttypes.models import ContentType

from courses.models.course import Course
from reviews.models import Review


class CourseDetailView(DetailView):
    """A view a detail course."""

    model = Course
    template_name = 'courses/manage/course/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course_content_type = ContentType.objects.get_for_model(Course)
        reviews = Review.objects.filter(content_type=course_content_type,
                                        object_id=self.object.pk)
        context['reviews'] = reviews
        return context
