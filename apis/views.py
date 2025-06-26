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
    InputGroup, InputOptions, AuthToken, UAdmin, AdminAuthToken, BaAuthToken
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
    InputOptionsSerializer, InputOptionsListSerializer,
    UAdminSerializer
)
from django.db import models
from django.contrib.auth.hashers import check_password
from rest_framework.authtoken.models import Token
from .authentication import TokenAuthentication, AdminTokenAuthentication, BaTokenAuthentication
from datetime import date, timedelta

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
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication, AdminTokenAuthentication, BaTokenAuthentication]
    
    def get_queryset(self):
        user = self.request.user

        if isinstance(user, UAdmin):
            return Agency.objects.filter(admins=user)

        if isinstance(user, Ba):
            if user.company:
                return Agency.objects.filter(id=user.company)
            return Agency.objects.none()

        if hasattr(user, 'agency') and user.agency:
            return Agency.objects.filter(id=user.agency.id)

        return Agency.objects.none()

    def get_serializer_class(self):
        if self.action == 'list':
            return AgencyListSerializer
        return AgencySerializer

class ProjectViewSet(BaseViewSet):
    """ViewSet for Project model"""
    queryset = Project.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication, AdminTokenAuthentication, BaTokenAuthentication]

    def get_queryset(self):
        user = self.request.user
        
        if isinstance(user, UAdmin):
            agency_ids = user.agencies.values_list('id', flat=True)
            return Project.objects.filter(company__in=agency_ids)

        if isinstance(user, Ba):
            project_ids = BaProject.objects.filter(ba_id=user.id).values_list('project_id', flat=True)
            return Project.objects.filter(id__in=project_ids)

        if hasattr(user, 'agency') and user.agency:
            return Project.objects.filter(company=user.agency.id)
            
        return Project.objects.none()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ProjectListSerializer
        return ProjectSerializer

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        user = request.user
        company_id = data.get('company')
        if not company_id:
            if isinstance(user, UAdmin):
                agencies = user.agencies.all()
                if agencies.count() == 0:
                    return Response({"success": False, "message": "Admin user is not associated with any company."}, status=status.HTTP_403_FORBIDDEN)
                if agencies.count() == 1:
                    company_id = agencies.first().id
                else:
                    return Response({"success": False, "message": "Admin with multiple companies must specify a 'company' ID."}, status=status.HTTP_400_BAD_REQUEST)
                data['company'] = company_id
            else:
                return Response({"success": False, "message": "You must specify a company."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({
            'success': True,
            'message': 'Item created successfully',
            'data': {'item': serializer.data}
        }, status=status.HTTP_201_CREATED, headers=headers)

    def retrieve(self, request, *args, **kwargs):
        """
        Get a specific project (form) and all its associated fields.
        This now matches the structure of the view_form action.
        """
        return super().retrieve(request, *args, **kwargs)

class ProjectHeadViewSet(BaseViewSet):
    """ViewSet for ProjectHead model"""
    queryset = ProjectHead.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication, AdminTokenAuthentication, BaTokenAuthentication]
    
    def get_queryset(self):
        user = self.request.user
        if isinstance(user, UAdmin):
            agency_ids = user.agencies.values_list('id', flat=True)
            return ProjectHead.objects.filter(company__in=agency_ids)
        allowed_agency_ids = []
        if isinstance(user, Ba):
            allowed_agency_ids = [user.company] if user.company else []
        elif hasattr(user, 'agency') and user.agency:
            allowed_agency_ids = [user.agency.id]
        return ProjectHead.objects.filter(company__in=allowed_agency_ids)

    def get_serializer_class(self):
        if self.action == 'list':
            return ProjectHeadListSerializer
        return ProjectHeadSerializer

    def create(self, request, *args, **kwargs):
        """
        Create a new ProjectHead.
        The company_id is inferred from the user token if possible.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        company_id_from_request = request.data.get('company')
        company_id = None

        if isinstance(user, UAdmin):
            agencies = user.agencies.all()
            if agencies.count() == 0:
                return Response({"success": False, "message": "Admin user is not associated with any company."}, status=status.HTTP_403_FORBIDDEN)
            
            if not company_id_from_request:
                if agencies.count() == 1:
                    company_id = agencies.first().id
                else:
                    return Response({"success": False, "message": "Admin with multiple companies must specify a 'company' ID."}, status=status.HTTP_400_BAD_REQUEST)
            else:
                company_id = company_id_from_request

            allowed_company_ids = agencies.values_list('id', flat=True)
            if int(company_id) not in allowed_company_ids:
                return Response({"success": False, "message": "You do not have permission for this company."}, status=status.HTTP_403_FORBIDDEN)

        elif isinstance(user, Ba):
            if not user.company:
                 return Response({"success": False, "message": "BA user is not associated with any company."}, status=status.HTTP_403_FORBIDDEN)
            company_id = user.company
        
        elif hasattr(user, 'agency') and user.agency:
            company_id = user.agency.id
        
        else:
            return Response({"success": False, "message": "Could not determine company from user token."}, status=status.HTTP_400_BAD_REQUEST)

        project_head = serializer.save(company=company_id)
        
        return Response({
            'success': True,
            'message': 'Project Head created successfully.',
            'data': self.get_serializer(project_head).data
        }, status=status.HTTP_201_CREATED)

    @action(methods=['put', 'patch'], detail=False, url_path='update')
    def update_by_body(self, request):
        """
        Update a ProjectHead by ID provided in the request body (no ID in URL).
        """
        user = request.user
        project_head_id = request.data.get('id')
        if not project_head_id:
            return Response({'success': False, 'message': 'ProjectHead ID is required.'}, status=400)
        try:
            project_head = ProjectHead.objects.get(id=project_head_id)
        except ProjectHead.DoesNotExist:
            return Response({'success': False, 'message': 'ProjectHead not found.'}, status=404)
        # Permission check
        if isinstance(user, UAdmin):
            allowed_agency_ids = user.agencies.values_list('id', flat=True)
            if project_head.company not in allowed_agency_ids:
                return Response({'success': False, 'message': 'You do not have permission to update this ProjectHead.'}, status=403)
        elif isinstance(user, Ba):
            if user.company != project_head.company:
                return Response({'success': False, 'message': 'You do not have permission to update this ProjectHead.'}, status=403)
        else:
            return Response({'success': False, 'message': 'Only admins and BAs can update ProjectHeads.'}, status=403)
        serializer = ProjectHeadSerializer(project_head, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'message': 'ProjectHead updated successfully.', 'data': serializer.data})
        return Response({'success': False, 'message': 'Invalid data.', 'errors': serializer.errors}, status=400)

    @action(methods=['delete'], detail=False, url_path='delete')
    def delete_by_body(self, request):
        """
        Delete a ProjectHead by ID provided in the request body.
        """
        user = request.user
        project_head_id = request.data.get('id')
        if not project_head_id:
            return Response({'success': False, 'message': 'ProjectHead ID is required.'}, status=400)
        try:
            project_head = ProjectHead.objects.get(id=project_head_id)
        except ProjectHead.DoesNotExist:
            return Response({'success': False, 'message': 'ProjectHead not found.'}, status=404)
        # Permission check
        if isinstance(user, UAdmin):
            allowed_agency_ids = user.agencies.values_list('id', flat=True)
            if project_head.company not in allowed_agency_ids:
                return Response({'success': False, 'message': 'You do not have permission to delete this ProjectHead.'}, status=403)
        elif isinstance(user, Ba):
            if user.company != project_head.company:
                return Response({'success': False, 'message': 'You do not have permission to delete this ProjectHead.'}, status=403)
        else:
            return Response({'success': False, 'message': 'Only admins and BAs can delete ProjectHeads.'}, status=403)
        project_head.delete()
        return Response({'success': True, 'message': 'ProjectHead deleted successfully.'}, status=200)

class BranchViewSet(BaseViewSet):
    """ViewSet for Branch model"""
    queryset = Branch.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication, AdminTokenAuthentication, BaTokenAuthentication]
    
    def get_queryset(self):
        # TODO: The Branch model is not linked to a company/agency.
        # This currently returns all branches to any authenticated user.
        # A schema change is required to filter this securely.
        return Branch.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return BranchListSerializer
        return BranchSerializer

class OutletViewSet(BaseViewSet):
    """ViewSet for Outlet model"""
    queryset = Outlet.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication, AdminTokenAuthentication, BaTokenAuthentication]
    
    def get_queryset(self):
        user = self.request.user
        
        if isinstance(user, UAdmin):
            agency_ids = user.agencies.values_list('id', flat=True)
            user_ids = User.objects.filter(agency_id__in=agency_ids).values_list('id', flat=True)
            outlet_ids = UserOutlet.objects.filter(user__in=user_ids).values_list('outlet', flat=True)
            return Outlet.objects.filter(id__in=outlet_ids)

        if isinstance(user, Ba) and user.company:
            # Find users in the same agency as the BA
            user_ids = User.objects.filter(agency_id=user.company).values_list('id', flat=True)
            # Find outlets assigned to those users
            outlet_ids = UserOutlet.objects.filter(user__in=user_ids).values_list('outlet', flat=True)
            return Outlet.objects.filter(id__in=outlet_ids)

        if isinstance(user, User):
             outlet_ids = UserOutlet.objects.filter(user=user.id).values_list('outlet', flat=True)
             return Outlet.objects.filter(id__in=outlet_ids)
        
        return Outlet.objects.none()

    def get_serializer_class(self):
        if self.action == 'list':
            return OutletListSerializer
        return OutletSerializer

class UserOutletViewSet(BaseViewSet):
    """ViewSet for UserOutlet model"""
    queryset = UserOutlet.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication, AdminTokenAuthentication, BaTokenAuthentication]
    
    def get_queryset(self):
        user = self.request.user
        if isinstance(user, UAdmin):
            agency_ids = user.agencies.values_list('id', flat=True)
            user_ids = User.objects.filter(agency_id__in=agency_ids).values_list('id', flat=True)
            return UserOutlet.objects.filter(user__in=user_ids)
        if isinstance(user, User):
            return UserOutlet.objects.filter(user=user.id)
        if isinstance(user, Ba) and user.company:
            user_ids = User.objects.filter(agency_id=user.company).values_list('id', flat=True)
            return UserOutlet.objects.filter(user__in=user_ids)
        return UserOutlet.objects.none()

    def get_serializer_class(self):
        if self.action == 'list':
            return UserOutletListSerializer
        return UserOutletSerializer


# Data Collection ViewSets

class AirtelCombinedViewSet(BaseViewSet):
    """ViewSet for AirtelCombined model"""
    queryset = AirtelCombined.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication, AdminTokenAuthentication, BaTokenAuthentication]
    
    def get_queryset(self):
        user = self.request.user
        if isinstance(user, UAdmin):
            agency_ids = user.agencies.values_list('id', flat=True)
            project_ids = Project.objects.filter(company__in=agency_ids).values_list('id', flat=True)
            return AirtelCombined.objects.filter(project_id__in=project_ids)
        if isinstance(user, Ba):
            return AirtelCombined.objects.filter(ba_id=user.id)
        if hasattr(user, 'agency') and user.agency:
            project_ids = Project.objects.filter(company=user.agency.id).values_list('id', flat=True)
            return AirtelCombined.objects.filter(project_id__in=project_ids)
        return AirtelCombined.objects.none()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return AirtelCombinedListSerializer
        return AirtelCombinedSerializer

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        user = request.user
        # If project is not provided, try to infer it
        if 'project' not in data or not data['project']:
            project_id = None
            if isinstance(user, Ba):
                # Find projects assigned to this BA
                project_ids = BaProject.objects.filter(ba_id=user.id).values_list('project_id', flat=True)
                if len(project_ids) == 1:
                    project_id = project_ids[0]
                elif len(project_ids) == 0:
                    return Response({"success": False, "message": "No projects assigned to this BA. Please specify the project."}, status=400)
                else:
                    return Response({"success": False, "message": "Multiple projects assigned to this BA. Please specify the project."}, status=400)
            elif isinstance(user, UAdmin):
                agency_ids = user.agencies.values_list('id', flat=True)
                project_ids = Project.objects.filter(company__in=agency_ids).values_list('id', flat=True)
                if len(project_ids) == 1:
                    project_id = project_ids[0]
                elif len(project_ids) == 0:
                    return Response({"success": False, "message": "No projects found for this admin. Please specify the project."}, status=400)
                else:
                    return Response({"success": False, "message": "Multiple projects found for this admin. Please specify the project."}, status=400)
            elif hasattr(user, 'agency') and user.agency:
                project_ids = Project.objects.filter(company=user.agency.id).values_list('id', flat=True)
                if len(project_ids) == 1:
                    project_id = project_ids[0]
                elif len(project_ids) == 0:
                    return Response({"success": False, "message": "No projects found for this user. Please specify the project."}, status=400)
                else:
                    return Response({"success": False, "message": "Multiple projects found for this user. Please specify the project."}, status=400)
            else:
                return Response({"success": False, "message": "Could not determine project from user context. Please specify the project."}, status=400)
            data['project'] = project_id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({
            'success': True,
            'message': 'Item created successfully',
            'data': {'item': serializer.data}
        }, status=status.HTTP_201_CREATED, headers=headers)

class CokeCombinedViewSet(BaseViewSet):
    """ViewSet for CokeCombined model"""
    queryset = CokeCombined.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication, AdminTokenAuthentication, BaTokenAuthentication]
    
    def get_queryset(self):
        user = self.request.user
        if isinstance(user, UAdmin):
            agency_ids = user.agencies.values_list('id', flat=True)
            project_ids = Project.objects.filter(company__in=agency_ids).values_list('id', flat=True)
            return CokeCombined.objects.filter(project_id__in=project_ids)
        if isinstance(user, Ba):
            return CokeCombined.objects.filter(ba_id=user.id)
        if hasattr(user, 'agency') and user.agency:
            project_ids = Project.objects.filter(company=user.agency.id).values_list('id', flat=True)
            return CokeCombined.objects.filter(project_id__in=project_ids)
        return CokeCombined.objects.none()

    def get_serializer_class(self):
        if self.action == 'list':
            return CokeCombinedListSerializer
        return CokeCombinedSerializer

class BaimsCombinedViewSet(BaseViewSet):
    """ViewSet for BaimsCombined model"""
    queryset = BaimsCombined.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication, AdminTokenAuthentication, BaTokenAuthentication]
    
    def get_queryset(self):
        user = self.request.user
        if isinstance(user, UAdmin):
            agency_ids = user.agencies.values_list('id', flat=True)
            project_ids = Project.objects.filter(company__in=agency_ids).values_list('id', flat=True)
            return BaimsCombined.objects.filter(project_id__in=project_ids)
        if isinstance(user, Ba):
            return BaimsCombined.objects.filter(ba_id=user.id)
        if hasattr(user, 'agency') and user.agency:
            project_ids = Project.objects.filter(company=user.agency.id).values_list('id', flat=True)
            return BaimsCombined.objects.filter(project_id__in=project_ids)
        return BaimsCombined.objects.none()

    def get_serializer_class(self):
        if self.action == 'list':
            return BaimsCombinedListSerializer
        return BaimsCombinedSerializer

class KspcaCombinedViewSet(BaseViewSet):
    """ViewSet for KspcaCombined model"""
    queryset = KspcaCombined.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication, AdminTokenAuthentication, BaTokenAuthentication]
    
    def get_queryset(self):
        user = self.request.user
        if isinstance(user, UAdmin):
            agency_ids = user.agencies.values_list('id', flat=True)
            project_ids = Project.objects.filter(company__in=agency_ids).values_list('id', flat=True)
            return KspcaCombined.objects.filter(project_id__in=project_ids)
        if isinstance(user, Ba):
            return KspcaCombined.objects.filter(ba_id=user.id)
        if hasattr(user, 'agency') and user.agency:
            project_ids = Project.objects.filter(company=user.agency.id).values_list('id', flat=True)
            return KspcaCombined.objects.filter(project_id__in=project_ids)
        return KspcaCombined.objects.none()

    def get_serializer_class(self):
        if self.action == 'list':
            return KspcaCombinedListSerializer
        return KspcaCombinedSerializer

class SaffCombinedViewSet(BaseViewSet):
    """ViewSet for SaffCombined model"""
    queryset = SaffCombined.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication, AdminTokenAuthentication, BaTokenAuthentication]
    
    def get_queryset(self):
        user = self.request.user
        if isinstance(user, UAdmin):
            agency_ids = user.agencies.values_list('id', flat=True)
            project_ids = Project.objects.filter(company__in=agency_ids).values_list('id', flat=True)
            return SaffCombined.objects.filter(project_id__in=project_ids)
        if isinstance(user, Ba):
            return SaffCombined.objects.filter(ba_id=user.id)
        if hasattr(user, 'agency') and user.agency:
            project_ids = Project.objects.filter(company=user.agency.id).values_list('id', flat=True)
            return SaffCombined.objects.filter(project_id__in=project_ids)
        return SaffCombined.objects.none()

    def get_serializer_class(self):
        if self.action == 'list':
            return SaffCombinedListSerializer
        return SaffCombinedSerializer

class RedbullOutletViewSet(BaseViewSet):
    """ViewSet for RedbullOutlet model"""
    queryset = RedbullOutlet.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication, AdminTokenAuthentication, BaTokenAuthentication]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return RedbullOutletListSerializer
        return RedbullOutletSerializer

class TotalKenyaViewSet(BaseViewSet):
    """ViewSet for TotalKenya model"""
    queryset = TotalKenya.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication, AdminTokenAuthentication, BaTokenAuthentication]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return TotalKenyaListSerializer
        return TotalKenyaSerializer

class AppDataViewSet(BaseViewSet):
    """ViewSet for AppData model"""
    queryset = AppData.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication, AdminTokenAuthentication, BaTokenAuthentication]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return AppDataListSerializer
        return AppDataSerializer

class BaViewSet(BaseViewSet):
    """ViewSet for Ba model"""
    queryset = Ba.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication, AdminTokenAuthentication, BaTokenAuthentication]
    
    def get_queryset(self):
        user = self.request.user
        if isinstance(user, UAdmin):
            agency_ids = user.agencies.values_list('id', flat=True)
            return Ba.objects.filter(company__in=agency_ids)
        elif isinstance(user, Ba):
            return Ba.objects.filter(id=user.id)
        elif hasattr(user, 'agency') and user.agency:
            return Ba.objects.filter(company=user.agency.id)
        return Ba.objects.none()

    def get_serializer_class(self):
        if self.action == 'list':
            return BaListSerializer
        return BaSerializer

    def create(self, request, *args, **kwargs):
        """
        Create a new BA.
        The company is inferred from the user token, not from the request data.
        Automatically associate them with projects based on their company.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        company_id = None

        if isinstance(user, UAdmin):
            agencies = user.agencies.all()
            if agencies.count() == 0:
                return Response({"success": False, "message": "Admin user is not associated with any company."}, status=status.HTTP_403_FORBIDDEN)
            if agencies.count() == 1:
                company_id = agencies.first().id
            else:
                return Response({"success": False, "message": "Admin with multiple companies must specify a company in the UI."}, status=status.HTTP_400_BAD_REQUEST)

        elif isinstance(user, Ba):
            if not user.company:
                return Response({"success": False, "message": "BA user is not associated with any company."}, status=status.HTTP_403_FORBIDDEN)
            company_id = user.company
        
        elif hasattr(user, 'agency') and user.agency:
            company_id = user.agency.id
        
        else:
            return Response({"success": False, "message": "Could not determine company from user token."}, status=status.HTTP_400_BAD_REQUEST)

        ba = serializer.save(company=company_id)
        
        projects = Project.objects.filter(company=company_id)
        
        start_date_str = request.data.get('start_date')
        end_date_str = request.data.get('end_date')

        try:
            start_date = date.fromisoformat(start_date_str) if start_date_str else date.today()
            end_date = date.fromisoformat(end_date_str) if end_date_str else date.today() + timedelta(days=365 * 5)
        except (ValueError, TypeError):
            start_date = date.today()
            end_date = date.today() + timedelta(days=365*5)

        ba_projects = []
        for project in projects:
            ba_projects.append(
                BaProject(ba_id=ba.id, project_id=project.id, start_date=start_date, end_date=end_date)
            )
        
        if ba_projects:
            BaProject.objects.bulk_create(ba_projects)
            
        return Response({
            'success': True,
            'message': f'BA created and assigned to {len(ba_projects)} projects.',
            'data': BaListSerializer(ba).data
        }, status=status.HTTP_201_CREATED)

class BackendViewSet(BaseViewSet):
    """ViewSet for Backend model"""
    queryset = Backend.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication, AdminTokenAuthentication, BaTokenAuthentication]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return BackendListSerializer
        return BackendSerializer

