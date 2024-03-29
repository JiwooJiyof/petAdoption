from datetime import datetime
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.core.exceptions import PermissionDenied
from rest_framework.generics import (
    ListCreateAPIView,
    CreateAPIView,
    RetrieveUpdateDestroyAPIView,
    RetrieveDestroyAPIView,
)
from rest_framework.permissions import (IsAuthenticated, IsAuthenticatedOrReadOnly)
from rest_framework.pagination import PageNumberPagination

from applications.models import Application
from accounts.models import PetSeeker, PetShelter
from .models import ApplicationComment, ShelterComment
from .serializers import *
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.permissions import BasePermission

class CommentResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50

class CanViewApplicationPermission(BasePermission):
    def has_permission(self, request, view):
        author = request.user
        application = get_object_or_404(Application, pk=view.kwargs['application'])
        try:
            if author.shelter != application.shelter:
                return False
        except ObjectDoesNotExist:
            if author != application.applicant:
                return False
        return True

# Create your views here.
class ShelterCommentListCreateView(ListCreateAPIView):
    """
    Comments from users on a given shelter.

    - A GET request returns all comments and replies to those comments for
    the given shelter.

    - A POST request adds a new comment to the shelter if the
    current user is logged in, and is not the shelter.
    """
    serializer_class = ShelterCommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = CommentResultsSetPagination
    def perform_create(self, serializer):
        author = self.request.user
        shelter = get_object_or_404(PetShelter, pk=self.kwargs["shelter"])
        try:
            if author.shelter == shelter:
                raise PermissionDenied
        except ObjectDoesNotExist:
            pass
        serializer.save(author=author, shelter=shelter)

    def get_queryset(self):
        return ShelterComment.objects.all().filter(shelter=self.kwargs["shelter"]).order_by("-created_at")

class ApplicationCommentListCreateView(ListCreateAPIView):
    """Comments from users on a given application.

    - A GET request returns all comments on an application 

    - A POST request adds a new comment to the list of comments on the given application

    Requests are only permitted if the current user is the shelter receiving the application or the current
    user is the applicant.

    """
    serializer_class = ApplicationCommentSerializer
    permission_classes = [IsAuthenticated, CanViewApplicationPermission]
    pagination_class = CommentResultsSetPagination

    def perform_create(self, serializer):
        author = self.request.user
        application = get_object_or_404(Application, pk=self.kwargs['application'])
        application.last_update_time = datetime.now()
        application.save()
        serializer.save(author=author, application=application)

    def get_queryset(self):
        try:
            return ApplicationComment.objects.all().filter(application__shelter=self.request.user.shelter,
                                                           application=self.kwargs['application']).order_by("-created_at")
        except ObjectDoesNotExist:
            return ApplicationComment.objects.all().filter(application=self.kwargs['application'],
                                                           application__applicant=self.request.user).order_by("-created_at")

class ReplyCreateView(CreateAPIView):
    """Replies to a given comment

    - A POST request adds a new reply to a given shelter comment.

    Any logged in user can reply to a comment.
    """
    serializer_class = ReplySerializer
    permission_classes = [IsAuthenticated]
    def perform_create(self, serializer):
        author = self.request.user
        parent = get_object_or_404(ShelterComment, pk=self.kwargs["parent"])
        serializer.save(author=author, parent=parent)
