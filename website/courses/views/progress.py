from django.contrib.auth.views import redirect_to_login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect
from django.views import View

from courses.models.course import Course
from courses.models.lesson_progress import LessonProgress
from courses.models.lessons import Lesson
from courses.services.lesson_progress import complete_step


class LessonProgressUpdateView(LoginRequiredMixin, View):
    """Persist a sequential lesson-step completion for the current student."""

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
        lesson = get_object_or_404(
            Lesson,
            module=module,
            id=kwargs['lesson_id'],
        )
        if request.POST.get('action') != 'complete_step':
            return HttpResponseBadRequest('Неизвестное действие.')
        try:
            step = int(request.POST.get('step', ''))
            progress = complete_step(
                user=request.user,
                lesson=lesson,
                step=step,
            )
        except (TypeError, ValueError):
            return HttpResponseBadRequest('Номер этапа должен быть числом.')
        except ValidationError as error:
            return HttpResponseBadRequest(error.messages[0])

        if progress.status == LessonProgress.Status.COMPLETED:
            next_lesson = Lesson.objects.filter(
                module__course=course,
            ).filter(
                Q(module__order__gt=module.order)
                | Q(module=module, order__gt=lesson.order)
            ).order_by('module__order', 'order', 'id').first()
            if next_lesson:
                return redirect(
                    'courses:course_trainer_lesson',
                    course.slug,
                    next_lesson.module_id,
                    next_lesson.id,
                )

        response = redirect(
            'courses:course_trainer_lesson',
            course.slug,
            module.id,
            lesson.id,
        )
        response['Location'] += f'?step={progress.current_step}'
        return response
