from django.db.models import (
    CharField, ForeignKey, ManyToManyField, permalink, PROTECT, URLField,
    CASCADE)
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext, ugettext_lazy as _
from tinymce.models import HTMLField
from .base import (
    CommonModel, AutoriteModel, LOWER_MSG, PLURAL_MSG, calc_pluriel,
    SlugModel, PublishedManager, PublishedQuerySet, AncrageSpatioTemporel, Fichier)

from common.utils.base import OrderedDefaultDict
from common.utils.html import cite, href, small, hlp
from common.utils.text import ex, str_list
from typography.models import TypographicModel


__all__ = (
    'TypeDeSource', 'Source', 'SourceEvenement', 'SourceOeuvre',
    'SourceIndividu', 'SourceEnsemble', 'SourceLieu', 'SourcePartie'
)


class TypeDeSource(CommonModel, SlugModel):
    nom = CharField(_('nom'), max_length=200, help_text=LOWER_MSG, unique=True,
                    db_index=True)
    nom_pluriel = CharField(_('nom (au pluriel)'), max_length=230, blank=True,
                            db_index=True, help_text=PLURAL_MSG)
    # TODO: Ajouter un classement et changer ordering en conséquence.

    class Meta(object):
        verbose_name = _('type de source')
        verbose_name_plural = _('types de source')
        ordering = ('slug',)

    @staticmethod
    def invalidated_relations_when_saved(all_relations=False):
        if all_relations:
            return ('sources',)
        return ()

    def pluriel(self):
        return calc_pluriel(self)

    def __str__(self):
        return self.nom


class SourceQuerySet(PublishedQuerySet):
    def group_by_type(self):
        sources = OrderedDefaultDict()
        for source in self:
            sources[source.type].append(source)
        return sources.items()

    def prefetch(self):
        fichiers = Fichier._meta.db_table
        sources = Source._meta.db_table
        return self.select_related('type').extra(select={
            '_has_others':
            f'EXISTS (SELECT 1 FROM {fichiers} '
            f'WHERE source_id = {sources}.id AND type = {Fichier.OTHER})',
            '_has_images':
            f'EXISTS (SELECT 1 FROM {fichiers} '
            f'WHERE source_id = {sources}.id AND type = {Fichier.IMAGE})',
            '_has_audios':
            f'EXISTS (SELECT 1 FROM {fichiers} '
            f'WHERE source_id = {sources}.id AND type = {Fichier.AUDIO})',
            '_has_videos':
            f'EXISTS (SELECT 1 FROM {fichiers} '
            f'WHERE source_id = {sources}.id AND type = {Fichier.VIDEO})'}
        ).only(
            'titre', 'numero', 'folio', 'page', 'lieu_conservation',
            'cote', 'url', 'transcription', 'date', 'date_approx',
            'type__nom', 'type__nom_pluriel',
        )

    def with_video(self):
        return self.filter(fichiers__type=Fichier.VIDEO).distinct()

    def with_audio(self):
        return self.filter(fichiers__type=Fichier.AUDIO).distinct()

    def with_image(self):
        return self.filter(fichiers__type=Fichier.IMAGE).distinct()

    def with_other(self):
        return self.filter(fichiers__type=Fichier.OTHER).distinct()

    def with_text(self):
        return self.exclude(transcription='')

    def with_link(self):
        return self.exclude(url='')

    def with_data_type(self, data_type):
        if data_type == Source.VIDEO:
            return self.with_video()
        if data_type == Source.AUDIO:
            return self.with_audio()
        if data_type == Source.IMAGE:
            return self.with_image()
        if data_type == Source.OTHER:
            return self.with_other()
        if data_type == Source.TEXT:
            return self.with_text()
        if data_type == Source.LINK:
            return self.with_link()
        raise ValueError('Unknown data type.')


class SourceManager(PublishedManager):
    queryset_class = SourceQuerySet

    def group_by_type(self):
        return self.get_queryset().group_by_type()

    def prefetch(self):
        return self.get_queryset().prefetch()

    def with_video(self):
        return self.get_queryset().with_video()

    def with_audio(self):
        return self.get_queryset().with_audio()

    def with_image(self):
        return self.get_queryset().with_image()

    def with_other(self):
        return self.get_queryset().with_other()

    def with_text(self):
        return self.get_queryset().with_text()

    def with_link(self):
        return self.get_queryset().with_link()

    def with_data_type(self, data_type):
        return self.get_queryset().with_data_type(data_type)


