from django.contrib import admin

from .models import CustomUser, ClientProfile, FreelancerProfile

class ClientProfileInline(admin.StackedInline):
    model = ClientProfile
    can_delete = False
    extra = 0

class FreelancerProfileInline(admin.StackedInline):
    model = FreelancerProfile
    can_delete = False
    extra = 0 

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "role",
        "phone",
        "is_staff",
        "is_active",
        "date_joined",
    )

    list_filter = (
        "role",
        "is_staff",
        "is_active",
        "is_superuser",
        "date_joined",
    )

    search_fields = (
        "email",
        "phone",
    )

    ordering = (
        "email",
    )

    readonly_fields = (
        "last_login",
        "date_joined",
    )

    inlines = [
        ClientProfileInline,
        FreelancerProfileInline,
    ]

    fieldsets = (
        (
            "Authentication",
            {
                "fields": (
                    "email",
                    "username",
                    "password",
                )
            },
        ),
        (
            "Personal Information",
            {
                "fields": (
                    "phone",
                    "role",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            "Important Dates",
            {
                "fields": (
                    "last_login",
                    "date_joined",
                )
            },
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "role",
                    "phone",
                    "password1",
                    "password2",
                    "is_active",
                    "is_staff",
                ),
            },
        ),
    )

