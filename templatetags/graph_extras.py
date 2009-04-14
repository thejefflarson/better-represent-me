from django import template
from django.template.defaulttags import WidthRatioNode
from better_represent.utils.json_coders import DateEncoder

register = template.Library()

@register.inclusion_tag('better_represent/graph.html')
def draw_graph(reps, num=3):
    list = {}
    for rep in reps[:num]:
        list[str(rep)] = rep.stats_by_day()
        list[str(rep)].reverse()
    return {'json': "%s" % DateEncoder().encode(list) }

@register.filter
def max_by_key(value, arg):
    return max([i[arg] for i in value])

