from django.views.generic import DetailView
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import redirect_to_login
from django.db.models import Prefetch, Q
from django.http import Http404

from courses.forms import CourseEnrollForm
from courses.models.course import Course
from courses.models.lesson_progress import LessonProgress
from courses.models.lesson_block import LessonBlock
from courses.models.lessons import Lesson
from courses.models.module import Module
from courses.models.quiz import QuizAttempt, QuizQuestion
from courses.services.lesson_blocks import get_lesson_stage_content
from courses.services.lesson_blocks import get_published_lesson_blocks
from courses.services.lesson_progress import course_progress, get_or_start_progress
from courses.services.quiz import course_quiz_progress, module_quiz_progress
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

    lesson_steps = (
        {'number': 1, 'key': 'objectives', 'label': 'Цели обучения'},
        {'number': 2, 'key': 'theory', 'label': 'Теория'},
        {'number': 3, 'key': 'practice', 'label': 'Практика'},
        {'number': 4, 'key': 'self_check', 'label': 'Самопроверка'},
        {'number': 5, 'key': 'resources', 'label': 'Источники'},
    )

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path(), self.get_login_url())
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        from courses.views.progress import LessonProgressUpdateView

        return LessonProgressUpdateView().post(request, *args, **kwargs)

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(
            Q(students=self.request.user) | Q(owner=self.request.user)
        ).distinct().prefetch_related(
            Prefetch(
                'modules',
                queryset=Module.objects.prefetch_related(
                    Prefetch(
                        'lessons',
                        queryset=Lesson.objects.select_related('material').order_by(
                            'order', 'id'
                        ).prefetch_related(
                            Prefetch(
                                'blocks',
                                queryset=LessonBlock.objects.filter(
                                    published=True,
                                ).order_by('position', 'id'),
                                to_attr='published_lesson_blocks',
                            ),
                            Prefetch(
                                'quiz_questions',
                                queryset=QuizQuestion.objects.filter(
                                    published=True,
                                ).order_by('position', 'id'),
                                to_attr='published_quiz_questions',
                            ),
                        ),
                    )
                ),
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = context['object']
        modules = list(course.modules.all())
        all_lessons = [
            lesson
            for module_item in modules
            for lesson in module_item.lessons.all()
        ]
        all_lessons.sort(key=lambda lesson: (lesson.module.order, lesson.order, lesson.id))
        progress_records = list(
            LessonProgress.objects.filter(
                user=self.request.user,
                lesson__module__course=course,
            ).select_related('lesson', 'lesson__module')
        )
        module_id = self.kwargs.get('module_id')
        if module_id:
            context['module'] = next(
                (module for module in modules if module.id == int(module_id)),
                None,
            )
            if context['module'] is None:
                raise Http404('Module not found')
        else:
            # Open the first module when no module was selected yet.
            context['module'] = modules[0]
        context['lesson_steps'] = self.lesson_steps
        context['course_progress'] = course_progress(
            user=self.request.user,
            course=course,
            lessons=all_lessons,
            progress_records=progress_records,
        )
        context['quiz_progress'] = course_quiz_progress(
            user=self.request.user,
            course=course,
        )
        context['quiz_progress_by_module'] = module_quiz_progress(
            user=self.request.user,
            course=course,
        )
        context['lesson_progress_by_id'] = {
            item.lesson_id: item
            for item in progress_records
        }
        if 'lesson_id' in self.kwargs:
            context['active_lesson'] = next(
                (
                    lesson
                    for lesson in context['module'].lessons.all()
                    if lesson.id == int(self.kwargs['lesson_id'])
                ),
                None,
            )
            if context['active_lesson'] is None:
                raise Http404('Lesson not found')
            context['material'] = getattr(context['active_lesson'], 'material', None)
            context['progress'] = get_or_start_progress(
                user=self.request.user,
                lesson=context['active_lesson'],
            )
            active_step = context['progress'].current_step
            requested_step = self.request.GET.get('step')
            if requested_step and requested_step.isdigit():
                active_step = int(requested_step)
            context['active_step'] = min(max(active_step, 1), 5)
            context['active_step_label'] = self.lesson_steps[context['active_step'] - 1]['label']
            if context['material']:
                active_descriptor = self.lesson_steps[context['active_step'] - 1]
                context['active_blocks'] = (
                    get_published_lesson_blocks(context['active_lesson'])
                    if active_descriptor['key'] == 'theory' else []
                )
                context['active_content'] = get_lesson_stage_content(
                    context['active_lesson'],
                    active_descriptor['key'],
                    context['material'],
                )
            context['quiz_questions'] = list(
                getattr(context['active_lesson'], 'published_quiz_questions', [])
            )
            context['quiz_attempt_history'] = list(QuizAttempt.objects.filter(
                user=self.request.user,
                lesson=context['active_lesson'],
            ).order_by('-submitted_at', '-id')[:10])
            context['quiz_last_attempt'] = context['quiz_attempt_history'][0] if context['quiz_attempt_history'] else None
            attempt_id = self.request.GET.get('quiz_attempt')
            context['quiz_attempt'] = None
            if attempt_id and attempt_id.isdigit():
                context['quiz_attempt'] = QuizAttempt.objects.filter(
                    id=int(attempt_id),
                    user=self.request.user,
                    lesson=context['active_lesson'],
                ).prefetch_related('answers__question').first()
            lesson_index = all_lessons.index(context['active_lesson'])
            context['previous_lesson'] = (
                all_lessons[lesson_index - 1] if lesson_index > 0 else None
            )
            context['next_lesson'] = (
                all_lessons[lesson_index + 1]
                if lesson_index < len(all_lessons) - 1 else None
            )
            context['recent_events'] = context['progress'].events.all()[:8]
        return context
