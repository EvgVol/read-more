from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .forms import CourseForm
from courses.models.advantage import Advantage
from courses.models.technology import Technology
from courses.models.subject import Subject
from courses.models.module import Module
from courses.models.course import Course
from courses.models.card import Card
from courses.models.lessons import Lesson



@admin.register(Advantage)
class AdvantageAdmin(admin.ModelAdmin):
    
    list_display = ('image_tag','name',)
    
    def image_tag(self, obj):
        return format_html(
            '<img src="{}" width="50" height="50" />'
            .format(obj.image.url)
        )

    image_tag.short_description = 'Image'


@admin.register(Technology)
class TechnologyAdmin(admin.ModelAdmin):
    
    list_display = ('image_tag', 'name', 'hints')
    search_fields = ['name']
    
    def image_tag(self, obj):
        return format_html(
            '<img src="{}" width="50" height="50" />'
            .format(obj.url)
        )

    image_tag.short_description = 'Image'


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug']
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title',)


class LessonInline(admin.StackedInline):  
    model = Lesson
    extra = 2


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ['id','title']
    inlines = [LessonInline]



class ModuleInLine(admin.StackedInline):
    model = Module
    extra = 2


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['icon_course','title', 'subject', 'created',
                    'complexity', 'get_technologies', 'period',
                    'count_projects']
    list_filter = ['created', 'subject', 'load', 'technologies']
    search_fields = ['title', 'overview']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ModuleInLine]
    filter_horizontal = ('technologies', 'advantages')
    form = CourseForm

    @admin.display(description=_('technologies'))
    def get_technologies(self, obj):
        return ',\n '.join([ 
            f'{item.name}'
            for item in obj.technologies.all()])

    @admin.display(description=_('icon course'))
    def icon_course(self, obj):
        return format_html(
            '<img src="{}" width="100" height="70" />'
            .format(obj.image.url)
        )


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ['title', 'course']
