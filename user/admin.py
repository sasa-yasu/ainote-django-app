from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from .models import Profile


class ProfileInline(admin.StackedInline):
    model = Profile
    max_num = 1
    can_delete = False


class CustomUserAdmin(DefaultUserAdmin):
    def get_inline_instances(self, request, obj=None):
        if obj:  # オブジェクトがある場合のみインラインを表示
            return [ProfileInline(self.model, self.admin_site)]
        return []

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
