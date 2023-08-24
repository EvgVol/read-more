from django.shortcuts import get_object_or_404
from rest_framework import (generics, authentication, decorators,
                            permissions, response, views, viewsets)

from courses.models.subject import Subject
from courses.models.course import Course
from courses.api.serializers import (SubjectSerializer, CourseSerializer,
                                     CourseWithContentsSerializer)
from courses.api.permissions import IsEnrolled


class SubjectListView(generics.ListAPIView):

    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer


class SubjectDetailView(generics.RetrieveAPIView):

    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer


class CourseViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    @decorators.action(detail=True,
                       methods=['post'],
                       authentication_classes=[
                           authentication.BasicAuthentication
                       ],
                       permission_classes=[permissions.IsAuthenticated])
    def enroll(self, request, *args, **kwargs):
        course = self.get_object()
        course.students.add(request.user)
        return response.Response({'enrolled': True})

    @decorators.action(detail=True,
            methods=['get'],
            serializer_class=CourseWithContentsSerializer,
            authentication_classes=[authentication.BasicAuthentication],
            permission_classes=[permissions.IsAuthenticated, IsEnrolled])
    def contents(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class CourseEnrollView(views.APIView):

    authentication_classes = [authentication.BasicAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk, format=None):
        course = get_object_or_404(Course, pk=pk)
        course.students.add(request.user)
        return response.Response({'enrolled': True})