class BaProjectViewSet(BaseViewSet):
    """ViewSet for BaProject model"""
    queryset = BaProject.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication, AdminTokenAuthentication, BaTokenAuthentication]
    
    def get_queryset(self):
        user = self.request.user
        if isinstance(user, UAdmin):
            agency_ids = user.agencies.values_list('id', flat=True)
            ba_ids = Ba.objects.filter(company__in=agency_ids).values_list('id', flat=True)
            return BaProject.objects.filter(ba_id__in=ba_ids)
        if isinstance(user, Ba):
            return BaProject.objects.filter(ba_id=user.id)
        return BaProject.objects.none()

    def get_serializer_class(self):
        if self.action == 'list':
            return BaProjectListSerializer
        return BaProjectSerializer

class ProjectAssocViewSet(BaseViewSet):
    """ViewSet for ProjectAssoc model"""
    queryset = ProjectAssoc.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication, AdminTokenAuthentication, BaTokenAuthentication]
    
    def get_queryset(self):
        user = self.request.user
        if isinstance(user, UAdmin):
            agency_ids = user.agencies.values_list('id', flat=True)
            project_ids = Project.objects.filter(company__in=agency_ids).values_list('id', flat=True)
            return ProjectAssoc.objects.filter(project__in=project_ids)
        
        allowed_project_ids = []
        if isinstance(user, Ba):
            allowed_project_ids = BaProject.objects.filter(ba_id=user.id).values_list('project_id', flat=True)
        elif hasattr(user, 'agency') and user.agency:
            allowed_project_ids = Project.objects.filter(company=user.agency.id).values_list('id', flat=True)

        return ProjectAssoc.objects.filter(project__in=allowed_project_ids)

    def get_serializer_class(self):
        if self.action == 'list':
            return ProjectAssocListSerializer
        return ProjectAssocSerializer

    def create(self, request, *args, **kwargs):
        """
        Create a new ProjectAssoc (form field).
        The project ID is inferred from the user token if not provided.
        """
        data = request.data.copy()
        user = request.user

        if 'project' not in data or not data['project']:
            project_id = None
            if isinstance(user, Ba):
                project_ids = BaProject.objects.filter(ba_id=user.id).values_list('project_id', flat=True)
                if len(project_ids) == 1:
                    project_id = project_ids[0]
                elif len(project_ids) == 0:
                    return Response({"success": False, "message": "No projects assigned to this BA. Please specify the project."}, status=400)
                else:
                    return Response({"success": False, "message": "Multiple projects assigned to this BA. Please specify the project."}, status=400)
            
            elif isinstance(user, UAdmin):
                agency_ids = user.agencies.values_list('id', flat=True)
                project_ids = Project.objects.filter(company__in=agency_ids).values_list('id', flat=True)
                if len(project_ids) == 1:
                    project_id = project_ids[0]
                elif len(project_ids) == 0:
                    return Response({"success": False, "message": "No projects found for this admin. Please specify the project."}, status=400)
                else:
                    return Response({"success": False, "message": "Multiple projects found for this admin. Please specify the project."}, status=400)

            elif hasattr(user, 'agency') and user.agency:
                project_ids = Project.objects.filter(company=user.agency.id).values_list('id', flat=True)
                if len(project_ids) == 1:
                    project_id = project_ids[0]
                elif len(project_ids) == 0:
                    return Response({"success": False, "message": "No projects found for this user. Please specify the project."}, status=400)
                else:
                    return Response({"success": False, "message": "Multiple projects found for this user. Please specify the project."}, status=400)
            else:
                return Response({"success": False, "message": "Could not determine project from user context. Please specify the project."}, status=400)
            
            data['project'] = project_id
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({
            'success': True,
            'message': 'Form field created successfully',
            'data': {'item': serializer.data}
        }, status=status.HTTP_201_CREATED, headers=headers)

