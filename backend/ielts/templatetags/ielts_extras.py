import json

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(is_safe=True)
def to_json(value):
    return mark_safe(json.dumps(value))
