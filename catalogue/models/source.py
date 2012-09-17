# coding: utf-8

from .common import CustomModel, Document, Illustration, Etat, \
                    LOWER_MSG, PLURAL_MSG, DATE_MSG, autoslugify, calc_pluriel
from .functions import ex, str_list, cite, no, date_html, href
from . import *
from django.db.models import CharField, SlugField, DateField, ForeignKey, \
                             ManyToManyField, permalink
from tinymce.models import HTMLField
from django.utils.html import strip_tags
from django.utils.translation import ungettext_lazy, ugettext, \
                                     ugettext_lazy as _


class TypeDeSource(CustomModel):
    nom = CharField(max_length=200, help_text=LOWER_MSG, unique=True)
    nom_pluriel = CharField(max_length=230, blank=True,
        verbose_name=_('nom (au pluriel)'),
        help_text=PLURAL_MSG)
    slug = SlugField(blank=True)

    class Meta:
        verbose_name = ungettext_lazy('type de source', 'types de source', 1)
        verbose_name_plural = ungettext_lazy('type de source',
                                             'types de source', 2)
        ordering = ['slug']
        app_label = 'catalogue'

    def save(self, *args, **kwargs):
        self.slug = autoslugify(self, unicode(self))
        super(TypeDeSource, self).save(*args, **kwargs)

    def pluriel(self):
        return calc_pluriel(self)

    def __unicode__(self):
        return self.nom


class Source(CustomModel):
    nom = CharField(max_length=200, help_text=ex(_('Journal de Rouen')))
    numero = CharField(max_length=50, blank=True)
    date = DateField(help_text=DATE_MSG)
    page = CharField(max_length=50, blank=True)
    type = ForeignKey(TypeDeSource, related_name='sources',
        help_text=ex(_('compte rendu')))
    contenu = HTMLField(blank=True)
    auteurs = ManyToManyField('Auteur', related_name='sources', blank=True,
        null=True)
    evenements = ManyToManyField('Evenement', related_name='sources', blank=True,
        null=True)
    documents = ManyToManyField('Document', related_name='sources', blank=True,
        null=True)
    illustrations = ManyToManyField('Illustration', related_name='sources',
        blank=True, null=True)
    etat = ForeignKey('Etat', related_name='sources', null=True, blank=True)
    notes = HTMLField(blank=True)

    @permalink
    def get_absolute_url(self):
        return ('source_pk', [self.pk])

    def permalien(self):
        return self.get_absolute_url()

    def link(self):
        return self.html()

    def individus_auteurs(self):
        pk_list = self.auteurs.values_list('individus', flat=True)
        return Individu.objects.in_bulk(pk_list).values()

    def calc_auteurs(self, tags=True):
        auteurs = self.auteurs.iterator()
        return str_list(a.html(tags) for a in auteurs)

    def html(self, tags=True):
        url = None if not tags else self.get_absolute_url()
        l = []
        l.append('%s' % cite(self.nom, tags))
        if self.numero:
            l.append(no(self.numero))
        date = ugettext('du %(date)s') % {'date': date_html(self.date, tags)}
        l.append(date)
        if self.page:
            l.append(ugettext('p. %s') % self.page)
        out = ' '.join(l)
        return href(url, out, tags)
    html.short_description = _('rendu HTML')
    html.allow_tags = True

    def disp_contenu(self):
        return self.contenu[:200] + u'[...]' + self.contenu[-50:]
    disp_contenu.short_description = _('contenu')
    disp_contenu.allow_tags = True

    class Meta:
        verbose_name = ungettext_lazy('source', 'sources', 1)
        verbose_name_plural = ungettext_lazy('source', 'sources', 2)
        ordering = ['date', 'nom', 'numero', 'page', 'type']
        app_label = 'catalogue'

    def __unicode__(self):
        return strip_tags(self.html(False))