class Source(AutoriteModel):
    type = ForeignKey('TypeDeSource', related_name='sources',
                      help_text=ex(_('compte rendu')), verbose_name=_('type'),
                      on_delete=PROTECT)
    titre = CharField(_('titre'), max_length=200, blank=True, db_index=True,
                      help_text=ex(_('Journal de Rouen')))
    legende = CharField(_('légende'), max_length=600, blank=True,
                        help_text=_('Recommandée pour les images.'))

    ancrage = AncrageSpatioTemporel(has_heure=False, has_lieu=False)
    numero = CharField(_('numéro'), max_length=50, blank=True, db_index=True,
                       help_text=_('Sans « № ». Exemple : « 52 »'))
    folio = CharField(_('folio'), max_length=10, blank=True,
                      help_text=_('Sans « f. ». Exemple : « 3 ».'))
    page = CharField(_('page'), max_length=10, blank=True, db_index=True,
                     help_text=_('Sans « p. ». Exemple : « 3 »'))
    lieu_conservation = CharField(_('lieu de conservation'), max_length=50,
                                  blank=True, db_index=True)
    cote = CharField(_('cote'), max_length=60, blank=True, db_index=True)
    url = URLField(_('URL'), blank=True,
                   help_text=_('Uniquement un permalien extérieur à Dezède.'))

    transcription = HTMLField(_('transcription'), blank=True,
        help_text=_('Recopier la source ou un extrait en suivant les règles '
                    'définies dans '  # FIXME: Don’t hardcode the URL.
                    '<a href="/examens/source">le didacticiel.</a>'))

    evenements = ManyToManyField(
        'Evenement', through='SourceEvenement', related_name='sources',
        verbose_name=_('événements'))
    oeuvres = ManyToManyField('Oeuvre', through='SourceOeuvre',
                              related_name='sources', verbose_name=_('œuvres'))
    individus = ManyToManyField(
        'Individu', through='SourceIndividu', related_name='sources',
        verbose_name=_('individus'))
    ensembles = ManyToManyField(
        'Ensemble', through='SourceEnsemble', related_name='sources',
        verbose_name=_('ensembles'))
    lieux = ManyToManyField('Lieu', through='SourceLieu',
                            related_name='sources', verbose_name=_('lieux'))
    parties = ManyToManyField(
        'Partie', through='SourcePartie', related_name='sources',
        verbose_name=_('sources'))

    objects = SourceManager()

    class Meta(object):
        verbose_name = _('source')
        verbose_name_plural = _('sources')
        ordering = ('date', 'titre', 'numero', 'page',
                    'lieu_conservation', 'cote')
        permissions = (('can_change_status', _('Peut changer l’état')),)

    def __str__(self):
        return strip_tags(self.html(False))

    @permalink
    def get_absolute_url(self):
        return 'source_permanent_detail', (self.pk,)

    def permalien(self):
        return self.get_absolute_url()

    def link(self):
        return self.html()
    link.short_description = _('Lien')
    link.allow_tags = True

    def auteurs_html(self, tags=True):
        return self.auteurs.html(tags)

    def no(self):
        return ugettext('n° %s') % self.numero

    def f(self):
        return ugettext('f. %s') % self.folio

    def p(self):
        return ugettext('p. %s') % self.page

    def html(self, tags=True, pretty_title=False):
        url = None if not tags else self.get_absolute_url()
        conservation = hlp(self.lieu_conservation,
                           ugettext('Lieu de conservation'), tags)
        if self.ancrage.date or self.ancrage.date_approx:
            ancrage = hlp(self.ancrage.html(tags, caps=False), ugettext('date'))
        else:
            ancrage = None
        if self.cote:
            conservation += f", {hlp(self.cote, 'cote', tags)}"
        if self.titre:
            l = [cite(self.titre, tags)]
            if self.numero:
                l.append(self.no())
            if ancrage is not None:
                l.append(ancrage)
            if self.folio:
                l.append(hlp(self.f(), ugettext('folio'), tags))
            if self.page:
                l.append(hlp(self.p(), ugettext('page'), tags))
            if self.lieu_conservation:
                l[-1] += f' ({conservation})'
        else:
            l = [conservation]
            if ancrage is not None:
                l.append(ancrage)
        l = (l[0], small(str_list(l[1:]), tags=tags)) if pretty_title else l
        out = str_list(l)
        return mark_safe(href(url, out, tags))
    html.short_description = _('rendu HTML')
    html.allow_tags = True

    def pretty_title(self):
        return self.html(pretty_title=True)

    def has_events(self):
        if hasattr(self, '_has_events'):
            return self._has_events
        return self.evenements.exists()
    has_events.short_description = _('événements')
    has_events.boolean = True
    has_events.admin_order_field = 'evenements'

    def has_program(self):
        if hasattr(self, '_has_program'):
            return self._has_program
        return self.evenements.with_program().exists()
    has_program.short_description = _('programme')
    has_program.boolean = True

    def has_fichiers(self):
        attrs = ('_has_others', '_has_images', '_has_audios', '_has_videos')
        if all(hasattr(self, attr) for attr in attrs):
            return any(getattr(self, attr) for attr in attrs)
        return self.fichiers.exists()

    def has_others(self):
        if hasattr(self, '_has_others'):
            return self._has_others
        return self.fichiers.others().exists()

    def has_images(self):
        if hasattr(self, '_has_images'):
            return self._has_images
        return self.fichiers.images().exists()

    def has_audios(self):
        if hasattr(self, '_has_audios'):
            return self._has_audios
        return self.fichiers.audios().exists()

    def has_videos(self):
        if hasattr(self, '_has_videos'):
            return self._has_videos
        return self.fichiers.videos().exists()

    def is_empty(self):
        return not (self.transcription or self.url or self.has_fichiers())

    DATA_TYPES = ('video', 'audio', 'image', 'other', 'text', 'link')
    VIDEO, AUDIO, IMAGE, OTHER, TEXT, LINK = DATA_TYPES

    @property
    def data_types(self):
        data_types = []
        if self.has_videos():
            data_types.append(self.VIDEO)
        if self.has_audios():
            data_types.append(self.AUDIO)
        if self.has_images():
            data_types.append(self.IMAGE)
        if self.has_others():
            data_types.append(self.OTHER)
        if self.transcription:
            data_types.append(self.TEXT)
        if self.url:
            data_types.append(self.LINK)
        return data_types

    ICONS = {
        VIDEO: '<i class="fa fa-fw fa-video-camera"></i>',
        AUDIO: '<i class="fa fa-fw fa-volume-up"></i>',
        IMAGE: '<i class="fa fa-fw fa-photo"></i>',
        OTHER: '<i class="fa fa-fw fa-paperclip"></i>',
        TEXT: '<i class="fa fa-fw fa-file-text-o"></i>',
        LINK: '<i class="fa fa-fw fa-external-link"></i>',
    }

    DATA_TYPES_WITH_ICONS = (
        (VIDEO, _(f'{ICONS[VIDEO]} Vidéo')),
        (AUDIO, _(f'{ICONS[AUDIO]} Audio')),
        (IMAGE, _(f'{ICONS[IMAGE]} Image')),
        (OTHER, _(f'{ICONS[OTHER]} Autre')),
        (TEXT, _(f'{ICONS[TEXT]} Texte')),
        (LINK, _(f'{ICONS[LINK]} Lien')),
    )

    @property
    def icons(self):
        return ''.join([self.ICONS[data_type]
                        for data_type in self.data_types])


