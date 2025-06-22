from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import NotFound, ValidationError, PermissionDenied
from rest_framework.views import APIView
from .models import (
    User, Agency, Project, ProjectHead, Branch, Outlet, UserOutlet,
    AirtelCombined, CokeCombined, BaimsCombined, KspcaCombined, SaffCombined,
    RedbullOutlet, TotalKenya, AppData, Ba, Backend, BaProject, ProjectAssoc,
    Containers, ContainerOptions, Coop, Coop2, FormSection, FormSubSection,
    InputGroup, InputOptions
)
from .serializers import (
    UserSerializer, UserListSerializer,
    AgencySerializer, AgencyListSerializer,
    ProjectSerializer, ProjectListSerializer,
    ProjectHeadSerializer, ProjectHeadListSerializer,
    BranchSerializer, BranchListSerializer,
    OutletSerializer, OutletListSerializer,
    UserOutletSerializer, UserOutletListSerializer,
    AirtelCombinedSerializer, AirtelCombinedListSerializer,
    CokeCombinedSerializer, CokeCombinedListSerializer,
    BaimsCombinedSerializer, BaimsCombinedListSerializer,
    KspcaCombinedSerializer, KspcaCombinedListSerializer,
    SaffCombinedSerializer, SaffCombinedListSerializer,
    RedbullOutletSerializer, RedbullOutletListSerializer,
    TotalKenyaSerializer, TotalKenyaListSerializer,
    AppDataSerializer, AppDataListSerializer,
    BaSerializer, BaListSerializer,
    BackendSerializer, BackendListSerializer,
    BaProjectSerializer, BaProjectListSerializer,
    ProjectAssocSerializer, ProjectAssocListSerializer,
    ContainersSerializer, ContainersListSerializer,
    ContainerOptionsSerializer, ContainerOptionsListSerializer,
    CoopSerializer, CoopListSerializer,
    Coop2Serializer, Coop2ListSerializer,
    FormSectionSerializer, FormSectionListSerializer,
    FormSubSectionSerializer, FormSubSectionListSerializer,
    InputGroupSerializer, InputGroupListSerializer,
    InputOptionsSerializer, InputOptionsListSerializer
)
from django.db import models
from django.contrib.auth.hashers import check_password
from rest_framework.authtoken.models import Token

