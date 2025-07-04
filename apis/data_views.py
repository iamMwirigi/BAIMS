from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime, date
from .authentication import TokenAuthentication, AdminTokenAuthentication, BaTokenAuthentication
from rest_framework.permissions import IsAuthenticated
from .models import (
    User, UAdmin, Ba, Agency, Project, FormSection, ProjectAssoc, InputOptions,
    AirtelCombined, CokeCombined, BaimsCombined, KspcaCombined, SaffCombined,
    BaProject
)


class WideDataFilterView(APIView):
    """
    View for filtering data from wide tables (airtel_combined, coke_combined, etc.)
    """
    authentication_classes = [TokenAuthentication, AdminTokenAuthentication, BaTokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Get filtered data from wide tables.
        
        Query Parameters:
        - table: The wide table name (airtel_combined, coke_combined, etc.)
        - ba_id: Filter by BA ID
        - start_date: Filter from date (YYYY-MM-DD)
        - end_date: Filter to date (YYYY-MM-DD)
        - project_id: Filter by project ID
        - fields: Comma-separated list of fields to include
        - limit: Number of records to return (default: 100)
        """
        try:
            # Get query parameters
            table_name = request.query_params.get('table')
            ba_id = request.query_params.get('ba_id')
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')
            project_id = request.query_params.get('project_id')
            fields = request.query_params.get('fields', '').split(',') if request.query_params.get('fields') else []
            limit = int(request.query_params.get('limit', 100))
            
            # Validate table name
            if not table_name:
                return Response({
                    'response': 'error',
                    'message': 'Table name is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get the model class based on table name
            model_class = self._get_model_class(table_name)
            if not model_class:
                return Response({
                    'response': 'error',
                    'message': f'Invalid table name: {table_name}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Build queryset
            queryset = model_class.objects.all()
            
            # Apply filters
            if ba_id:
                queryset = queryset.filter(ba_id=ba_id)

            if project_id:
                # Check if the model has a 'project' ForeignKey
                if hasattr(model_class, 'project') and isinstance(model_class._meta.get_field('project'), models.ForeignKey):
                    queryset = queryset.filter(project__id=project_id)
                else: # Fallback for models that might use IntegerField for project_id
                    available_fields = [f.name for f in model_class._meta.get_fields()]
                    project_field = None # Reset project_field
                    for candidate in ['project', 'project_id']:
                        if candidate in available_fields:
                            project_field = candidate
                            break
                    if project_field:
                        queryset = queryset.filter(**{project_field: project_id})
                # If neither field exists, skip filtering by project_id
            
            if start_date:
                try:
                    start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
                    queryset = queryset.filter(t_date__gte=start_date_obj) # Assuming t_date exists
                except ValueError:
                    return Response({
                        'response': 'error',
                        'message': 'Invalid start_date format. Use YYYY-MM-DD'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            if end_date: # Assuming t_date exists
                try:
                    end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
                    queryset = queryset.filter(t_date__lte=end_date_obj)
                except ValueError:
                    return Response({
                        'response': 'error',
                        'message': 'Invalid end_date format. Use YYYY-MM-DD'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Limit results
            queryset = queryset[:limit]
            
            # Get field names
            if fields and fields[0]:  # Check if fields is not empty
                # Filter to only include specified fields that exist in the model
                available_fields = [f.name for f in model_class._meta.get_fields()]
                valid_fields = [f for f in fields if f in available_fields]
                if not valid_fields:
                    return Response({
                        'response': 'error',
                        'message': f'No valid fields found. Available fields: {available_fields}'
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                # Get all fields
                valid_fields = [f.name for f in model_class._meta.get_fields()]
            
            # Serialize data
            data = []
            for obj in queryset:
                record = {}
                for field in valid_fields:
                    value = getattr(obj, field)
                    if isinstance(value, date):
                        value = value.isoformat()
                    record[field] = value
                data.append(record)
            
            return Response({
                'response': 'success',
                'table': table_name,
                'count': len(data),
                'data': data
            })
            
        except Exception as e:
            return Response({
                'response': 'error',
                'message': f'An error occurred: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _get_model_class(self, table_name):
        """Get the Django model class for a given table name"""
        table_mapping = {
            'airtel_combined': AirtelCombined,
            'coke_combined': CokeCombined,
            'baims_combined': BaimsCombined,
            'kspca_combined': KspcaCombined,
            'saff_combined': SaffCombined,
        }
        return table_mapping.get(table_name)


class ProjectDataView(APIView):
    """
    View for getting project data with form structure and actual data records
    """
    authentication_classes = [TokenAuthentication, AdminTokenAuthentication, BaTokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, project_id):
        """
        Get project data with forms, fields, and actual data records.
        
        Query Parameters:
        - ba_id: Filter by BA ID
        - start_date: Filter from date (YYYY-MM-DD)
        - end_date: Filter to date (YYYY-MM-DD)
        - include_data: Include actual data records (true/false)
        - data_table: Specify which data table to use
        """
        try:
            user = self.request.user
            # Get query parameters
            ba_id = request.query_params.get('ba_id')
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')
            include_data = request.query_params.get('include_data', 'false').lower() == 'true'
            data_table = request.query_params.get('data_table')
            
            # Get project, ensuring the user has permission
            try:
                allowed_projects = self._get_allowed_projects(user)
                project = allowed_projects.select_related('company').get(id=project_id)
            except Project.DoesNotExist:
                return Response({
                    'response': 'error',
                    'message': f'Project with ID {project_id} not found or you do not have permission to access it.'
                }, status=status.HTTP_404_NOT_FOUND)

            # Get form sections
            form_sections = FormSection.objects.filter(project=project).order_by('rank')
            
            forms_data = []
            for form_section in form_sections:
                form_data = self._get_form_data(
                    form_section, ba_id, start_date, end_date, include_data, data_table
                )
                if form_data:
                    forms_data.append(form_data)
            
            # Get agency name
            agency_name = project.company.name if project.company else "Unknown Agency"

            
            response_data = {
                "response": "success",
                "project_title": project.name,
                "code_name": project.name,
                "project_id": str(project.id),
                "company": agency_name,
                "forms": forms_data
            }
            
            return Response(response_data)
            
        except Exception as e:
            return Response({
                'response': 'error',
                'message': f'An error occurred: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _get_allowed_projects(self, user):
        """Returns a queryset of projects the user is allowed to see."""
        # UAdmin sees all projects
        if isinstance(user, UAdmin):
            return Project.objects.all()

        # BA sees projects they are assigned to via BaProject
        if isinstance(user, Ba):
            project_ids = BaProject.objects.filter(ba=user).values_list('project_id', flat=True)
            return Project.objects.filter(id__in=project_ids)

        # Regular User sees projects for their agency
        if hasattr(user, 'agency') and user.agency:
            return Project.objects.filter(company=user.agency.id)
            
        # Default to no projects
        return Project.objects.none()
    
    def _get_form_data(self, form_section, ba_id, start_date, end_date, include_data, data_table):
        """Get form data with fields and optionally data records"""
        # Get project associations (fields)
        project_assocs = ProjectAssoc.objects.filter(project=form_section.project).order_by('rank')
        
        fields_data = []
        for project_assoc in project_assocs:
            field_data = self._get_field_data(
                project_assoc, ba_id, start_date, end_date, include_data, data_table
            )
            if field_data:
                fields_data.append(field_data)
        
        return {
            "0": form_section.title,
            "form_title": form_section.title,
            "1": str(form_section.id),
            "form_id": str(form_section.id),
            "2": str(form_section.rank),
            "form_rank": str(form_section.rank),
            "3": "off",
            "location_status": "off",
            "4": "NO",
            "image_required": "NO",
            "form_fields": fields_data
        }
    
    def _get_field_data(self, project_assoc, ba_id, start_date, end_date, include_data, data_table):
        """Get field data with options and optionally data values"""
        # Get input options
        input_options = InputOptions.objects.filter(field=project_assoc).order_by('rank') # Use FK
        options_data = []
        for option in input_options:
            options_data.append({
                "0": option.title,
                "option_text": option.title,
                "1": str(option.rank),
                "option_rank": str(option.rank)
            })
        
        field_data = {
            "input_title": project_assoc.report_display_name,
            "field_id": project_assoc.column_name,
            "input_rank": str(project_assoc.rank),
            "field_type": project_assoc.field_type or "input",
            "multiple_choice": str(project_assoc.multiple).lower(),
            "options_available": str(project_assoc.options_available),
            "field_input_options": options_data
        }
        
        # If include_data is True, get actual data values
        if include_data and data_table:
            field_data['data_values'] = self._get_field_data_values(
                project_assoc.column_name, ba_id, start_date, end_date, data_table
            )
        
        return field_data
    
    def _get_field_data_values(self, column_name, ba_id, start_date, end_date, data_table):
        """Get actual data values for a specific field from the wide table"""
        try:
            # Get the model class
            model_class = self._get_model_class(data_table)
            if not model_class:
                return []
            
            # Build queryset
            queryset = model_class.objects.all()
            
            # Apply filters
            if ba_id and hasattr(model_class, 'ba'): # Check if model has a 'ba' FK
                queryset = queryset.filter(ba__id=ba_id)
            
            if start_date:
                start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
                queryset = queryset.filter(t_date__gte=start_date_obj) # Assuming t_date exists
            
            if end_date: # Assuming t_date exists
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
                queryset = queryset.filter(t_date__lte=end_date_obj)
            
            # Get values for the specific column
            values = list(queryset.values_list(column_name, flat=True))
            return [str(v) if v is not None else '' for v in values]
            
        except Exception as e:
            return []
    
    def _get_model_class(self, table_name):
        """Get the Django model class for a given table name"""
        table_mapping = {
            'airtel_combined': AirtelCombined,
            'coke_combined': CokeCombined,
            'baims_combined': BaimsCombined,
            'kspca_combined': KspcaCombined,
            'saff_combined': SaffCombined,
        }
        return table_mapping.get(table_name) 