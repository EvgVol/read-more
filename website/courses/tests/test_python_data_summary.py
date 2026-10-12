from pathlib import Path

from django.test import SimpleTestCase

from courses.lesson_examples.python_data_summary import (
    InvalidOrderError,
    read_orders,
    summarize_orders,
)


class PythonDataSummaryTests(SimpleTestCase):
    def test_valid_csv_returns_structured_summary(self):
        path = Path(__file__).parent / 'fixtures' / 'orders_valid.csv'
        result = summarize_orders(path)

        self.assertEqual(result['row_count'], 2)
        self.assertEqual(result['columns'], ['order_id', 'amount', 'status', 'comment'])
        self.assertEqual(result['missing_ratio']['comment'], 0.5)
        self.assertEqual(result['amount_total'], '200.50')
        self.assertEqual(result['errors'], [])

    def test_missing_file_is_explicit(self):
        with self.assertRaises(FileNotFoundError):
            read_orders('/tmp/read-more-does-not-exist.csv')

    def test_invalid_amount_stops_with_line_number(self):
        path = Path(__file__).parent / 'fixtures' / 'orders_invalid_amount.csv'

        with self.assertRaisesRegex(InvalidOrderError, r'line 3.*amount'):
            summarize_orders(path)

