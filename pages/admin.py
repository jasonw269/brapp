from django.contrib import admin
from .models import GalleryImage, SiteContent


@admin.register(SiteContent)
class SiteContentAdmin(admin.ModelAdmin):
    list_display = ['label', 'key', 'updated_at']
    search_fields = ['key', 'label']
    readonly_fields = ['key', 'updated_at']

    def has_add_permission(self, request):
        return False  # Only edit existing entries, don't add raw keys

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ['title', 'order', 'uploaded_at']
    list_editable = ['order']
    exclude = ['uploaded_by']  # Set automatically on save

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)
