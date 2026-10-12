"""Safe, dependency-free reference solution for lesson 2717.

The web application never executes student code. This module is a fixed
reference implementation exercised by repository tests and used for examples.
"""

import csv
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Iterable


REQUIRED_COLUMNS = ('order_id', 'amount', 'status')
ALLOWED_STATUSES = {'paid', 'pending', 'cancelled'}


class InvalidOrderError(ValueError):
    """An input row violates the lesson's strict CSV contract."""


def read_orders(path: str | Path) -> list[dict[str, str]]:
    source = Path(path)
    with source.open('r', encoding='utf-8', newline='') as handle:
        reader = csv.DictReader(handle)
        columns = reader.fieldnames or []
        missing = [name for name in REQUIRED_COLUMNS if name not in columns]
        if missing:
            raise InvalidOrderError(
                f'missing required columns: {", ".join(missing)}'
            )
        return list(reader)


def _parse_order(row: dict[str, str | None], line_number: int) -> dict[str, object]:
    order_id = (row.get('order_id') or '').strip()
    if not order_id:
        raise InvalidOrderError(f'line {line_number}: order_id is required')

    raw_amount = (row.get('amount') or '').strip()
    try:
        amount = Decimal(raw_amount)
    except (InvalidOperation, ValueError):
        raise InvalidOrderError(
            f'line {line_number}: amount must be a positive number'
        ) from None
    if amount <= 0:
        raise InvalidOrderError(
            f'line {line_number}: amount must be a positive number'
        )

    status = (row.get('status') or '').strip()
    if status not in ALLOWED_STATUSES:
        allowed = ', '.join(sorted(ALLOWED_STATUSES))
        raise InvalidOrderError(
            f'line {line_number}: status must be one of {allowed}'
        )
    return {'order_id': order_id, 'amount': amount, 'status': status, 'comment': row.get('comment') or ''}


def summarize_orders(rows_or_path: Iterable[dict[str, str]] | str | Path) -> dict[str, object]:
    """Validate every row strictly and return a stable, JSON-ready summary."""
    if isinstance(rows_or_path, (str, Path)):
        raw_rows = read_orders(rows_or_path)
        columns = list(raw_rows[0].keys()) if raw_rows else list(REQUIRED_COLUMNS)
    else:
        raw_rows = list(rows_or_path)
        columns = list(raw_rows[0].keys()) if raw_rows else list(REQUIRED_COLUMNS)

    parsed = [_parse_order(row, index) for index, row in enumerate(raw_rows, start=2)]
    total = sum((row['amount'] for row in parsed), Decimal('0'))
    missing_ratio = {
        column: sum(not (row.get(column) or '').strip() for row in raw_rows) / len(raw_rows)
        if raw_rows else 0.0
        for column in columns
    }
    return {
        'row_count': len(parsed),
        'columns': columns,
        'missing_ratio': missing_ratio,
        'amount_total': format(total, 'f'),
        'errors': [],
    }
