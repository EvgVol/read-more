from django.test import SimpleTestCase

from courses.management.commands.ml_theory import BLUEPRINTS, build_theory


class MlTheoryPilotTests(SimpleTestCase):
    def test_python_data_analysis_theory_has_readable_learning_contract(self):
        theory = build_theory('Python для анализа данных')

        self.assertIn('## Как читать этот урок', theory)
        self.assertIn(':::important', theory)
        self.assertIn(':::practice', theory)
        self.assertIn('```python', theory)
        self.assertIn('| Этап | Что проверяем |', theory)
        self.assertIn(
            '/static/images/courses/ml-inzhener/python/01-data-flow.svg',
            theory,
        )
        self.assertIn('alt="', theory)
        self.assertGreaterEqual(theory.count('## '), 8)

    def test_other_theory_blueprints_remain_available(self):
        for title in BLUEPRINTS:
            with self.subTest(title=title):
                self.assertTrue(build_theory(title).strip())
