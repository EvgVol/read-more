from django.contrib import admin
from django.db import models
from django.forms import SelectMultiple
from django.utils.html import format_html

from courses.models import subject, course, module, advantage, technology
from .forms import CourseForm

@admin.register(advantage.Advantage)
class AdvantageAdmin(admin.ModelAdmin):
    
    list_display = ('image_tag','name',)
    
    def image_tag(self, obj):
        return format_html('<img src="{}" width="50" height="50" />'.format(obj.image.url))

    image_tag.short_description = 'Image'


@admin.register(technology.Technology)
class TechnologyAdmin(admin.ModelAdmin):
    
    list_display = ('image_tag','name',)
    
    def image_tag(self, obj):
        return format_html('<img src="{}" width="50" height="50" />'.format(obj.url))

    image_tag.short_description = 'Image'


@admin.register(subject.Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug']
    prepopulated_fields = {'slug': ('title',)}


class ModuleInLine(admin.StackedInline):
    model = module.Module


@admin.register(course.Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'created', 'complexity', 'description']
    list_filter = ['created', 'subject']
    search_fields = ['title', 'overview']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ModuleInLine]
    filter_horizontal = ('technologies', 'advantages')
    form = CourseForm
