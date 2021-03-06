from __future__ import unicode_literals
from datetime import date
from django.db import models
from django.core.exceptions import ValidationError

# class Scheme(models.Model):
#     name = models.CharField(max_length=255)
#     description = models.CharField(max_length=255)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return unicode(self.name)

#     class Meta:
#         get_latest_by = 'created_at'


class Category(models.Model):
    #scheme = models.ForeignKey(Scheme,
    #    on_delete=models.DO_NOTHING)
    parent = models.ForeignKey('Category', 
        blank=True, null=True,
        related_name="subcategories",
        on_delete=models.DO_NOTHING)

    name = models.CharField(max_length=255)
    # in admin: prepopulated_fields = {"slug": ("name",)}
    index = models.PositiveIntegerField(null=True, blank=True)
    slug = models.SlugField("abbreviation", max_length=255)
    reference = models.CharField(max_length=255, unique=True)
    reference_verbose = models.CharField("directory", max_length=255, unique=True)
    allows_storage = models.BooleanField()
    description = models.TextField(
        blank=True, null=True)

    def make_path(self):
        if self.parent:
            return "%s/%s/" % (self.parent.path,  self.index)
        else:
            return "/%s" % self.slug

    def make_human_path(self):
        slug = self.slug if not self.index else "%s_%s" % (self.index, self.slug)
        return "%s/%s/" % ( self.parent.reference_verbose if self.parent else "",  slug)

    @classmethod
    def storage_categories(cls):
        return cls.objects.filter(allows_storage=True)

    def __str__(self):
        return self.reference_verbose

    def save(self, *args, **kwargs):
        self.reference = self.make_path()
        self.reference_verbose = self.make_human_path()
        super(Category, self).save(*args, **kwargs)

    def clean(self):
        if not self.index and self.parent:
            raise ValidationError('All subcategories should have index number')

        if self.index and not self.parent:
            raise ValidationError('Top categories should not have index number')

    class Meta():
        verbose_name_plural = "Categories"
        ordering = ("reference_verbose",)
        unique_together = (("index", "parent"),)


class StorageLocation(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.name


def storage_categories():
    #  https://djangosnippets.org/snippets/1968/
    cats = Category.storage_categories().values_list("id", flat=True)
    return {"id__in": cats } 


class Communication(models.Model):
    protocol = models.CharField(max_length=255, db_index=True, unique=True)
    protocol_verbose = models.CharField(max_length=255, db_index=True, unique=True)

    index = models.CharField(max_length=255, null=True, blank=True)
    category = models.ForeignKey(
        Category, limit_choices_to=storage_categories,
        on_delete=models.DO_NOTHING)
    subject = models.TextField()
    frm = models.CharField("from", max_length=255)
    to = models.CharField(max_length=255)
    #date = models.DateTimeField()

    submitted = models.DateTimeField(auto_now_add=True)
    is_incoming = models.BooleanField()

    storage = models.ForeignKey(StorageLocation,
        null=True, blank=True,
        help_text="Physical storage location",
        on_delete=models.DO_NOTHING)
    is_digital = models.BooleanField()
    metadata = models.TextField(blank=True, null=True)

    class Meta:
        get_latest_by = 'submitted'
        ordering = ("submitted",)
        verbose_name="Correspondence"
        verbose_name_plural="Correspondences"

    def get_last_id(self):
        current_year = date.today().year
        return current_year, Communication.objects.filter(submitted__year=current_year).count()

    def create_id(self):

        current_year, latest_id = self.get_last_id()
        return current_year, latest_id + 1

    def save(self, *args, **kwargs):
        if not self.id:
            # super(Communication, self).save(*args, **kwargs)
            self.index = "%s_%s" % self.create_id()
            self.protocol = "%s%s" % (self.category.reference, self.index)
            self.protocol_verbose = "%s%s" % (self.category.reference_verbose, self.index)

        super(Communication, self).save(*args, **kwargs)

    def clean(self):
        if not self.is_digital and not self.storage:
            raise ValidationError('Storage location must be set for physical correspondance')

        if self.is_digital and self.storage:
            raise ValidationError('Storage location does not apply for digital correspondance only for physical')

    @property
    def storage_dir(self):
        return "protocol%s" % self.protocol_verbose
        
    def __str__(self):
        return "%s %s" % (self.protocol, self.subject)


def get_storage_location(instance, filename):
        return "%s-%s" % (instance.communication.storage_dir, filename)


class Document(models.Model):
    communication = models.ForeignKey(
        Communication,
        on_delete=models.DO_NOTHING)
    message_id = models.CharField(max_length=255, blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    attachment = models.FileField(
        upload_to = get_storage_location,
        blank=True, null=True)
    body = models.TextField(blank=True, null=True)
    metadata = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.communication.protocol

    def clean(self):
        if not self.attachment and not self.body:
            raise ValidationError('File atachment must be set or "body" of the message')

    def save(self, *args, **kwargs):
        # TODO extract and save metadata as JSON

        super(Document, self).save(*args, **kwargs)


