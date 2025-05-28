from django.contrib import admin
from .models import Letter

@admin.register(Letter)
class LetterAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'delivery_date', 'is_delivered', 'created_at')
    list_filter = ('is_delivered', 'delivery_date')
    search_fields = ('title', 'content', 'author__email')
    readonly_fields = ('created_at', 'uuid')
