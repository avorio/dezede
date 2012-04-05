from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import Context, RequestContext
from django.views.generic import ListView, DetailView
from musicologie.catalogue.models import *
from musicologie.catalogue.forms import *
from collections import OrderedDict

class SourceDetailView(DetailView):
    model = Source
    context_object_name = 'source'

class EvenementListView(ListView):
    model = Evenement
    context_object_name = 'evenements'
    def get_queryset(self):
        q = {}
        bindings = {
          'lieu_slug': 'ancrage_debut__lieu__slug',
          'year': 'ancrage_debut__date__year',
          'month': 'ancrage_debut__date__month',
          'day': 'ancrage_debut__date__day',
        }
        for key, value in self.kwargs.items():
            if value:
                q[bindings[key]] = value
        return Evenement.objects.filter(**q)

class EvenementDetailView(DetailView):
    model = Evenement

class LieuListView(ListView):
    model = Lieu
    queryset = Lieu.objects.filter(parent=None)
    context_object_name = 'lieux'

class LieuDetailView(DetailView):
    model = Lieu
    context_object_name = 'lieu'

class IndividuListView(ListView):
    model = Individu
    context_object_name = 'individus'

class IndividuDetailView(DetailView):
    model = Individu
    context_object_name = 'individu'

class OeuvreDetailView(DetailView):
    model = Oeuvre
    context_object_name = 'oeuvre'

def saisie_source(request, source_id=None):
    if source_id != None:
        source = get_object_or_404(Source, pk=source_id)
    else:
        source = None
    if request.method == 'POST':
        form = SourceForm(request.POST, instance=source)
        if form.is_valid():
            form.save()
            return redirect('saisie_sources')
    else:
        form = SourceForm(instance=source)
    c = RequestContext(request, {'form': form, 'sources': Source.objects.all(), 'source': source,})
    return render_to_response('catalogue/saisie_source.html', c)

