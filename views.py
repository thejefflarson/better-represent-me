import datetime
from better_represent.models import *
from better_represent.search import NewsAggregator
from polygons.models import *
from better_represent.forms import *
from django.core.paginator import Paginator
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseForbidden, HttpResponseRedirect 
from django.template.defaultfilters import slugify
from django.conf import settings
from django.views.decorators.cache import cache_page
from django.db.models import Q


def paginate(objects_list, request, num=30):
    paginator = Paginator(objects_list, num) # Show 25 contacts per page
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    try:
        return paginator.page(page)
    except (EmptyPage, InvalidPage):
        return paginator.page(paginator.num_pages)

def index(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            try:
                try:
                    address=Address.objects.get(address__icontains=address_normalize(form.cleaned_data['address']))
                except Address.DoesNotExist:
                    address=Address(address=form.cleaned_data['address'])
                    address.save()
                except Address.MultipleObjectsReturned:
                    address=Address.objects.filter(address__icontains=address_normalize(form.cleaned_data['address']))[0]
                return HttpResponseRedirect(address.get_absolute_url())
            except Address.AddressPointNotFoundError, e:
                form.errors['address']=[u"I couldn't find that address."]
                if settings.DEBUG:
                    form.errors['address'][0] += "%s" % (e)

    else:
        form = AddressForm()

    representatives = GenericRep.objects.all().live().annotate_max_stats().total_stats()
    return render_to_response('better_represent/index.html', {'form': form, 'popular': paginate(representatives, request)})

@cache_page(0)
def address_detail(request, address_slug=None):
    address = get_object_or_404(Address, slug=address_slug)
    state = get_object_or_404(State, poly__contains=address.point)
    cd = get_object_or_404(CongressionalDistrict, poly__contains=address.point)
    representatives = GenericRep.objects.all().live().filter( (Q(type="H") & Q(district=cd)) | Q(type="S"), state=state)
    items = []
    for rep in representatives:
        items.extend(rep.items)
    items.sort(key=lambda x: x['datetime'], reverse=True)
    return render_to_response('better_represent/address_detail.html', {'address': address, 'state': state, 'data':items, 'reps': representatives})

def rep_detail(request, rep_type, rep_id):
    pass
