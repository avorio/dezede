from django.db.models import Manager
from django.test import TestCase
from libretto.api.models.utils import update_or_create
from libretto.models import *


class UpdateOrCreateTestCase(TestCase):
    cleans_up_after_itself = True

    def setUp(self):
        self.objects = []

        self.data = data = dict(
            nom='Dezède', pseudonyme='Dezède', prenoms='Nicolas')

        self.objects.append(update_or_create(Individu, data))
        # Tests if the following line does nothing.
        self.objects.append(update_or_create(Individu, data))

        data.update(nom_naissance='inconnu')
        self.objects.append(
            update_or_create(Individu, data,
                             unique_keys=['nom', 'prenoms']))

    def testException(self):
        self.assertRaisesMessage(
            Exception, '`conflict_handling` must be in CONFLICT_HANDLINGS.',
            lambda: update_or_create(Individu, self.data,
                                     conflict_handling='bad'))

    def testUniqueness(self):
        reference_pk = self.objects[0].pk
        for obj in self.objects[1:]:
            self.assertEqual(reference_pk, obj.pk)

    def testContent(self):
        last_object = self.objects[-1]
        for k, v_ref in self.data.items():
            v = getattr(last_object, k)
            if isinstance(v, Manager):
                self.assertQuerysetEqual(v.all(), map(repr, v_ref))
            else:
                self.assertEqual(v, v_ref)
