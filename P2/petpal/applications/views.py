from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Application
from .serializers import ApplicationSerializer
from pet_listing.models import PetListing
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from accounts.models import PetSeeker

# Taken from https://stackoverflow.com/questions/31785966/django-rest-framework-turn-on-pagination-on-a-viewset-like-modelviewset-pagina


class IsShelterPermission(IsAuthenticated):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.is_shelter


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 10


# Taken from https://b0uh.github.io/drf-viewset-permission-policy-per-method.html
class PermissionPolicyMixin:
    def check_permissions(self, request):
        try:
            # This line is heavily inspired from `APIView.dispatch`.
            # It returns the method associated with an endpoint.
            handler = getattr(self, request.method.lower())
        except AttributeError:
            handler = None

        if (
            handler
            and self.permission_classes_per_method
            and handler.__name__.upper() in self.permission_classes_per_method
        ):
            self.permission_classes = self.permission_classes_per_method.get(
                handler.__name__.upper()
            )
        super().check_permissions(request)

# permissions + users cant create if already have application


class ApplicationCreateView(CreateAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        pet_listing = get_object_or_404(
            PetListing, id=self.kwargs["pet_listing"]
        )

        # User can only create one application for a pet listing
        existing_application = Application.objects.filter(
            applicant=request.user,
            pet_listing=pet_listing
        ).first()

        if existing_application:
            return Response({"error": "You already have an application for this pet"}, status=status.HTTP_400_BAD_REQUEST)

        if pet_listing.status == "Available":
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(serializer.data)
        else:
            return Response({"error": "The selected pet is not available"}, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        applicant = self.request.user
        pet_listing = get_object_or_404(
            PetListing, id=self.kwargs["pet_listing"]
        )
        serializer.validated_data['applicant'] = applicant
        serializer.validated_data['pet_listing'] = pet_listing
        serializer.validated_data['shelter'] = applicant.shelter
        serializer.save()

# permissions


class ApplicationListView(ListAPIView):
    serializer_class = ApplicationSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status']
    ordering_fields = ['creation_time', 'last_update_time']
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        owner = self.request.user
        if owner.is_shelter:
            queryset = Application.objects.filter(shelter=owner.shelter)
        else:
            queryset = Application.objects.filter(applicant=owner)
        return queryset

# permissions


class ApplicationUpdateView(RetrieveUpdateAPIView):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        application = self.get_object()

        # if shelter, can update to Accepted or Rejected
        applicant = self.request.user
        if applicant.is_shelter:
            new_status = request.data.get('status', '')
            print(new_status)
            if new_status != "Accepted" and new_status != "Rejected":
                return Response({"error": "Choose between Accepted or Rejected"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                application.status = new_status
                application.save()

        # if applicant, can update to Withdraw
        else:
            new_status = request.data.get('status', '')
            if new_status != "WITHDRAW":
                return Response({"error": "Can only withdraw application"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                application.status = new_status
                application.save()

        # Return a success response
        return Response(
            self.get_serializer(application).data,
            status=status.HTTP_200_OK
        )
