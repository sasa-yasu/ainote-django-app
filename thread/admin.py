from django.contrib import admin
from .models import ThreadCategory, Thread

@admin.register(ThreadCategory)
class ThreadCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at', 'updated_at')
    search_fields = ('name', 'description')

@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_categories', 'created_at', 'updated_at')
    list_filter = ('categories',)  # カテゴリでフィルタリング可能
    search_fields = ('name', 'content', 'categories__name')  # カテゴリ名でも検索可能
    
    def get_categories(self, obj):
        return ", ".join([category.name for category in obj.categories.all()])
    get_categories.short_description = 'Categories'
