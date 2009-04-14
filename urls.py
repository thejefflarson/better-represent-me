from better_represent.models import *
from django.conf.urls.defaults import *

urlpatterns = patterns('better_represent.views',
    url(r'^$', 'index', name='better_represent_index'),
    url(r'^(?P<address_slug>[\w-]+)/$', 'address_detail', name="address_detail"),
)
