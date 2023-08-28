from django.shortcuts import render, get_list_or_404
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required


@login_required
def course_chat_room(request, course_id):
    try:
        course = request.user.courses_joined.get(id=course_id)
    except:
        return HttpResponseForbidden()
    
    users_in_chat = course.students.all()
    return render(request,
                  'chat/room.html',
                  {'course': course, 'users_in_chat': users_in_chat})
