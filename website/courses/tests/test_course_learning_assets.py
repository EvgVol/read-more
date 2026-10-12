from pathlib import Path

from django.test import SimpleTestCase


class CourseLearningAssetTests(SimpleTestCase):
    def test_learning_stylesheet_and_template_contract_exist(self):
        css_path = Path(__file__).resolve().parents[2] / 'static/css/course-learning.css'
        template_path = (
            Path(__file__).resolve().parents[2]
            / 'templates/courses/manage/course/trainer.html'
        )

        css = css_path.read_text()
        template = template_path.read_text()

        self.assertIn('{% static \'css/course-learning.css\' %}', template)
        self.assertIn('.course-learning__reading', css)
        self.assertIn('.course-learning__sidebar', css)
        self.assertIn('@media (max-width: 991.98px)', css)
        self.assertIn('overflow-x: auto', css)
        self.assertIn('outline:', css)

    def test_global_loader_is_hidden_after_page_load(self):
        template_path = (
            Path(__file__).resolve().parents[2] / 'templates/main.html'
        )
        template = template_path.read_text()

        self.assertIn("window.addEventListener('load'", template)
        self.assertIn("loader.style.display = 'none'", template)

    def test_reading_styles_and_pilot_diagrams_exist(self):
        css_path = Path(__file__).resolve().parents[2] / 'static/css/course-learning.css'
        static_root = Path(__file__).resolve().parents[2] / 'static'
        css = css_path.read_text()

        self.assertIn('.course-learning__toc', css)
        self.assertIn('.lesson-callout', css)
        self.assertIn('.lesson-material figure', css)
        self.assertIn('.lesson-block', css)
        self.assertIn('.lesson-block--summary', css)
        self.assertIn('.lesson-block--code-example', css)
        self.assertIn('.lesson-quiz', css)
        self.assertIn('.lesson-quiz__result', css)
        self.assertIn('.course-learning__quiz-summary', css)
        self.assertIn('.course-learning__module-quiz', css)
        self.assertIn('@media (max-width: 575.98px)', css)
        for diagram in (
            '01-data-flow.svg',
            '02-boundaries.svg',
            '03-validation-loop.svg',
        ):
            self.assertTrue(
                (static_root / 'images/courses/ml-inzhener/python' / diagram).exists()
            )
