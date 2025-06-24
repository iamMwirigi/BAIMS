from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime, date
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
                    ba = Ba.objects.get(id=ba_id)
                except Ba.DoesNotExist:
                    return Response({
                        'response': 'error',
                        'message': f'BA with ID {ba_id} not found'
                    }, status=status.HTTP_404_NOT_FOUND)
                
                # Apply filters
                ba = self._apply_filters(ba, start_date, end_date, project_id, form_id, company)
                serializer = BaNestedSerializer(ba)
                return Response(serializer.data)
            
            # If no ba_id, get all BAs with filters
            queryset = Ba.objects.all()
            
            # Apply company filter
            if company:
                try:
                    agency = Agency.objects.get(name__icontains=company)
                    queryset = queryset.filter(company=agency.id)
                except Agency.DoesNotExist:
                    return Response({
                        'response': 'error',
                        'message': f'Company {company} not found'
                    }, status=status.HTTP_404_NOT_FOUND)
            
            # Get BAs and apply filters
            bas = []
            for ba in queryset:
                filtered_ba = self._apply_filters(ba, start_date, end_date, project_id, form_id, company)
                if filtered_ba:
                    serializer = BaNestedSerializer(filtered_ba)
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
    
    def _apply_filters(self, ba, start_date, end_date, project_id, form_id, company):
        """
        Apply filters to BA data and return filtered BA object
        """
        # Get projects for this BA's company
        projects = Project.objects.filter(company=ba.company, status=1).order_by('rank')
        
        # Apply project filter
        if project_id:
            try:
                projects = projects.filter(id=project_id)
            except ValueError:
                return None
        
        # Apply date filters (if you have date fields in your data)
        if start_date or end_date:
            # This would need to be implemented based on your data structure
            # For now, we'll just pass through
            pass
        
        # Apply form filter
        if form_id:
            # Filter projects that have the specified form
            projects_with_form = []
            for project in projects:
                if FormSection.objects.filter(id=form_id, project=project.id).exists():
                    projects_with_form.append(project)
            projects = projects_with_form
        
        # Create a temporary BA object with filtered projects
        ba.projects = projects
        return ba


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
                ba = Ba.objects.get(id=ba_id)
            except Ba.DoesNotExist:
                return Response({
                    'response': 'error',
                    'message': f'BA with ID {ba_id} not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Get agency name
            agency_name = "Unknown Agency"
            try:
                agency = Agency.objects.get(id=ba.company)
                agency_name = agency.name
            except Agency.DoesNotExist:
                pass
            
            # Get projects
            projects = Project.objects.filter(company=ba.company, status=1).order_by('rank')
            
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
        form_sections = FormSection.objects.filter(project=project.id).order_by('rank')
        
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
            field_data = self._get_field_data(project_assoc, ba, start_date, end_date, include_data)
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
    
    def _get_field_data(self, project_assoc, ba, start_date, end_date, include_data):
        """
        Get field data with options and optionally data values
        """
        # Get input options
        input_options = InputOptions.objects.filter(field_id=project_assoc.id)
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
        
        # If include_data is True, you could add actual data values here
        # This would require querying the wide data tables (airtel_combined, etc.)
        if include_data:
            # This is where you'd add logic to get actual data values
            # from the wide tables based on the column_name
            pass
        
        return field_data 