class SourceEvenement(TypographicModel):
    source = ForeignKey(Source, related_name='sourceevenement_set',
                        on_delete=CASCADE)
    evenement = ForeignKey('Evenement', verbose_name=_('événement'),
                           related_name='sourceevenement_set',
                           on_delete=CASCADE)

    class Meta(object):
        db_table = 'libretto_source_evenements'
        unique_together = ('source', 'evenement')


class SourceOeuvre(TypographicModel):
    source = ForeignKey(Source, related_name='sourceoeuvre_set',
                        on_delete=CASCADE)
    oeuvre = ForeignKey('Oeuvre', verbose_name=_('œuvre'),
                        related_name='sourceoeuvre_set',
                        on_delete=CASCADE)

    class Meta(object):
        db_table = 'libretto_source_oeuvres'
        unique_together = ('source', 'oeuvre')


class SourceIndividu(TypographicModel):
    source = ForeignKey(Source, related_name='sourceindividu_set',
                        on_delete=CASCADE)
    individu = ForeignKey('Individu', verbose_name=_('individu'),
                          related_name='sourceindividu_set',
                          on_delete=CASCADE)

    class Meta(object):
        db_table = 'libretto_source_individus'
        unique_together = ('source', 'individu')


class SourceEnsemble(TypographicModel):
    source = ForeignKey(Source, related_name='sourceensemble_set',
                        on_delete=CASCADE)
    ensemble = ForeignKey('Ensemble', verbose_name=_('ensemble'),
                          related_name='sourceensemble_set',
                          on_delete=CASCADE)

    class Meta(object):
        db_table = 'libretto_source_ensembles'
        unique_together = ('source', 'ensemble')


class SourceLieu(TypographicModel):
    source = ForeignKey(Source, related_name='sourcelieu_set',
                        on_delete=CASCADE)
    lieu = ForeignKey('Lieu', verbose_name=_('lieu'),
                      related_name='sourcelieu_set',
                      on_delete=CASCADE)

    class Meta(object):
        db_table = 'libretto_source_lieux'
        unique_together = ('source', 'lieu')


class SourcePartie(TypographicModel):
    source = ForeignKey(Source, related_name='sourcepartie_set',
                        on_delete=CASCADE)
    partie = ForeignKey('Partie', verbose_name=_('rôle ou instrument'),
                        related_name='sourcepartie_set', on_delete=CASCADE)

    class Meta(object):
        db_table = 'libretto_source_parties'
        unique_together = ('source', 'partie')
