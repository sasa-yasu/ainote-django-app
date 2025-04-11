from django.contrib import admin
from .models import FindMe, FindMeImage

class FindMeImageInline(admin.TabularInline):
    model = FindMeImage
    extra = 1

@admin.register(FindMe)
class FindMeAdmin(admin.ModelAdmin):
    inlines = [FindMeImageInline]