class ContainersViewSet(BaseViewSet):
    """ViewSet for Containers model"""
    queryset = Containers.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication, AdminTokenAuthentication, BaTokenAuthentication]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ContainersListSerializer
        return ContainersSerializer

class ContainerOptionsViewSet(BaseViewSet):
    """ViewSet for ContainerOptions model"""
    queryset = ContainerOptions.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication, AdminTokenAuthentication, BaTokenAuthentication]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ContainerOptionsListSerializer
        return ContainerOptionsSerializer

class CoopViewSet(BaseViewSet):
    """ViewSet for Coop model"""
    queryset = Coop.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication, AdminTokenAuthentication, BaTokenAuthentication]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CoopListSerializer
        return CoopSerializer

class Coop2ViewSet(BaseViewSet):
    """ViewSet for Coop2 model"""
    queryset = Coop2.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication, AdminTokenAuthentication, BaTokenAuthentication]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return Coop2ListSerializer
        return Coop2Serializer

class FormSectionViewSet(BaseViewSet):
    """ViewSet for FormSection model"""
    queryset = FormSection.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication, AdminTokenAuthentication, BaTokenAuthentication]
    
    def get_queryset(self):
        user = self.request.user
        if isinstance(user, UAdmin):
            agency_ids = user.agencies.values_list('id', flat=True)
            project_ids = Project.objects.filter(company__in=agency_ids).values_list('id', flat=True)
            return FormSection.objects.filter(project__in=project_ids)
        
        allowed_project_ids = []
        if isinstance(user, Ba):
            allowed_project_ids = BaProject.objects.filter(ba_id=user.id).values_list('project_id', flat=True)
        elif hasattr(user, 'agency') and user.agency:
            allowed_project_ids = Project.objects.filter(company=user.agency.id).values_list('id', flat=True)

        return FormSection.objects.filter(project__in=allowed_project_ids)

    def get_serializer_class(self):
        if self.action == 'list':
            return FormSectionListSerializer
        return FormSectionSerializer

