from django.contrib import admin

from .models import Project

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['owner', 'title', 'status', 'budget', 'deadline', 'created_at', 'updated_at']
    list_filter = ['status', 'created_at', 'updated_at']
    search_fields = ['title', 'description', 'owner__email']
    raw_id_fields = ['owner']
