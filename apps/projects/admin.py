from django.contrib import admin

from .models import Project, Proposal

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['owner', 'title', 'status', 'budget', 'deadline', 'created_at', 'updated_at']
    list_filter = ['status', 'created_at', 'updated_at']
    search_fields = ['title', 'description', 'owner__email']
    raw_id_fields = ['owner']

@admin.register(Proposal)
class ProposalAdmin(admin.ModelAdmin):
    list_display = ['project', 'freelancer', 'bid_amount', 'status', 'created_at', 'updated_at']
    list_filter = ['status']
    search_fields = ['project__title', 'freelancer__email']
    raw_id_fields = ['project', 'freelancer']
    readonly_fields = ['created_at', 'updated_at']