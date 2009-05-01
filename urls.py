from better_represent.models import *
from django.conf.urls.defaults import *

urlpatterns = patterns('better_represent.views',
    url(r'^$', 'index', name='better_represent_index'),
    url(r'^(?P<address_slug>[\w-]+)/$', 'address_detail', name="address_detail"),
    url(r'^(?P<rep_id>\d+)-(?P<first_name>\w+)-(?P<last_name>\w+)', 'rep_detail', name="rep_detail"),
)
urlpatterns += patterns('django.views.generic.list_detail',
    #url(r'^rep/(?P<object_id>\d+)/$', 'object_list', {'queryset': GenericRep.objects.all().live().annotate_max_stats().total_stats(), 'template_object_name': 'reps', 'template_name':"better_represent/rep_detail.html"}, "rep_detail", ),
)
