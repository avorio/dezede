# coding: utf-8

from __future__ import unicode_literals
import json
from django.db.models import Q
from django.http import HttpResponse
from django.utils.encoding import smart_text
from django.views.generic import ListView, TemplateView
from haystack.views import SearchView
from libretto.models import Oeuvre, Lieu, Individu
from libretto.search_indexes import autocomplete_search
from .models import Diapositive


class HomeView(ListView):
    model = Diapositive
    template_name = 'home.html'

    def get_queryset(self):
        qs = super(HomeView, self).get_queryset()
        return qs.published(self.request)


class CustomSearchView(SearchView):
    """
    Custom SearchView to fix spelling suggestions.
    """
    def extra_context(self):
        context = {'suggestion': None}

        if self.results.query.backend.include_spelling:
            q = self.query or ''
            suggestion = self.form.get_suggestion() or ''
            if suggestion.lower() != q.lower():
                context['suggestion'] = suggestion

        return context

    def get_results(self):
        sqs = super(CustomSearchView, self).get_results()
        user_id = self.request.user.id
        filters = Q(public=True)
        if user_id is not None:
            filters |= Q(owner_id=user_id)
        return sqs.filter(filters)


def autocomplete(request):
    q = request.GET.get('q', '')
    suggestions = autocomplete_search(request, q)
    data = json.dumps(map(smart_text, suggestions))
    return HttpResponse(data, content_type='application/json')


class ErrorView(TemplateView):
    status = 200

    def render_to_response(self, context, **response_kwargs):
        response_kwargs['status'] = self.status
        self.template_name = '%s.html' % self.status
        return super(ErrorView, self).render_to_response(context,
                                                         **response_kwargs)


class BibliographieView(TemplateView):
    template_name = 'pages/bibliographie.html'

    def get_context_data(self, **kwargs):
        context = super(BibliographieView, self).get_context_data(**kwargs)
        context.update(
            oeuvres=Oeuvre.objects.all(),
            individus=Individu.objects.all(),
            lieux=Lieu.objects.all(),
        )
        return context
