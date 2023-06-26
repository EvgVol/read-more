import csv
import datetime
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _


def export_to_csv(modeladmin, request, queryset):
    opts = modeladmin.model._meta
    content_disposition = f'attachment; filename={opts.verbose_name}.csv'
    response = HttpResponse(content_type='text/csv')
    response['Content-Disponsition'] = content_disposition
    writer = csv.writer(response)
    fields = [field for field in opts.get_fields()
              if not field.many_to_many
              and not field.one_to_many]
    # записать первую строку с информацией заголовка
    writer.writerow([field.verbose_name for field in fields])
    # записать строки данных
    for obj in queryset:
        data_row = []
        for field in fields:
            value = getattr(obj, field.name)
            if isinstance(value, datetime.datetime):
                value = value.strftime('%d/%m/%Y')
            data_row.append(value)
        writer.writerow(data_row)
    return response

export_to_csv.short_description = _('Export to CSV')