class FormSubSectionViewSet(BaseViewSet):
    """ViewSet for FormSubSection model"""
    queryset = FormSubSection.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication, AdminTokenAuthentication, BaTokenAuthentication]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return FormSubSectionListSerializer
        return FormSubSectionSerializer

class InputGroupViewSet(BaseViewSet):
    """ViewSet for InputGroup model"""
    queryset = InputGroup.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication, AdminTokenAuthentication, BaTokenAuthentication]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return InputGroupListSerializer
        return InputGroupSerializer

class InputOptionsViewSet(BaseViewSet):
    """ViewSet for InputOptions model"""
    queryset = InputOptions.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication, AdminTokenAuthentication, BaTokenAuthentication]
    
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

        # NOTE: This assumes you are storing plain text passwords.
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

        # Get or create a token for the user
        token, created = AuthToken.objects.get_or_create(user=user)

        user_data = UserSerializer(user).data

        return Response({
            'success': True,
            'message': 'Login successful',
            'data': {
                'token': token.key,
                'user': user_data
            }
        })

class AdminLoginView(APIView):
    """
    Custom login view to authenticate an Admin User and return a token.
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
            admin = UAdmin.objects.get(u_name=username)
        except UAdmin.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)

        # NOTE: This assumes you are storing plain text passwords.
        if admin.p_phrase != password:
            return Response({
                'success': False,
                'message': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)

        # If you want to check for active status, add a property to UAdmin and check here
        # if not admin.is_active:
        #     return Response({
        #         'success': False,
        #         'message': 'Admin account is inactive'
        #     }, status=status.HTTP_403_FORBIDDEN)

        # Get or create a token for the admin
        token, created = AdminAuthToken.objects.get_or_create(admin=admin)

        admin_data = UAdminSerializer(admin).data

        return Response({
            'success': True,
            'message': 'Admin login successful',
            'data': {
                'token': token.key,
                'admin': admin_data
            }
        })

class UAdminViewSet(viewsets.ModelViewSet):
    """ViewSet for UAdmin model"""
    queryset = UAdmin.objects.all()
    serializer_class = UAdminSerializer
    authentication_classes = [AdminTokenAuthentication]
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'], url_path='assign-agency')
    def assign_agency(self, request, pk=None):
        """Assign an agency to this admin user."""
        admin = self.get_object()
        agency_id = request.data.get('agency_id')

        if not agency_id:
            return Response({'success': False, 'message': 'agency_id is required in the request body.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            agency = Agency.objects.get(id=agency_id)
        except Agency.DoesNotExist:
            return Response({'success': False, 'message': f'Agency with ID {agency_id} not found.'}, status=status.HTTP_404_NOT_FOUND)

        admin.agencies.add(agency)
        serializer = self.get_serializer(admin)
        return Response({
            'success': True,
            'message': f'Successfully assigned agency "{agency.name}" to admin "{admin.u_name}".',
            'data': serializer.data
        })

    @action(detail=True, methods=['post'], url_path='unassign-agency')
    def unassign_agency(self, request, pk=None):
        """Unassign an agency from this admin user."""
        admin = self.get_object()
        agency_id = request.data.get('agency_id')

        if not agency_id:
            return Response({'success': False, 'message': 'agency_id is required in the request body.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            agency = Agency.objects.get(id=agency_id)
        except Agency.DoesNotExist:
             return Response({'success': False, 'message': f'Agency with ID {agency_id} not found.'}, status=status.HTTP_404_NOT_FOUND)

        if not admin.agencies.filter(id=agency.id).exists():
            return Response({'success': False, 'message': f'Admin "{admin.u_name}" is not assigned to agency "{agency.name}".'}, status=status.HTTP_400_BAD_REQUEST)

        admin.agencies.remove(agency)
        serializer = self.get_serializer(admin)
        return Response({
            'success': True,
            'message': f'Successfully unassigned agency "{agency.name}" from admin "{admin.u_name}".',
            'data': serializer.data
        })

class BaLoginView(APIView):
    """
    Custom login view to authenticate a BA (Business Agent) using phone and pass_code.
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        phone = request.data.get('phone')
        pass_code = request.data.get('pass_code')

        if not phone or not pass_code:
            return Response({
                'success': False,
                'message': 'Phone and pass_code are required'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            ba = Ba.objects.get(phone=phone)
        except Ba.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)

        if ba.pass_code != pass_code:
            return Response({
                'success': False,
                'message': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)

        # Optional: Check if BA is active (if such a field exists)
        if hasattr(ba, 'active_status') and getattr(ba, 'active_status', 1) != 1:
            return Response({
                'success': False,
                'message': 'BA account is inactive'
            }, status=status.HTTP_403_FORBIDDEN)

        # Get or create a token for the BA
        token, created = BaAuthToken.objects.get_or_create(ba=ba)

        return Response({
            'success': True,
            'message': 'BA login successful',
            'data': {
                'token': token.key,
                'ba_id': ba.id
            }
        })

class ProjectHeadWithProjectsView(APIView):
    authentication_classes = [TokenAuthentication, AdminTokenAuthentication, BaTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        user = request.user
        # Allow for UAdmin and Ba
        if isinstance(user, UAdmin):
            agency_ids = user.agencies.values_list('id', flat=True)
        elif isinstance(user, Ba):
            agency_ids = [user.company] if user.company else []
        else:
            return Response({'detail': 'Only admins and BAs can access this endpoint.'}, status=403)
        
        project_heads = ProjectHead.objects.filter(company__in=agency_ids)
        
        if pk is not None:
            project_heads = project_heads.filter(id=pk)
            if not project_heads.exists():
                return Response({
                    'success': False,
                    'message': f'ProjectHead with ID {pk} not found or you do not have permission to view it.'
                }, status=status.HTTP_404_NOT_FOUND)

        data = []
        for head in project_heads:
            projects = Project.objects.filter(company=head.company)
            project_list = []
            for project in projects:
                form_details = {
                    'id': project.id,
                    'name': project.name,
                    'client': project.client,
                    'top_table': project.top_table,
                    'rank': project.rank,
                    'combined': project.combined,
                    'status': project.status,
                    'location_status': project.location_status,
                    'company': project.company,
                    'image_required': project.image_required,
                }
                project_list.append({
                    'form_details': form_details,
                })
            data.append({
                'project_head': {
                    'id': head.id,
                    'name': head.name,
                    'company': head.company,
                    'start_date': str(head.start_date) if head.start_date else None,
                    'end_date': str(head.end_date) if head.end_date else None,
                    'aka_name': head.aka_name,
                },
                'projects': project_list
            })
        return Response({'results': data})

    def post(self, request):
        """
        Create a new ProjectHead (and optionally assign projects).
        """
        data = request.data
        name = data.get('name')
        aka_name = data.get('aka_name')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        company = data.get('company')
        projects = data.get('projects', [])

        if not name or not aka_name or not company:
            return Response({'success': False, 'message': 'name, aka_name, and company are required.'}, status=400)

        # Create the ProjectHead
        project_head = ProjectHead.objects.create(
            name=name,
            aka_name=aka_name,
            start_date=start_date,
            end_date=end_date,
            company=company
        )

        # Optionally assign projects (if you want to link in a custom way, add here)
        # For now, just return the created head and the project IDs

        return Response({
            'success': True,
            'message': 'Project Head created successfully.',
            'data': {
                'id': project_head.id,
                'name': project_head.name,
                'aka_name': project_head.aka_name,
                'start_date': str(project_head.start_date) if project_head.start_date else None,
                'end_date': str(project_head.end_date) if project_head.end_date else None,
                'company': project_head.company,
                'projects': projects
            }
        }, status=201)

    def put(self, request, pk=None):
        """
        Update a ProjectHead by ID.
        """
        user = request.user
        project_head_id = pk or request.data.get('id')
        if not project_head_id:
            return Response({'success': False, 'message': 'ProjectHead ID is required.'}, status=400)
        try:
            project_head = ProjectHead.objects.get(id=project_head_id)
        except ProjectHead.DoesNotExist:
            return Response({'success': False, 'message': 'ProjectHead not found.'}, status=404)
        # Permission check
        if isinstance(user, UAdmin):
            allowed_agency_ids = user.agencies.values_list('id', flat=True)
            if project_head.company not in allowed_agency_ids:
                return Response({'success': False, 'message': 'You do not have permission to update this ProjectHead.'}, status=403)
        elif isinstance(user, Ba):
            if user.company != project_head.company:
                return Response({'success': False, 'message': 'You do not have permission to update this ProjectHead.'}, status=403)
        else:
            return Response({'success': False, 'message': 'Only admins and BAs can update ProjectHeads.'}, status=403)
        serializer = ProjectHeadSerializer(project_head, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'message': 'ProjectHead updated successfully.', 'data': serializer.data})
        return Response({'success': False, 'message': 'Invalid data.', 'errors': serializer.errors}, status=400)

    def patch(self, request, pk=None):
        return self.put(request, pk)

    def delete(self, request, pk=None):
        """
        Delete a ProjectHead by ID.
        """
        user = request.user
        project_head_id = pk or request.data.get('id')
        if not project_head_id:
            return Response({'success': False, 'message': 'ProjectHead ID is required.'}, status=400)
        try:
            project_head = ProjectHead.objects.get(id=project_head_id)
        except ProjectHead.DoesNotExist:
            return Response({'success': False, 'message': 'ProjectHead not found.'}, status=404)
        # Permission check
        if isinstance(user, UAdmin):
            allowed_agency_ids = user.agencies.values_list('id', flat=True)
            if project_head.company not in allowed_agency_ids:
                return Response({'success': False, 'message': 'You do not have permission to delete this ProjectHead.'}, status=403)
        elif isinstance(user, Ba):
            if user.company != project_head.company:
                return Response({'success': False, 'message': 'You do not have permission to delete this ProjectHead.'}, status=403)
        else:
            return Response({'success': False, 'message': 'Only admins and BAs can delete ProjectHeads.'}, status=403)
        project_head.delete()
        return Response({'success': True, 'message': 'ProjectHead deleted successfully.'})

class ProjectFormFieldsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, project_id=None):
        user = request.user
        project_ids = []
        # Admin: all projects in their agencies
        if hasattr(user, 'agencies'):
            agency_ids = user.agencies.values_list('id', flat=True)
            project_ids = list(Project.objects.filter(company__in=agency_ids).values_list('id', flat=True))
        # BA: projects assigned to them
        elif hasattr(user, 'company') and hasattr(user, 'id') and hasattr(user, 'is_authenticated'):
            from .models import BaProject
            project_ids = list(BaProject.objects.filter(ba_id=user.id).values_list('project_id', flat=True))
        # Agency user: projects for their agency
        elif hasattr(user, 'agency') and user.agency:
            project_ids = list(Project.objects.filter(company=user.agency.id).values_list('id', flat=True))
        # If no projects found, return empty
        if not project_ids:
            return Response({'form_fields': []})
        # Support both path and query param
        pid = project_id
        if pid is None:
            pid = request.query_params.get('project_id')
        if pid is not None:
            try:
                pid = int(pid)
            except ValueError:
                return Response({'form_fields': [], 'error': 'Invalid project_id'}, status=400)
            if pid not in project_ids:
                return Response({'form_fields': [], 'error': 'You do not have access to this project'}, status=403)
            project_ids = [pid]
        # Get all form fields for these projects
        form_fields = ProjectAssoc.objects.filter(project__in=project_ids).order_by('project', 'rank')
        serializer = ProjectAssocSerializer(form_fields, many=True)
        return Response({'form_fields': serializer.data})

    def post(self, request, project_id=None):
        user = request.user
        data = request.data.copy()
        project_ids = []
        # Admin: all projects in their agencies
        if hasattr(user, 'agencies'):
            agency_ids = user.agencies.values_list('id', flat=True)
            project_ids = list(Project.objects.filter(company__in=agency_ids).values_list('id', flat=True))
        # BA: projects assigned to them
        elif hasattr(user, 'company') and hasattr(user, 'id') and hasattr(user, 'is_authenticated'):
            from .models import BaProject
            project_ids = list(BaProject.objects.filter(ba_id=user.id).values_list('project_id', flat=True))
        # Agency user: projects for their agency
        elif hasattr(user, 'agency') and user.agency:
            project_ids = list(Project.objects.filter(company=user.agency.id).values_list('id', flat=True))
        # If no projects found, return error
        if not project_ids:
            return Response({'success': False, 'message': 'No accessible projects found.'}, status=403)
        # Determine project to use
        pid = project_id
        if pid is None:
            pid = request.query_params.get('project_id')
        if pid is None:
            pid = data.get('project')
        if pid is not None:
            try:
                pid = int(pid)
            except ValueError:
                return Response({'success': False, 'message': 'Invalid project_id.'}, status=400)
            if pid not in project_ids:
                return Response({'success': False, 'message': 'You do not have access to this project.'}, status=403)
        else:
            # If only one project, use it
            if len(project_ids) == 1:
                pid = project_ids[0]
            else:
                return Response({'success': False, 'message': 'Multiple projects available. Please specify project.'}, status=400)
        data['project'] = pid
        serializer = ProjectAssocSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'message': 'Form field created successfully.', 'form_field': serializer.data}, status=201)
        return Response({'success': False, 'message': 'Invalid data.', 'errors': serializer.errors}, status=400)

    def put(self, request, form_field_id=None):
        user = request.user
        if form_field_id is None:
            return Response({'success': False, 'message': 'Form field ID is required.'}, status=400)
        try:
            form_field = ProjectAssoc.objects.get(id=form_field_id)
        except ProjectAssoc.DoesNotExist:
            return Response({'success': False, 'message': 'Form field not found.'}, status=404)
        # Check project access
        project_id = form_field.project
        allowed_projects = []
        if hasattr(user, 'agencies'):
            agency_ids = user.agencies.values_list('id', flat=True)
            allowed_projects = list(Project.objects.filter(company__in=agency_ids).values_list('id', flat=True))
        elif hasattr(user, 'company') and hasattr(user, 'id') and hasattr(user, 'is_authenticated'):
            from .models import BaProject
            allowed_projects = list(BaProject.objects.filter(ba_id=user.id).values_list('project_id', flat=True))
        elif hasattr(user, 'agency') and user.agency:
            allowed_projects = list(Project.objects.filter(company=user.agency.id).values_list('id', flat=True))
        if project_id not in allowed_projects:
            return Response({'success': False, 'message': 'You do not have access to this project.'}, status=403)
        serializer = ProjectAssocSerializer(form_field, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'message': 'Form field updated successfully.', 'form_field': serializer.data})
        return Response({'success': False, 'message': 'Invalid data.', 'errors': serializer.errors}, status=400)

    def patch(self, request, form_field_id=None):
        return self.put(request, form_field_id)

    def delete(self, request, form_field_id=None):
        user = request.user
        if form_field_id is None:
            return Response({'success': False, 'message': 'Form field ID is required.'}, status=400)
        try:
            form_field = ProjectAssoc.objects.get(id=form_field_id)
        except ProjectAssoc.DoesNotExist:
            return Response({'success': False, 'message': 'Form field not found.'}, status=404)
        # Check project access
        project_id = form_field.project
        allowed_projects = []
        if hasattr(user, 'agencies'):
            agency_ids = user.agencies.values_list('id', flat=True)
            allowed_projects = list(Project.objects.filter(company__in=agency_ids).values_list('id', flat=True))
        elif hasattr(user, 'company') and hasattr(user, 'id') and hasattr(user, 'is_authenticated'):
            from .models import BaProject
            allowed_projects = list(BaProject.objects.filter(ba_id=user.id).values_list('project_id', flat=True))
        elif hasattr(user, 'agency') and user.agency:
            allowed_projects = list(Project.objects.filter(company=user.agency.id).values_list('id', flat=True))
        if project_id not in allowed_projects:
            return Response({'success': False, 'message': 'You do not have access to this project.'}, status=403)
        form_field.delete()
        return Response({'success': True, 'message': 'Form field deleted successfully.'})

