from django.views.generic.base import View
from django.views.generic.edit import DeleteView
from courses.views.mixins import OwnerCourseMixin
from django.shortcuts import redirect, get_object_or_404


from courses.models.content import Content


class CourseDeleteView(OwnerCourseMixin, DeleteView):
    """A view for deleting an existing course."""

    template_name = 'courses/manage/course/delete.html'
    permission_required = 'courses.delete_course'


class ContentDeleteView(View):
    def post(self, request, id):
        content_id = get_object_or_404(Content,
                                       id=id,
                                       module__course__owner=request.user)
        module = content_id.module
        content_id.item.delete()
        content_id.delete()
        return redirect('courses:content_list', module.id)
