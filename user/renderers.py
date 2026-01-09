import csv
from io import StringIO
from rest_framework import renderers


class CSVRenderer(renderers.BaseRenderer):
    media_type = 'text/csv'
    format = 'csv'

    def render(self, data : dict | None, accepted_media_type=None, renderer_context=None):
        if data is None:
            return ''

        csv_buffer = StringIO()
        writer = csv.DictWriter(csv_buffer, fieldnames=data.keys())
        writer.writeheader()
        writer.writerow(data)

        return csv_buffer.getvalue()
