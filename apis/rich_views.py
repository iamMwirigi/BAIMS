from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
from .models import Ba, Agency, Project, FormSection, ProjectAssoc, InputOptions
from .nested_serializers import BaNestedSerializer


class BaRichDataView(APIView):
    """
    Rich API endpoint that returns BA data with nested projects, forms, and fields.
    Supports filtering by date, project, and other parameters.
    """
    
    def get(self, request, ba_id=None):
        """
        Get rich BA data with nested structure.
        
        Query Parameters:
        - start_date: Filter data from this date (YYYY-MM-DD)
        - end_date: Filter data to this date (YYYY-MM-DD)
        - project_id: Filter by specific project
        - form_id: Filter by specific form
        - company: Filter by company/agency
        """
        try:
            # Get query parameters for filtering
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')
            project_id = request.query_params.get('project_id')
            form_id = request.query_params.get('form_id')
            company = request.query_params.get('company')
            
            # If ba_id is provided, get specific BA
            if ba_id:
                try:
                    ba = Ba.objects.select_related('company').get(id=ba_id) # Optimize query
                except Ba.DoesNotExist:
                    return Response({
                        'response': 'error',
                        'message': f'BA with ID {ba_id} not found'
                    }, status=status.HTTP_404_NOT_FOUND)
                
                # Apply filters
                ba.projects = self._get_filtered_projects(ba, start_date, end_date, project_id, form_id) # Assign filtered projects
                serializer = BaNestedSerializer(ba)
                return Response(serializer.data)
            
            # If no ba_id, get all BAs with filters
            queryset = Ba.objects.all()
            
            # Apply company filter
            if company:
                try:
                    agency = Agency.objects.get(name__icontains=company) # Case-insensitive search
                    queryset = queryset.filter(company=agency.id)
                except Agency.DoesNotExist:
                    return Response({
                        'response': 'error',
                        'message': f'Company {company} not found'
                    }, status=status.HTTP_404_NOT_FOUND)
            
            # Get BAs and apply filters
            bas = []
            for ba in queryset:
                ba.projects = self._get_filtered_projects(ba, start_date, end_date, project_id, form_id)
                if ba.projects.exists(): # Only include BA if they have projects after filtering
                    serializer = BaNestedSerializer(ba)
                    bas.append(serializer.data)
            
            return Response({
                'response': 'success',
                'count': len(bas),
                'data': bas
            })
            
        except Exception as e:
            return Response({
                'response': 'error',
                'message': f'An error occurred: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _get_filtered_projects(self, ba, start_date, end_date, project_id, form_id):
        """
        Apply filters to projects associated with a BA's company and return a filtered queryset.
        """
        # Get projects for this BA's company
        projects = Project.objects.filter(company=ba.company, status=True).order_by('rank') \
            .prefetch_related('form_sections__associations__input_options') # Optimize queries
        # Apply project filter
        if project_id:
            try:
                projects = projects.filter(id=project_id)
            except ValueError:
                return None
        
        # Apply date filters (if you have date fields in your data)
        # Assuming start_date/end_date apply to project's start/end dates
        if start_date or end_date:
            if start_date:
                try:
                    start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
                    projects = projects.filter(start_date__gte=start_date_obj)
                except ValueError:
                    pass # Invalid date format, ignore filter
            if end_date:
                try:
                    end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
                    projects = projects.filter(end_date__lte=end_date_obj)
                except ValueError:
                    pass # Invalid date format, ignore filter
        
        # Apply form filter
        if form_id:
            projects = projects.filter(form_sections__id=form_id).distinct()

        return projects


class BaDataWithRecordsView(APIView):
    """
    Enhanced API endpoint that returns BA data with actual data records from wide tables.
    """
    
    def get(self, request, ba_id):
        """
        Get BA data with projects, forms, fields, and actual data records.
        
        Query Parameters:
        - start_date: Filter data from this date (YYYY-MM-DD)
        - end_date: Filter data to this date (YYYY-MM-DD)
        - project_id: Filter by specific project
        - include_data: Include actual data records (true/false)
        """
        try:
            # Get query parameters
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')
            project_id = request.query_params.get('project_id')
            include_data = request.query_params.get('include_data', 'false').lower() == 'true'
            
            # Get BA
            try:
                ba = Ba.objects.select_related('company').get(id=ba_id) # Optimize query
            except Ba.DoesNotExist:
                return Response({
                    'response': 'error',
                    'message': f'BA with ID {ba_id} not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Get agency name
            agency_name = ba.company.name if ba.company else "Unknown Agency"
            
            # Get projects
            projects = Project.objects.filter(company=ba.company, status=True).order_by('rank') \
                .prefetch_related('form_sections__associations__input_options') # Optimize queries
            
            # Apply project filter
            if project_id:
                try:
                    projects = projects.filter(id=project_id)
                except ValueError:
                    return Response({
                        'response': 'error',
                        'message': f'Invalid project ID: {project_id}'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Build response
            projects_data = []
            for project in projects:
                project_data = self._get_project_data(project, ba, start_date, end_date, include_data)
                if project_data:
                    projects_data.append(project_data)
            
            response_data = {
                "response": "success",
                "name": ba.name,
                "ba_id": str(ba.id),
                "company": agency_name,
                "projects": projects_data
            }
            
            return Response(response_data)
            
        except Exception as e:
            return Response({
                'response': 'error',
                'message': f'An error occurred: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _get_project_data(self, project, ba, start_date, end_date, include_data):
        """
        Get project data with forms and optionally data records
        """
        # Get form sections
        form_sections = FormSection.objects.filter(project=project).order_by('rank')
        
        forms_data = []
        for form_section in form_sections:
            form_data = self._get_form_data(form_section, ba, start_date, end_date, include_data)
            if form_data:
                forms_data.append(form_data)
        
        return {
            "project_title": project.name,
            "code_name": project.name,
            "project_id": str(project.id),
            "start_date": "2025-06-11",  # You might want to get this from BaProject
            "end_date": "2025-06-11",    # You might want to get this from BaProject
            "forms": forms_data
        }
    
    def _get_form_data(self, form_section, ba, start_date, end_date, include_data):
        """
        Get form data with fields and optionally data records
        """
        # Get project associations (fields)
        project_assocs = ProjectAssoc.objects.filter(project=form_section.project).order_by('rank')
        
        fields_data = []
        for project_assoc in project_assocs:
            field_data = self._get_field_data(project_assoc)
            if field_data:
                fields_data.append(field_data)
        
        return {
            "form_title": form_section.title,
            "form_id": str(form_section.id),
            "form_rank": str(form_section.rank),
            "location_status": form_section.project.location_status,
            "image_required": form_section.project.image_required,
            "form_fields": fields_data
        }
    
    def _get_field_data(self, project_assoc):
        """
        Get field data with options and optionally data values
        """
        # Get input options
        input_options = InputOptions.objects.filter(field_id=project_assoc.id).order_by('rank')
        options_data = []
        for option in input_options:
            options_data.append({
                "option_text": option.title,
                "option_rank": str(option.rank)
            })
        
        return {
            "input_title": project_assoc.report_display_name,
            "field_id": project_assoc.column_name,
            "input_rank": str(project_assoc.rank),
            "field_type": project_assoc.field_type,
            "multiple_choice": str(project_assoc.multiple).lower(),
            "options_available": str(project_assoc.options_available),
            "field_input_options": options_data
        } 