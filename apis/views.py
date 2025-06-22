from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from .models import User
from .serializers import UserSerializer, UserListSerializer
from django.db import models

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
    permission_classes = [AllowAny]  # We'll change this later for security
    
    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.action == 'list':
            return UserListSerializer
        return UserSerializer
    
    def list(self, request, *args, **kwargs):
        """Get all users with optional filtering"""
        queryset = self.get_queryset()
        
        # Filter by region if provided
        region = request.query_params.get('region', None)
        if region:
            queryset = queryset.filter(region=region)
        
        # Filter by active status if provided
        active_status = request.query_params.get('active_status', None)
        if active_status is not None:
            queryset = queryset.filter(active_status=int(active_status))
        
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
            'message': 'Users retrieved successfully',
            'data': {
                'users': serializer.data,
                'count': queryset.count()
            }
        })
    
    def create(self, request, *args, **kwargs):
        """Create a new user"""
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
            'message': 'Invalid data provided',
            'data': {
                'errors': serializer.errors
            }
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def retrieve(self, request, *args, **kwargs):
        """Get a specific user by ID"""
        user = self.get_object()
        serializer = UserListSerializer(user)
        return Response({
            'success': True,
            'message': 'User retrieved successfully',
            'data': {
                'user': serializer.data
            }
        })
    
    def update(self, request, *args, **kwargs):
        """Update a user (full update)"""
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
            'message': 'Invalid data provided',
            'data': {
                'errors': serializer.errors
            }
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def partial_update(self, request, *args, **kwargs):
        """Update a user (partial update)"""
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
            'message': 'Invalid data provided',
            'data': {
                'errors': serializer.errors
            }
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        """Delete a user"""
        user = self.get_object()
        user.delete()
        return Response({
            'success': True,
            'message': 'User deleted successfully',
            'data': {}
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def regions(self, request):
        """Get all unique regions"""
        regions = User.objects.values_list('region', flat=True).distinct()
        return Response({
            'success': True,
            'message': 'Regions retrieved successfully',
            'data': {
                'regions': list(regions)
            }
        })
    
    @action(detail=True, methods=['post'])
    def toggle_status(self, request, pk=None):
        """Toggle user active status"""
        user = self.get_object()
        user.active_status = 0 if user.active_status == 1 else 1
        user.save()
        status_text = "active" if user.active_status == 1 else "inactive"
        return Response({
            'success': True,
            'message': f'User status changed to {status_text}',
            'data': {
                'user': UserListSerializer(user).data
            }
        })
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get user statistics"""
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
