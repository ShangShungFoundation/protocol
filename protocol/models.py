from __future__ import unicode_literals

from django.db import models


class Scheme(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    date_add = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return unicode(self.name)


class Category(models.Model):
    scheme = models.ForeignKey(Scheme)
    parent = models.ForeignKey('Category', blank=True, null=True)

    name = models.CharField(max_length=255)
    # in admin: prepopulated_fields = {"slug": ("name",)}
    slug = models.SlugField(max_length=255)
    description = models.CharField(max_length=255)

    def get_current_scheme(self):
        return Scheme.objects.latest()

    def path(self):
        return u"%s/%s" % ( self.parent.slug if self.parent else "",  self.slug)

    @classmethod
    def get_leave_categories(cls):
        cats = [c for c in cls.objects.all()]
        for c in cats:
            if c.parent in cats:
                del cats[c]
        return cats

    def __unicode__(self):
        return unicode(self.name)


class Communication(models.Model):
    reference = models.CharField(
        max_length=255, index_db=True, unique=True)
    category = models.ForeignKey(Category)
    sender = models.CharField(max_length=255)
    subject = models.TextField()
    submitted = models.DateTimeField(auto_now_add=True)
    is_incoming = models.BooleanField()
    location = models.CharField(
        max_length=255, blank=True, null=True,
        help_text="indicate storage location for ordinary (physical) communications")

    def __unicode__(self):
        return u"%s %s %s" % (self.submitted, self.reference, self.subject)


class Message:
    communication = models.ForeignKey(Communication)
    body = models.BlobField()

    def __unicode__(self):
        return self.title


class Attachments:
    message = models.ForeignKey(Message)
    attachment = models.FileField(upload_to = self.get_storage_location())

    def get_storage_location(self):
        return u"%s" % (self.message.communication.path)

    def __unicode__(self):
        return self.title