# Custom exception handler for better error messages
def custom_exception_handler(exc, context):
    """Custom exception handler to provide better error messages"""
    if isinstance(exc, NotFound):
        return Response({
            'success': False,
            'message': 'The requested resource was not found',
            'data': {
                'errors': 'Resource not found',
                'suggestion': 'Please check the URL and resource ID'
            }
        }, status=status.HTTP_404_NOT_FOUND)
    
    elif isinstance(exc, ValidationError):
        return Response({
            'success': False,
            'message': 'Invalid data provided',
            'data': {
                'errors': exc.detail,
                'suggestion': 'Please check the data format and required fields'
            }
        }, status=status.HTTP_400_BAD_REQUEST)
    
    elif isinstance(exc, PermissionDenied):
        return Response({
            'success': False,
            'message': 'You do not have permission to perform this action',
            'data': {
                'errors': 'Permission denied',
                'suggestion': 'Please check your authentication and permissions'
            }
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Handle unsupported media type error
    elif hasattr(exc, 'status_code') and exc.status_code == 415:
        return Response({
            'success': False,
            'message': 'Unsupported media type in request',
            'data': {
                'errors': 'Content-Type header is incorrect',
                'suggestion': 'Please set Content-Type header to "application/json"',
                'example': {
                    'headers': {
                        'Content-Type': 'application/json'
                    },
                    'note': 'Make sure your request body is valid JSON format'
                }
            }
        }, status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
    
    # Call the default exception handler for other exceptions
    from rest_framework.views import exception_handler
    response = exception_handler(exc, context)
    
    if response is not None:
        response.data = {
            'success': False,
            'message': 'An error occurred while processing your request',
            'data': {
                'errors': response.data,
                'suggestion': 'Please try again or contact support if the issue persists'
            }
        }
    
    return response

# Generic BaseViewSet to be inherited by other viewsets
class BaseViewSet(viewsets.ModelViewSet):
    """Base ViewSet with standardized response format"""
    
    def get_object(self):
        """Override to provide better error messages"""
        try:
            return super().get_object()
        except ObjectDoesNotExist:
            model_name = self.queryset.model.__name__
            item_id = self.kwargs.get('pk')
            raise ObjectDoesNotExist(f"{model_name} with ID '{item_id}' does not exist.")
    
    def list(self, request, *args, **kwargs):
        """List all items"""
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response({
                'success': True,
                'message': f'Successfully retrieved {queryset.count()} items',
                'data': {
                    'items': serializer.data,
                    'count': queryset.count()
                }
            })
        except Exception as e:
            return Response({
                'success': False,
                'message': 'An error occurred while retrieving items',
                'data': {'errors': str(e)}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def create(self, request, *args, **kwargs):
        """Create a new item"""
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                item = serializer.save()
                return Response({
                    'success': True,
                    'message': 'Item created successfully',
                    'data': {'item': self.get_serializer(item).data}
                }, status=status.HTTP_201_CREATED)
            return Response({
                'success': False,
                'message': 'Invalid data provided',
                'data': {'errors': serializer.errors}
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'success': False,
                'message': 'An error occurred while creating the item',
                'data': {'errors': str(e)}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def retrieve(self, request, *args, **kwargs):
        """Retrieve a specific item by ID"""
        try:
            item = self.get_object()
            serializer = self.get_serializer(item)
            return Response({
                'success': True,
                'message': 'Item retrieved successfully',
                'data': {'item': serializer.data}
            })
        except ObjectDoesNotExist as e:
            return Response({
                'success': False,
                'message': str(e),
                'data': {'errors': 'Item not found'}
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'message': 'An error occurred while retrieving the item',
                'data': {'errors': str(e)}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def update(self, request, *args, **kwargs):
        """Update an item (full update)"""
        try:
            item = self.get_object()
            serializer = self.get_serializer(item, data=request.data)
            if serializer.is_valid():
                item = serializer.save()
                return Response({
                    'success': True,
                    'message': 'Item updated successfully',
                    'data': {'item': self.get_serializer(item).data}
                })
            return Response({
                'success': False,
                'message': 'Invalid data provided',
                'data': {'errors': serializer.errors}
            }, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist as e:
            return Response({
                'success': False,
                'message': str(e),
                'data': {'errors': 'Item not found'}
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'message': 'An error occurred while updating the item',
                'data': {'errors': str(e)}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def partial_update(self, request, *args, **kwargs):
        """Update an item (partial update)"""
        try:
            item = self.get_object()
            serializer = self.get_serializer(item, data=request.data, partial=True)
            if serializer.is_valid():
                item = serializer.save()
                return Response({
                    'success': True,
                    'message': 'Item updated successfully',
                    'data': {'item': self.get_serializer(item).data}
                })
            return Response({
                'success': False,
                'message': 'Invalid data provided',
                'data': {'errors': serializer.errors}
            }, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist as e:
            return Response({
                'success': False,
                'message': str(e),
                'data': {'errors': 'Item not found'}
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'message': 'An error occurred while updating the item',
                'data': {'errors': str(e)}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def destroy(self, request, *args, **kwargs):
        """Delete an item"""
        try:
            item = self.get_object()
            item.delete()
            return Response({
                'success': True,
                'message': 'Item deleted successfully',
                'data': {}
            }, status=status.HTTP_200_OK)
        except ObjectDoesNotExist as e:
            return Response({
                'success': False,
                'message': str(e),
                'data': {'errors': 'Item not found'}
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'message': 'An error occurred while deleting the item',
                'data': {'errors': str(e)}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Create your views here.

class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for User model with full CRUD operations
    
    list: Get all users (without passwords)
    create: Create a new user
    retrieve: Get a specific user by ID
    update: Update a user (PUT - full update)
    partial_update: Update a user (PATCH - partial update)
    destroy: Delete a user
    """
    
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.action == 'list':
            return UserListSerializer
        return UserSerializer
    
    def get_object(self):
        """Override to provide better error messages"""
        try:
            return super().get_object()
        except ObjectDoesNotExist:
            user_id = self.kwargs.get('pk')
            raise ObjectDoesNotExist(f"User with ID '{user_id}' does not exist. Please check the user ID and try again.")
    
    def list(self, request, *args, **kwargs):
        """Get all users with optional filtering"""
        try:
            queryset = self.get_queryset()
            
            # Filter by region if provided
            region = request.query_params.get('region', None)
            if region:
                queryset = queryset.filter(region=region)
            
            # Filter by active status if provided
            active_status = request.query_params.get('active_status', None)
            if active_status is not None:
                try:
                    active_status = int(active_status)
                    queryset = queryset.filter(active_status=active_status)
                except ValueError:
                    return Response({
                        'success': False,
                        'message': 'Invalid active_status parameter. Must be 0 or 1.',
                        'data': {
                            'errors': {'active_status': 'Must be 0 or 1'}
                        }
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Search by name or username
            search = request.query_params.get('search', None)
            if search:
                queryset = queryset.filter(
                    models.Q(name__icontains=search) | 
                    models.Q(username__icontains=search)
                )
            
            serializer = self.get_serializer(queryset, many=True)
            return Response({
                'success': True,
                'message': f'Successfully retrieved {queryset.count()} users',
                'data': {
                    'users': serializer.data,
                    'count': queryset.count()
                }
            })
        except Exception as e:
            return Response({
                'success': False,
                'message': 'An error occurred while retrieving users',
                'data': {
                    'errors': str(e)
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def create(self, request, *args, **kwargs):
        """Create a new user"""
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                return Response({
                    'success': True,
                    'message': 'User created successfully',
                    'data': {
                        'user': UserListSerializer(user).data
                    }
                }, status=status.HTTP_201_CREATED)
            return Response({
                'success': False,
                'message': 'Invalid data provided. Please check the required fields.',
                'data': {
                    'errors': serializer.errors,
                    'required_fields': ['name', 'username', 'password', 'region'],
                    'optional_fields': ['active_status', 'place_holder']
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'success': False,
                'message': 'An error occurred while creating the user',
                'data': {
                    'errors': str(e)
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def retrieve(self, request, *args, **kwargs):
        """Get a specific user by ID"""
        try:
            user = self.get_object()
            serializer = UserListSerializer(user)
            return Response({
                'success': True,
                'message': 'User retrieved successfully',
                'data': {
                    'user': serializer.data
                }
            })
        except ObjectDoesNotExist as e:
            return Response({
                'success': False,
                'message': str(e),
                'data': {
                    'errors': 'User not found',
                    'suggestion': 'Please check the user ID and try again'
                }
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'message': 'An error occurred while retrieving the user',
                'data': {
                    'errors': str(e)
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def update(self, request, *args, **kwargs):
        """Update a user (full update)"""
        try:
            user = self.get_object()
            serializer = self.get_serializer(user, data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                return Response({
                    'success': True,
                    'message': 'User updated successfully',
                    'data': {
                        'user': UserListSerializer(user).data
                    }
                })
            return Response({
                'success': False,
                'message': 'Invalid data provided. Please check the required fields.',
                'data': {
                    'errors': serializer.errors,
                    'required_fields': ['name', 'username', 'password', 'region'],
                    'optional_fields': ['active_status', 'place_holder']
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist as e:
            return Response({
                'success': False,
                'message': str(e),
                'data': {
                    'errors': 'User not found',
                    'suggestion': 'Please check the user ID and try again'
                }
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'message': 'An error occurred while updating the user',
                'data': {
                    'errors': str(e)
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def partial_update(self, request, *args, **kwargs):
        """Update a user (partial update)"""
        try:
            user = self.get_object()
            serializer = self.get_serializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                user = serializer.save()
                return Response({
                    'success': True,
                    'message': 'User updated successfully',
                    'data': {
                        'user': UserListSerializer(user).data
                    }
                })
            return Response({
                'success': False,
                'message': 'Invalid data provided. Please check the field values.',
                'data': {
                    'errors': serializer.errors,
                    'available_fields': ['name', 'username', 'password', 'region', 'active_status', 'place_holder']
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist as e:
            return Response({
                'success': False,
                'message': str(e),
                'data': {
                    'errors': 'User not found',
                    'suggestion': 'Please check the user ID and try again'
                }
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'message': 'An error occurred while updating the user',
                'data': {
                    'errors': str(e)
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def destroy(self, request, *args, **kwargs):
        """Delete a user"""
        try:
            user = self.get_object()
            user_name = user.name
            user.delete()
            return Response({
                'success': True,
                'message': f'User "{user_name}" deleted successfully',
                'data': {}
            }, status=status.HTTP_200_OK)
        except ObjectDoesNotExist as e:
            return Response({
                'success': False,
                'message': str(e),
                'data': {
                    'errors': 'User not found',
                    'suggestion': 'Please check the user ID and try again'
                }
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'message': 'An error occurred while deleting the user',
                'data': {
                    'errors': str(e)
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def regions(self, request):
        """Get all unique regions"""
        try:
            regions = User.objects.values_list('region', flat=True).distinct()
            return Response({
                'success': True,
                'message': f'Successfully retrieved {len(regions)} unique regions',
                'data': {
                    'regions': list(regions)
                }
            })
        except Exception as e:
            return Response({
                'success': False,
                'message': 'An error occurred while retrieving regions',
                'data': {
                    'errors': str(e)
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def toggle_status(self, request, pk=None):
        """Toggle user active status"""
        try:
            user = self.get_object()
            old_status = user.active_status
            user.active_status = 0 if user.active_status == 1 else 1
            user.save()
            status_text = "active" if user.active_status == 1 else "inactive"
            return Response({
                'success': True,
                'message': f'User status changed from {"active" if old_status == 1 else "inactive"} to {status_text}',
                'data': {
                    'user': UserListSerializer(user).data
                }
            })
        except ObjectDoesNotExist as e:
            return Response({
                'success': False,
                'message': str(e),
                'data': {
                    'errors': 'User not found',
                    'suggestion': 'Please check the user ID and try again'
                }
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'message': 'An error occurred while toggling user status',
                'data': {
                    'errors': str(e)
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get user statistics"""
        try:
            total_users = User.objects.count()
            active_users = User.objects.filter(active_status=1).count()
            inactive_users = User.objects.filter(active_status=0).count()
            
            return Response({
                'success': True,
                'message': 'User statistics retrieved successfully',
                'data': {
                    'statistics': {
                        'total_users': total_users,
                        'active_users': active_users,
                        'inactive_users': inactive_users
                    }
                }
            })
        except Exception as e:
            return Response({
                'success': False,
                'message': 'An error occurred while retrieving user statistics',
                'data': {
                    'errors': str(e)
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def ids(self, request):
        """Get list of user IDs and names for reference"""
        try:
            users = User.objects.values('id', 'name', 'username', 'active_status').order_by('id')
            return Response({
                'success': True,
                'message': f'Successfully retrieved {len(users)} user IDs',
                'data': {
                    'users': list(users),
                    'count': len(users),
                    'note': 'Use these IDs for GET, PUT, PATCH, or DELETE operations on specific users'
                }
            })
        except Exception as e:
            return Response({
                'success': False,
                'message': 'An error occurred while retrieving user IDs',
                'data': {
                    'errors': str(e)
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# New ViewSets for all other models

class AgencyViewSet(BaseViewSet):
    """ViewSet for Agency model"""
    queryset = Agency.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return AgencyListSerializer
        return AgencySerializer

class ProjectViewSet(BaseViewSet):
    """ViewSet for Project model"""
    queryset = Project.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and hasattr(user, 'agency') and user.agency:
            return Project.objects.filter(company=user.agency.id)
        return Project.objects.none()

    def get_serializer_class(self):
        if self.action == 'list':
            return ProjectListSerializer
        return ProjectSerializer

    @action(detail=True, methods=['get'], url_path='view-form')
    def view_form(self, request, pk=None):
        """
        Get a specific project (form) and all its associated fields.
        This replicates the functionality of VIEW-FORM.php.
        """
        try:
            project = self.get_object()
            
            # Get all associated form fields
            form_fields = ProjectAssoc.objects.filter(project=project.id).order_by('rank')
            
            project_serializer = self.get_serializer(project)
            fields_serializer = ProjectAssocSerializer(form_fields, many=True)
            
            response_data = {
                'success': True,
                'message': 'Form structure retrieved successfully',
                'data': {
                    'form_details': project_serializer.data,
                    'form_fields': fields_serializer.data
                }
            }
            
            return Response(response_data)
            
        except ObjectDoesNotExist:
            return Response({
                'success': False,
                'message': f"Project with ID '{pk}' not found.",
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'message': 'An error occurred while retrieving the form structure.',
                'data': {'errors': str(e)}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ProjectHeadViewSet(BaseViewSet):
    """ViewSet for ProjectHead model"""
    queryset = ProjectHead.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ProjectHeadListSerializer
        return ProjectHeadSerializer

class BranchViewSet(BaseViewSet):
    """ViewSet for Branch model"""
    queryset = Branch.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return BranchListSerializer
        return BranchSerializer

class OutletViewSet(BaseViewSet):
    """ViewSet for Outlet model"""
    queryset = Outlet.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return OutletListSerializer
        return OutletSerializer

class UserOutletViewSet(BaseViewSet):
    """ViewSet for UserOutlet model"""
    queryset = UserOutlet.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return UserOutletListSerializer
        return UserOutletSerializer


# Data Collection ViewSets

class AirtelCombinedViewSet(BaseViewSet):
    """ViewSet for AirtelCombined model"""
    queryset = AirtelCombined.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return AirtelCombinedListSerializer
        return AirtelCombinedSerializer

class CokeCombinedViewSet(BaseViewSet):
    """ViewSet for CokeCombined model"""
    queryset = CokeCombined.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CokeCombinedListSerializer
        return CokeCombinedSerializer

class BaimsCombinedViewSet(BaseViewSet):
    """ViewSet for BaimsCombined model"""
    queryset = BaimsCombined.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return BaimsCombinedListSerializer
        return BaimsCombinedSerializer

class KspcaCombinedViewSet(BaseViewSet):
    """ViewSet for KspcaCombined model"""
    queryset = KspcaCombined.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return KspcaCombinedListSerializer
        return KspcaCombinedSerializer

class SaffCombinedViewSet(BaseViewSet):
    """ViewSet for SaffCombined model"""
    queryset = SaffCombined.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return SaffCombinedListSerializer
        return SaffCombinedSerializer

class RedbullOutletViewSet(BaseViewSet):
    """ViewSet for RedbullOutlet model"""
    queryset = RedbullOutlet.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return RedbullOutletListSerializer
        return RedbullOutletSerializer

class TotalKenyaViewSet(BaseViewSet):
    """ViewSet for TotalKenya model"""
    queryset = TotalKenya.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return TotalKenyaListSerializer
        return TotalKenyaSerializer

class AppDataViewSet(BaseViewSet):
    """ViewSet for AppData model"""
    queryset = AppData.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return AppDataListSerializer
        return AppDataSerializer

class BaViewSet(BaseViewSet):
    """ViewSet for Ba model"""
    queryset = Ba.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return BaListSerializer
        return BaSerializer

class BackendViewSet(BaseViewSet):
    """ViewSet for Backend model"""
    queryset = Backend.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return BackendListSerializer
        return BackendSerializer

class BaProjectViewSet(BaseViewSet):
    """ViewSet for BaProject model"""
    queryset = BaProject.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return BaProjectListSerializer
        return BaProjectSerializer

class ProjectAssocViewSet(BaseViewSet):
    """ViewSet for ProjectAssoc model"""
    queryset = ProjectAssoc.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ProjectAssocListSerializer
        return ProjectAssocSerializer

class ContainersViewSet(BaseViewSet):
    """ViewSet for Containers model"""
    queryset = Containers.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ContainersListSerializer
        return ContainersSerializer

class ContainerOptionsViewSet(BaseViewSet):
    """ViewSet for ContainerOptions model"""
    queryset = ContainerOptions.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ContainerOptionsListSerializer
        return ContainerOptionsSerializer

class CoopViewSet(BaseViewSet):
    """ViewSet for Coop model"""
    queryset = Coop.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CoopListSerializer
        return CoopSerializer

class Coop2ViewSet(BaseViewSet):
    """ViewSet for Coop2 model"""
    queryset = Coop2.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return Coop2ListSerializer
        return Coop2Serializer

class FormSectionViewSet(BaseViewSet):
    """ViewSet for FormSection model"""
    queryset = FormSection.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return FormSectionListSerializer
        return FormSectionSerializer

class FormSubSectionViewSet(BaseViewSet):
    """ViewSet for FormSubSection model"""
    queryset = FormSubSection.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return FormSubSectionListSerializer
        return FormSubSectionSerializer

class InputGroupViewSet(BaseViewSet):
    """ViewSet for InputGroup model"""
    queryset = InputGroup.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return InputGroupListSerializer
        return InputGroupSerializer

class InputOptionsViewSet(BaseViewSet):
    """ViewSet for InputOptions model"""
    queryset = InputOptions.objects.all()
    
    def get_serializer_class(self):
        return InputOptionsListSerializer if self.action == 'list' else InputOptionsSerializer

class LoginView(APIView):
    """
    Custom login view to authenticate a User and return a token.
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({
                'success': False,
                'message': 'Username and password are required'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)

        # For a production system, you should use a secure password hashing mechanism
        # like Django's default password hashing.
        # Assuming plain text passwords for now as in the original User model.
        if user.password != password:
            return Response({
                'success': False,
                'message': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_active:
            return Response({
                'success': False,
                'message': 'User account is inactive'
            }, status=status.HTTP_403_FORBIDDEN)

        token, created = Token.objects.get_or_create(user_id=user.pk)

        user_data = UserSerializer(user).data

        return Response({
            'success': True,
            'message': 'Login successful',
            'data': {
                'token': token.key,
                'user': user_data
            }
        })
