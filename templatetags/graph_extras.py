from django import template
from django.template.defaulttags import WidthRatioNode
from better_represent.utils.json_coders import DateEncoder

register = template.Library()

def merge(reps):
    items = []
    for rep in reps:
        items.extend(rep.items)
    items.sort(key=lambda x: x['datetime'], reverse=True)
    return items

@register.inclusion_tag('better_represent/graph.html')
def draw_graph(reps, num=3, pronoun=''):
    list = {}
    by_day = []
    max = 0
    try:
        reps = reps[:num]
    except:
        reps = [reps]
    for rep in reps:
        list[str(rep)] = rep.stats_by_day()
        for day in rep.stats_by_day():
            day['rep'] = rep
            by_day.append(day)
            if max < day['num_stats']: 
                max = day['num_stats']
        by_day.sort(key=lambda x: x['date'])
    return {'json': "%s" % DateEncoder().encode(list), 'data': merge(reps), 'pronoun': pronoun, 'by_day':by_day, 'max':max }

@register.filter
def max_by_key(value, arg):
#    return max([i[arg] for i in value])
    pass