class UnifiedFormFieldView(APIView):
    permission_classes = [IsAuthenticated]

    def _get_allowed_projects_for_user(self, user):
        project_ids = []
        if hasattr(user, 'agencies'): # UAdmin
            agency_ids = user.agencies.values_list('id', flat=True)
            project_ids = list(Project.objects.filter(company__in=agency_ids).values_list('id', flat=True))
        elif hasattr(user, 'company') and hasattr(user, 'id') and hasattr(user, 'is_authenticated'): # BA
            from .models import BaProject
            project_ids = list(BaProject.objects.filter(ba_id=user.id).values_list('project_id', flat=True))
        elif hasattr(user, 'agency') and user.agency: # Regular User
            project_ids = list(Project.objects.filter(company=user.agency.id).values_list('id', flat=True))
        return project_ids

    def get(self, request, id):
        """GET all form fields for a given form_id (project_id)"""
        user = request.user
        form_id = id
        
        allowed_projects = self._get_allowed_projects_for_user(user)
        if form_id not in allowed_projects:
            return Response({'success': False, 'message': 'You do not have access to this project.'}, status=403)
        
        form_fields = ProjectAssoc.objects.filter(project=form_id).order_by('rank')
        serializer = ProjectAssocSerializer(form_fields, many=True)
        return Response({'success': True, 'form_fields': serializer.data})

    def post(self, request, id):
        """POST to create a new form field for a given form_id (project_id)"""
        user = request.user
        form_id = id

        allowed_projects = self._get_allowed_projects_for_user(user)
        if form_id not in allowed_projects:
            return Response({'success': False, 'message': 'You do not have access to this project.'}, status=403)

        data = request.data.copy()
        data['project'] = form_id
        
        serializer = ProjectAssocSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'message': 'Form field created successfully.', 'form_field': serializer.data}, status=201)
        return Response({'success': False, 'message': 'Invalid data.', 'errors': serializer.errors}, status=400)

    def put(self, request, id):
        """PUT to update a form field by its field_id"""
        user = request.user
        field_id = id
        
        try:
            form_field = ProjectAssoc.objects.get(id=field_id)
        except ProjectAssoc.DoesNotExist:
            return Response({'success': False, 'message': 'Form field not found.'}, status=404)

        allowed_projects = self._get_allowed_projects_for_user(user)
        if form_field.project not in allowed_projects:
            return Response({'success': False, 'message': 'You do not have permission to modify this form field.'}, status=403)
            
        serializer = ProjectAssocSerializer(form_field, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'message': 'Form field updated successfully.', 'form_field': serializer.data})
        return Response({'success': False, 'message': 'Invalid data.', 'errors': serializer.errors}, status=400)
        
    def delete(self, request, id):
        """DELETE a form field by its field_id"""
        user = request.user
        field_id = id

        try:
            form_field = ProjectAssoc.objects.get(id=field_id)
        except ProjectAssoc.DoesNotExist:
            return Response({'success': False, 'message': 'Form field not found.'}, status=404)

        allowed_projects = self._get_allowed_projects_for_user(user)
        if form_field.project not in allowed_projects:
            return Response({'success': False, 'message': 'You do not have permission to delete this form field.'}, status=403)
            
        form_field.delete()
        return Response({'success': True, 'message': 'Form field deleted successfully.'})

