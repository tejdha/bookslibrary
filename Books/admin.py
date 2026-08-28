from django.contrib import admin
from .models import Book,Category, ActivityLog,Notificaton
from django.contrib.auth.admin import UserAdmin
from pypdf import PdfReader
# Register your models here.

# admin.site.register(Book)
admin.site.register(Category)
admin.site.register(ActivityLog)
admin.site.register(Notificaton)

from .cache_utils import invalidate_books_cache

# this entire code to not ask the pages field and calculate automatically 
# in admin panel coz it doesn't use form
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):

    readonly_fields = ['pages']

    def save_model(self, request, obj, form, change):

        if obj.pdf:
            reader = PdfReader(obj.pdf)
            obj.pages=len(reader.pages)
        super().save_model(request, obj, form, change)

        invalidate_books_cache()

    def delete_model(self, request, obj):
        return super().delete_model(request, obj)
        invalidate_books_cache()