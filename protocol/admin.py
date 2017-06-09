from django.contrib import admin

from .models import Category, Communication, Document, StorageLocation

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('reference_verbose', 'reference', 'name', 'allows_storage')
    readonly_fields = ('reference', 'reference_verbose', )
    prepopulated_fields = {'slug': ('name',), }
    fieldsets = (
        (None, {
            'fields': (
                ('parent', 'allows_storage'),
                ("index", "name", "slug"),
                ('reference', 'reference_verbose'),
                "description",
                
            )
        }),
    )

class DocumentInline(admin.StackedInline):
    model = Document
    readonly_fields = ('metadata', )
    extra = 1
    min_num = 1


class CommunicationAdmin(admin.ModelAdmin):
    list_display = ('protocol', 'submitted',  'subject', 'is_digital')
    search_fields = ("subject", 'frm', 'to', 'category__reference', 'category__reference_verbose', 'category__name')
    list_filter =  ('category', 'is_digital')
    readonly_fields = ('index', 'protocol', 'protocol_verbose', 'submitted', 'metadata')
    inlines = (DocumentInline, )

    fieldsets = (
        (None, {
            'fields': (
                ('category', 'index'),
                ('protocol', 'protocol_verbose'),
                ('is_incoming', 'submitted'),
                ('is_digital', 'storage'),
            )
        }),
        (None, {
            'fields': (
                'subject',
                ("frm", "to"),
                'metadata',
            )
        }),
    )


    # readonly_fields = ['user', 'transaction_type', 'transaction_date']
    # verbose_name = 'Transaction'
    # verbose_name_plural = 'Book history'


class DocumentAdmin(admin.ModelAdmin):
    list_display = ('communication', 'submitted_at')
    readonly_fields = ('metadata', 'submitted_at')
    raw_id_fields = ('communication',)
    
    # def save_model(self, request, obj, form, change):
    #         if getattr(obj, 'created_by', None) is None:
    #             obj.created_by = request.user
    #         obj.save()
admin.site.register(StorageLocation)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Communication, CommunicationAdmin)
admin.site.register(Document, DocumentAdmin)
# admin.site.register(Attachment)

