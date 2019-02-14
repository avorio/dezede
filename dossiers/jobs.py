from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _
from django_rq import job
from slugify import slugify

from common.utils.export import send_pdf
from .models import DossierDEvenements


@job
def dossier_to_pdf(dossier_pk, user_pk, site_pk, language_code):
    dossier = DossierDEvenements.objects.get(pk=dossier_pk)
    context = {'object': dossier}
    template_name = 'dossiers/dossierdevenements_detail.tex'
    subject = _('du dossier « %s »') % dossier
    filename = slugify(force_text(dossier))
    send_pdf(context, template_name, subject, filename, user_pk, site_pk,
             language_code)
