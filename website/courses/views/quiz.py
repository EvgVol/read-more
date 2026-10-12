from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect
from django.views import View

from courses.models.course import Course
from courses.models.lessons import Lesson
from courses.models.quiz import QuizQuestion
from courses.services.quiz import submit_quiz


class QuizSubmitView(LoginRequiredMixin, View):
    """Grade a quiz using server-side answers and redirect to its result."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path(), self.get_login_url())
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        course = get_object_or_404(
            Course.objects.filter(
                Q(students=request.user) | Q(owner=request.user),
            ).distinct(),
            slug=kwargs['slug'],
        )
        module = get_object_or_404(course.modules, id=kwargs['module_id'])
        lesson = get_object_or_404(Lesson, module=module, id=kwargs['lesson_id'])
        questions = QuizQuestion.objects.filter(lesson=lesson, published=True)
        answers = {
            str(question.id): request.POST.getlist(f'question_{question.id}')
            for question in questions
        }
        try:
            attempt = submit_quiz(user=request.user, lesson=lesson, answers=answers)
        except ValidationError as error:
            return HttpResponseBadRequest(error.messages[0])
        return redirect(
            f'/ru/course/{course.slug}/trainer/{module.id}/lesson/{lesson.id}/'
            f'?step=2&quiz_attempt={attempt.id}#lesson-quiz'
        )
