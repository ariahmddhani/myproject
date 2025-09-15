import os
from django import template
import re

register = template.Library()

@register.filter
def filename(value):
    if not value:  # Cek apakah value kosong atau None
        return None
    return os.path.basename(value)

@register.filter(name='replace_headings')
def replace_headings(value):
    # Replace all <h1>, <h2>, <h3>... tags with <p>
    value = re.sub(r'<h[1-6](.*?)>', r'<p\1>', value)
    value = re.sub(r'</h[1-6]>', '</p>', value)
    return value
