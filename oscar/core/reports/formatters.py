import StringIO
import csv
from django.template.loader import render_to_string
from django.utils.html import mark_safe


class Formatter(object):
    """
    """

    paginator_class = None
    paginated_by = None

    def get_paginator_class(self):
        return self.paginator_class

    def get_data_chunk(self, data, page=None):
        paginator_class = self.get_paginator_class()
        if not paginator_class:
            # if there is no paginator return everything
            return data
        paginated_data = paginator_class(data, self.paginated_by)
        chunk = paginated_data.page(page)
        return chunk.object_list

    def __init__(self, context={}):
        self.context = context

    def render(self):
        pass


class CSVFormatter(Formatter):
    content_type = 'application/csv'
    fields = []

    def render(self, data):
        def _getattr(obj, attr_path):
            parts = attr_path.split('.')
            return_value = obj
            for part in parts:
                return_value = getattr(return_value, part)
            return return_value

        fd = StringIO.StringIO()
        output_file = csv.writer(fd, delimiter=',', quotechar='"')
        output_file.writerow(self.fields)
        for row in self.get_data_chunk(data):
            output_row = [_getattr(row, field) for field in self.fields]
            output_file.writerow(output_row)
        output = fd.getvalue()
        fd.close()
        return output

class HTMLFormatter(Formatter):
    content_type = 'text/html'
    data_context_name = 'data'
    template_name = ''

    def render(self, data):
        self.context.update({self.data_context_name: self.get_data_chunk(data)})
        return mark_safe(render_to_string(self.template_name, self.context))