class UnifiedFormSectionView(APIView):
    permission_classes = [IsAuthenticated]

    def _get_allowed_projects_for_user(self, user):
        project_ids = []
        if hasattr(user, 'agencies'): # UAdmin
            agency_ids = user.agencies.values_list('id', flat=True)
            project_ids = list(Project.objects.filter(company__in=agency_ids).values_list('id', flat=True))
        elif hasattr(user, 'company') and hasattr(user, 'id') and hasattr(user, 'is_authenticated'): # BA
            from .models import BaProject
            project_ids = list(BaProject.objects.filter(ba_id=user.id).values_list('project_id', flat=True))
        elif hasattr(user, 'agency') and user.agency: # Regular User
            project_ids = list(Project.objects.filter(company=user.agency.id).values_list('id', flat=True))
        return project_ids

    def get(self, request, id):
        """GET all form sections for a given form_id (project_id)"""
        user = request.user
        form_id = id
        
        allowed_projects = self._get_allowed_projects_for_user(user)
        if form_id not in allowed_projects:
            return Response({'success': False, 'message': 'You do not have access to this project.'}, status=403)
        
        form_sections = FormSection.objects.filter(project=form_id).order_by('rank')
        serializer = FormSectionListSerializer(form_sections, many=True)
        return Response({'success': True, 'form_sections': serializer.data})

    def post(self, request, id):
        """POST to create a new form section for a given form_id (project_id)"""
        user = request.user
        form_id = id

        allowed_projects = self._get_allowed_projects_for_user(user)
        if form_id not in allowed_projects:
            return Response({'success': False, 'message': 'You do not have access to this project.'}, status=403)

        data = request.data.copy()
        data['project'] = form_id
        
        serializer = FormSectionSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'message': 'Form section created successfully.', 'form_section': serializer.data}, status=201)
        return Response({'success': False, 'message': 'Invalid data.', 'errors': serializer.errors}, status=400)

    def put(self, request, id):
        """PUT to update a form section by its form_section_id"""
        user = request.user
        section_id = id
        
        try:
            form_section = FormSection.objects.get(id=section_id)
        except FormSection.DoesNotExist:
            return Response({'success': False, 'message': 'Form section not found.'}, status=404)

        allowed_projects = self._get_allowed_projects_for_user(user)
        if form_section.project.id not in allowed_projects:
            return Response({'success': False, 'message': 'You do not have permission to modify this form section.'}, status=403)
            
        serializer = FormSectionSerializer(form_section, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'message': 'Form section updated successfully.', 'form_section': serializer.data})
        return Response({'success': False, 'message': 'Invalid data.', 'errors': serializer.errors}, status=400)
        
    def delete(self, request, id):
        """DELETE a form section by its form_section_id"""
        user = request.user
        section_id = id

        try:
            form_section = FormSection.objects.get(id=section_id)
        except FormSection.DoesNotExist:
            return Response({'success': False, 'message': 'Form section not found.'}, status=404)

        allowed_projects = self._get_allowed_projects_for_user(user)
        if form_section.project.id not in allowed_projects:
            return Response({'success': False, 'message': 'You do not have permission to delete this form section.'}, status=403)
            
        form_section.delete()
        return Response({'success': True, 'message': 'Form section deleted successfully.'})

