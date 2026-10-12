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
