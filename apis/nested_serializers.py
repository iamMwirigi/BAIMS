from rest_framework import serializers
from .models import (
    Ba, Agency, Project, FormSection, ProjectAssoc, InputOptions
)


class InputOptionsNestedSerializer(serializers.ModelSerializer):
    """Nested serializer for input options with proper field mapping"""
    
    class Meta:
        model = InputOptions
        fields = ['id', 'title', 'rank']
    
    def to_representation(self, instance):
        """Custom representation to match the expected format"""
        return {
            "0": instance.title,
            "option_text": instance.title,
            "1": str(instance.rank),
            "option_rank": str(instance.rank)
        }


class ProjectAssocNestedSerializer(serializers.ModelSerializer):
    """Nested serializer for project associations with input options"""
    
    class Meta:
        model = ProjectAssoc
        fields = [
            'id', 'report_display_name', 'column_name', 'rank', 
            'field_type', 'input_type', 'options_available', 'multiple'
        ]
    
    def to_representation(self, instance):
        """Custom representation to match the expected format"""
        # Get input options for this field
        input_options = InputOptions.objects.filter(field_id=instance.id)
        options_data = InputOptionsNestedSerializer(input_options, many=True).data
        
        return {
            "id": instance.id,
            "input_title": instance.report_display_name,
            "field_id": instance.column_name,
            "input_rank": str(instance.rank),
            "field_type": instance.field_type or "input",
            "multiple_choice": str(instance.multiple).lower(),
            "options_available": str(instance.options_available),
            "field_input_options": options_data
        }


class FormSectionNestedSerializer(serializers.ModelSerializer):
    """Nested serializer for form sections"""
    
    class Meta:
        model = FormSection
        fields = ['id', 'title', 'rank', 'project']
    
    def to_representation(self, instance):
        """Custom representation to match the expected format"""
        # Get project associations for this section
        project_assocs = ProjectAssoc.objects.filter(project=instance.project).order_by('rank')
        fields_data = ProjectAssocNestedSerializer(project_assocs, many=True).data
        
        return {
            "0": instance.title,
            "form_title": instance.title,
            "1": str(instance.id),
            "form_id": str(instance.id),
            "2": str(instance.rank),
            "form_rank": str(instance.rank),
            "3": "off",  # location_status - default value
            "location_status": "off",
            "4": "NO",   # image_required - default value
            "image_required": "NO",
            "form_fields": fields_data
        }


class ProjectNestedSerializer(serializers.ModelSerializer):
    """Nested serializer for projects with forms"""
    
    class Meta:
        model = Project
        fields = ['id', 'name', 'client', 'company']
    
    def to_representation(self, instance):
        """Custom representation to match the expected format"""
        # Get form sections for this project
        form_sections = FormSection.objects.filter(project=instance.id).order_by('rank')
        forms_data = FormSectionNestedSerializer(form_sections, many=True).data
        
        return {
            "project_title": instance.name,
            "code_name": instance.name,
            "project_id": str(instance.id),
            "start_date": "2025-06-11",  # Default date - you might want to get this from BaProject
            "end_date": "2025-06-11",    # Default date - you might want to get this from BaProject
            "forms": forms_data
        }


class BaNestedSerializer(serializers.ModelSerializer):
    """Nested serializer for BA with projects"""
    
    class Meta:
        model = Ba
        fields = ['id', 'name', 'phone', 'company']
    
    def to_representation(self, instance):
        """Custom representation to match the expected format"""
        # Get agency name
        agency_name = "Unknown Agency"
        try:
            agency = Agency.objects.get(id=instance.company)
            agency_name = agency.name
        except Agency.DoesNotExist:
            pass
        
        # Get projects for this BA's company
        projects = Project.objects.filter(company=instance.company, status=1).order_by('rank')
        projects_data = ProjectNestedSerializer(projects, many=True).data
        
        return {
            "response": "success",
            "name": instance.name,
            "ba_id": str(instance.id),
            "company": agency_name,
            "projects": projects_data
        } 