class UnifiedFormView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        """GET forms by project_head_id"""
        try:
            project_head = ProjectHead.objects.get(id=id)
            # Add permission check here if necessary
            projects = Project.objects.filter(company=project_head.company)
            serializer = ProjectListSerializer(projects, many=True)
            return Response({
                'success': True,
                'data': serializer.data
            })
        except ProjectHead.DoesNotExist:
            return Response({'success': False, 'message': 'ProjectHead not found.'}, status=404)

    def post(self, request, id):
        """POST to create a form under a project_head_id"""
        try:
            project_head = ProjectHead.objects.get(id=id)
        except ProjectHead.DoesNotExist:
            return Response({'success': False, 'message': 'ProjectHead not found.'}, status=404)

        data = request.data.copy()
        data['company'] = project_head.company
        serializer = ProjectSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'message': 'Form created successfully.', 'data': serializer.data}, status=201)
        return Response({'success': False, 'message': 'Invalid data.', 'errors': serializer.errors}, status=400)

    def put(self, request, id):
        """PUT to update a form by form_id"""
        try:
            project = Project.objects.get(id=id)
            # Add permission check here
            serializer = ProjectSerializer(project, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'success': True, 'message': 'Form updated successfully.', 'data': serializer.data})
            return Response({'success': False, 'message': 'Invalid data.', 'errors': serializer.errors}, status=400)
        except Project.DoesNotExist:
            return Response({'success': False, 'message': 'Form not found.'}, status=404)

    def delete(self, request, id):
        """DELETE a form by form_id"""
        try:
            project = Project.objects.get(id=id)
            # Add permission check here
            project.delete()
            return Response({'success': True, 'message': 'Form deleted successfully.'}, status=200)
        except Project.DoesNotExist:
            return Response({'success': False, 'message': 'Form not found.'}, status=404)
