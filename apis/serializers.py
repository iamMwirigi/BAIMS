import sys
from rest_framework import serializers
from .models import (
    User, Agency, Project, ProjectHead, Branch, Outlet, UserOutlet,
    AirtelCombined, CokeCombined, BaimsCombined, KspcaCombined, SaffCombined,
    RedbullOutlet, TotalKenya, AppData, Ba, Backend, BaProject, ProjectAssoc,
    Containers, ContainerOptions, Coop, Coop2, FormSection, FormSubSection,
    InputGroup, InputOptions, UAdmin
)

# Agency Serializers
class AgencySerializer(serializers.ModelSerializer):
    """Serializer for Agency model"""
    
    class Meta:
        model = Agency
        fields = ['id', 'name', 'country', 'holding_table']
    
    def create(self, validated_data):
        """Create a new agency"""
        return Agency.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        """Update an existing agency"""
        instance.name = validated_data.get('name', instance.name)
        instance.country = validated_data.get('country', instance.country)
        instance.holding_table = validated_data.get('holding_table', instance.holding_table)
        instance.save()
        return instance

class AgencyListSerializer(serializers.ModelSerializer):
    """Serializer for listing agencies"""
    
    class Meta:
        model = Agency
        fields = ['id', 'name', 'country', 'holding_table']


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    agency = AgencySerializer(read_only=True)
    agency_id = serializers.PrimaryKeyRelatedField(
        queryset=Agency.objects.all(), source='agency', write_only=True, allow_null=True
    )

    class Meta:
        model = User
        fields = ['id', 'name', 'username', 'password', 'region', 'active_status', 'place_holder', 'agency', 'agency_id']
        extra_kwargs = {
            'password': {'write_only': True},  # Don't include password in responses
            'active_status': {'default': 1},
            'place_holder': {'default': 0}
        }
    
    def create(self, validated_data):
        """Create a new user"""
        return User.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        """Update an existing user"""
        instance.name = validated_data.get('name', instance.name)
        instance.username = validated_data.get('username', instance.username)
        instance.password = validated_data.get('password', instance.password)
        instance.region = validated_data.get('region', instance.region)
        instance.active_status = validated_data.get('active_status', instance.active_status)
        instance.place_holder = validated_data.get('place_holder', instance.place_holder)
        instance.agency = validated_data.get('agency', instance.agency)
        instance.save()
        return instance

class UserListSerializer(serializers.ModelSerializer):
    """Serializer for listing users (without password)"""
    agency = AgencyListSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'name', 'username', 'region', 'active_status', 'place_holder', 'agency']


# Project Serializers
class ProjectSerializer(serializers.ModelSerializer):
    """Serializer for Project model"""
    
    class Meta:
        model = Project
        fields = ['id', 'name', 'client', 'top_table', 'rank', 'combined', 'status', 'location_status', 'company', 'image_required']
        extra_kwargs = {
            'combined': {'default': 1},
            'status': {'default': 1},
            'location_status': {'default': 'off'},
            'image_required': {'default': 'NO'}
        }
    
    def create(self, validated_data):
        """Create a new project"""
        return Project.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        """Update an existing project"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class ProjectListSerializer(serializers.ModelSerializer):
    """Serializer for listing projects"""
    
    class Meta:
        model = Project
        fields = ['id', 'name', 'client', 'top_table', 'rank', 'combined', 'status', 'location_status', 'company', 'image_required']


# Project Head Serializers
class ProjectHeadSerializer(serializers.ModelSerializer):
    """Serializer for ProjectHead model"""
    
    class Meta:
        model = ProjectHead
        fields = ['id', 'name', 'company', 'start_date', 'end_date', 'aka_name']
    
    def create(self, validated_data):
        """Create a new project head"""
        return ProjectHead.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        """Update an existing project head"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class ProjectHeadListSerializer(serializers.ModelSerializer):
    """Serializer for listing project heads"""
    
    class Meta:
        model = ProjectHead
        fields = ['id', 'name', 'company', 'start_date', 'end_date', 'aka_name']


# Branch Serializers
class BranchSerializer(serializers.ModelSerializer):
    """Serializer for Branch model"""
    
    class Meta:
        model = Branch
        fields = ['id', 'name']
    
    def create(self, validated_data):
        """Create a new branch"""
        return Branch.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        """Update an existing branch"""
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        return instance

class BranchListSerializer(serializers.ModelSerializer):
    """Serializer for listing branches"""
    
    class Meta:
        model = Branch
        fields = ['id', 'name']


# Outlet Serializers
class OutletSerializer(serializers.ModelSerializer):
    """Serializer for Outlet model"""
    
    class Meta:
        model = Outlet
        fields = [
            'id', 'name', 'longitude', 'latitude', 't_date', 't_time', 'update_by',
            'photo', 'type', 'location', 'owner_name', 'contact', 'region',
            'outlet_location', 'items_given', 'feedback', 't_shirt', 'money_bag',
            'table_mat', 'parasol'
        ]
        extra_kwargs = {
            'longitude': {'default': 0},
            'latitude': {'default': 0},
            'update_by': {'default': 0},
            't_shirt': {'default': 0},
            'money_bag': {'default': 0},
            'table_mat': {'default': 0},
            'parasol': {'default': 0}
        }
    
    def create(self, validated_data):
        """Create a new outlet"""
        return Outlet.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        """Update an existing outlet"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class OutletListSerializer(serializers.ModelSerializer):
    """Serializer for listing outlets"""
    
    class Meta:
        model = Outlet
        fields = [
            'id', 'name', 'longitude', 'latitude', 't_date', 't_time', 'update_by',
            'photo', 'type', 'location', 'owner_name', 'contact', 'region',
            'outlet_location', 'items_given', 'feedback', 't_shirt', 'money_bag',
            'table_mat', 'parasol'
        ]


# User Outlet Serializers
class UserOutletSerializer(serializers.ModelSerializer):
    """Serializer for UserOutlet model"""
    
    class Meta:
        model = UserOutlet
        fields = ['id', 'user', 'outlet']
    
    def create(self, validated_data):
        """Create a new user outlet relationship"""
        return UserOutlet.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        """Update an existing user outlet relationship"""
        instance.user = validated_data.get('user', instance.user)
        instance.outlet = validated_data.get('outlet', instance.outlet)
        instance.save()
        return instance

class UserOutletListSerializer(serializers.ModelSerializer):
    """Serializer for listing user outlet relationships"""
    
    class Meta:
        model = UserOutlet
        fields = ['id', 'user', 'outlet']


# Data Collection Base Serializers
class DataCollectionBaseSerializer(serializers.ModelSerializer):
    """Base serializer for data collection models"""
    
    class Meta:
        abstract = True
        fields = ['id', 'project', 'image_url', 'longitude', 'latitude', 't_date']
    
    def create(self, validated_data):
        """Create a new data collection record"""
        return self.Meta.model.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        """Update an existing data collection record"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


# Airtel Combined Serializers
class AirtelCombinedSerializer(DataCollectionBaseSerializer):
    """Serializer for AirtelCombined model"""
    
    class Meta(DataCollectionBaseSerializer.Meta):
        model = AirtelCombined
        fields = ['id', 'project', 'image_url', 'longitude', 'latitude', 't_date']

class AirtelCombinedListSerializer(serializers.ModelSerializer):
    """Serializer for listing Airtel combined data"""
    
    class Meta:
        model = AirtelCombined
        fields = ['id', 'project', 'image_url', 'longitude', 'latitude', 't_date']


# Coke Combined Serializers
class CokeCombinedSerializer(DataCollectionBaseSerializer):
    """Serializer for CokeCombined model"""
    
    class Meta(DataCollectionBaseSerializer.Meta):
        model = CokeCombined
        fields = ['id', 'project', 'image_url', 'longitude', 'latitude', 't_date']

class CokeCombinedListSerializer(serializers.ModelSerializer):
    """Serializer for listing Coke combined data"""
    
    class Meta:
        model = CokeCombined
        fields = ['id', 'project', 'image_url', 'longitude', 'latitude', 't_date']


# Baims Combined Serializers
class BaimsCombinedSerializer(DataCollectionBaseSerializer):
    """Serializer for BaimsCombined model"""
    
    class Meta(DataCollectionBaseSerializer.Meta):
        model = BaimsCombined
        fields = ['id', 'project', 'image_url', 'longitude', 'latitude', 't_date']

class BaimsCombinedListSerializer(serializers.ModelSerializer):
    """Serializer for listing Baims combined data"""
    
    class Meta:
        model = BaimsCombined
        fields = ['id', 'project', 'image_url', 'longitude', 'latitude', 't_date']


# KPSCA Combined Serializers
class KspcaCombinedSerializer(DataCollectionBaseSerializer):
    """Serializer for KspcaCombined model"""
    
    class Meta(DataCollectionBaseSerializer.Meta):
        model = KspcaCombined
        fields = ['id', 'project', 'image_url', 'longitude', 'latitude', 't_date']

class KspcaCombinedListSerializer(serializers.ModelSerializer):
    """Serializer for listing KPSCA combined data"""
    
    class Meta:
        model = KspcaCombined
        fields = ['id', 'project', 'image_url', 'longitude', 'latitude', 't_date']


# Safaricom Combined Serializers
class SaffCombinedSerializer(DataCollectionBaseSerializer):
    """Serializer for SaffCombined model"""
    
    class Meta(DataCollectionBaseSerializer.Meta):
        model = SaffCombined
        fields = ['id', 'project', 'image_url', 'longitude', 'latitude', 't_date']

class SaffCombinedListSerializer(serializers.ModelSerializer):
    """Serializer for listing Safaricom combined data"""
    
    class Meta:
        model = SaffCombined
        fields = ['id', 'project', 'image_url', 'longitude', 'latitude', 't_date']


# Redbull Outlet Serializers
class RedbullOutletSerializer(serializers.ModelSerializer):
    """Serializer for RedbullOutlet model"""
    
    class Meta:
        model = RedbullOutlet
        fields = ['id']
    
    def create(self, validated_data):
        """Create a new redbull outlet"""
        return RedbullOutlet.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        """Update an existing redbull outlet"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class RedbullOutletListSerializer(serializers.ModelSerializer):
    """Serializer for listing redbull outlets"""
    
    class Meta:
        model = RedbullOutlet
        fields = ['id']


# Total Kenya Serializers
class TotalKenyaSerializer(serializers.ModelSerializer):
    """Serializer for TotalKenya model"""
    
    class Meta:
        model = TotalKenya
        fields = ['id']
    
    def create(self, validated_data):
        """Create a new total kenya record"""
        return TotalKenya.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        """Update an existing total kenya record"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class TotalKenyaListSerializer(serializers.ModelSerializer):
    """Serializer for listing total kenya data"""
    
    class Meta:
        model = TotalKenya
        fields = ['id']


# App Data Serializers
class AppDataSerializer(serializers.ModelSerializer):
    """Serializer for AppData model"""
    
    class Meta:
        model = AppData
        fields = ['id']
    
    def create(self, validated_data):
        """Create a new app data record"""
        return AppData.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        """Update an existing app data record"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class AppDataListSerializer(serializers.ModelSerializer):
    """Serializer for listing app data"""
    
    class Meta:
        model = AppData
        fields = ['id']


# BA Serializers
class BaSerializer(serializers.ModelSerializer):
    """Serializer for Ba model"""
    
    class Meta:
        model = Ba
        fields = ['id', 'name', 'phone', 'company', 'pass_code']
    
    def create(self, validated_data):
        """Create a new BA record"""
        print('Validated data for Ba:', validated_data, file=sys.stderr)
        return Ba.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        """Update an existing BA record"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class BaListSerializer(serializers.ModelSerializer):
    """Serializer for listing BA data"""
    
    class Meta:
        model = Ba
        fields = ['id', 'name', 'phone', 'company']


# Backend Serializers
class BackendSerializer(serializers.ModelSerializer):
    """Serializer for Backend model"""
    
    class Meta:
        model = Backend
        fields = ['id']
    
    def create(self, validated_data):
        """Create a new backend record"""
        return Backend.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        """Update an existing backend record"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class BackendListSerializer(serializers.ModelSerializer):
    """Serializer for listing backend data"""
    
    class Meta:
        model = Backend
        fields = ['id']


# BA Project Serializers
class BaProjectSerializer(serializers.ModelSerializer):
    """Serializer for BaProject model"""
    
    class Meta:
        model = BaProject
        fields = ['id']
    
    def create(self, validated_data):
        """Create a new BA project record"""
        return BaProject.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        """Update an existing BA project record"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class BaProjectListSerializer(serializers.ModelSerializer):
    """Serializer for listing BA project data"""
    
    class Meta:
        model = BaProject
        fields = ['id']


# Project Association Serializers
class ProjectAssocSerializer(serializers.ModelSerializer):
    """Serializer for ProjectAssoc model"""
    
    class Meta:
        model = ProjectAssoc
        fields = [
            'id', 'project', 'report_display_name', 'column_name', 'rank',
            'field_type', 'multiple', 'options_available', 'options_id',
            'formula_id'
        ]
    
    def create(self, validated_data):
        """Create a new project association record"""
        return ProjectAssoc.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        """Update an existing project association record"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class ProjectAssocListSerializer(serializers.ModelSerializer):
    """Serializer for listing project association data"""
    
    class Meta:
        model = ProjectAssoc
        fields = [
            'id', 'project', 'report_display_name', 'column_name', 'rank',
            'field_type', 'multiple', 'options_available', 'options_id',
            'formula_id'
        ]


# Containers Serializers
class ContainersSerializer(serializers.ModelSerializer):
    """Serializer for Containers model"""
    
    class Meta:
        model = Containers
        fields = ['id']
    
    def create(self, validated_data):
        """Create a new container record"""
        return Containers.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        """Update an existing container record"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class ContainersListSerializer(serializers.ModelSerializer):
    """Serializer for listing containers"""
    
    class Meta:
        model = Containers
        fields = ['id']


# Container Options Serializers
class ContainerOptionsSerializer(serializers.ModelSerializer):
    """Serializer for ContainerOptions model"""
    
    class Meta:
        model = ContainerOptions
        fields = ['id']
    
    def create(self, validated_data):
        """Create a new container option record"""
        return ContainerOptions.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        """Update an existing container option record"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class ContainerOptionsListSerializer(serializers.ModelSerializer):
    """Serializer for listing container options"""
    
    class Meta:
        model = ContainerOptions
        fields = ['id']


# Coop Serializers
class CoopSerializer(serializers.ModelSerializer):
    """Serializer for Coop model"""
    
    class Meta:
        model = Coop
        fields = ['id']
    
    def create(self, validated_data):
        """Create a new coop record"""
        return Coop.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        """Update an existing coop record"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class CoopListSerializer(serializers.ModelSerializer):
    """Serializer for listing coop data"""
    
    class Meta:
        model = Coop
        fields = ['id']


# Coop2 Serializers
class Coop2Serializer(serializers.ModelSerializer):
    """Serializer for Coop2 model"""
    
    class Meta:
        model = Coop2
        fields = ['id']
    
    def create(self, validated_data):
        """Create a new coop2 record"""
        return Coop2.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        """Update an existing coop2 record"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class Coop2ListSerializer(serializers.ModelSerializer):
    """Serializer for listing coop2 data"""
    
    class Meta:
        model = Coop2
        fields = ['id']


# Form Section Serializers
class FormSectionSerializer(serializers.ModelSerializer):
    """Serializer for FormSection model"""
    
    class Meta:
        model = FormSection
        fields = ['id']
    
    def create(self, validated_data):
        """Create a new form section record"""
        return FormSection.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        """Update an existing form section record"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class FormSectionListSerializer(serializers.ModelSerializer):
    """Serializer for listing form sections"""
    
    class Meta:
        model = FormSection
        fields = ['id']


# Form Sub Section Serializers
class FormSubSectionSerializer(serializers.ModelSerializer):
    """Serializer for FormSubSection model"""
    
    class Meta:
        model = FormSubSection
        fields = ['id']
    
    def create(self, validated_data):
        """Create a new form sub section record"""
        return FormSubSection.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        """Update an existing form sub section record"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class FormSubSectionListSerializer(serializers.ModelSerializer):
    """Serializer for listing form sub sections"""
    
    class Meta:
        model = FormSubSection
        fields = ['id']


# Input Group Serializers
class InputGroupSerializer(serializers.ModelSerializer):
    """Serializer for InputGroup model"""
    
    class Meta:
        model = InputGroup
        fields = ['id']
    
    def create(self, validated_data):
        """Create a new input group record"""
        return InputGroup.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        """Update an existing input group record"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class InputGroupListSerializer(serializers.ModelSerializer):
    """Serializer for listing input groups"""
    
    class Meta:
        model = InputGroup
        fields = ['id']


# Input Options Serializers
class InputOptionsSerializer(serializers.ModelSerializer):
    """Serializer for InputOptions model"""
    
    class Meta:
        model = InputOptions
        fields = ['id']
    
    def create(self, validated_data):
        """Create a new input option record"""
        return InputOptions.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        """Update an existing input option record"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class InputOptionsListSerializer(serializers.ModelSerializer):
    """Serializer for listing input options"""
    
    class Meta:
        model = InputOptions
        fields = ['id'] 


# UAdmin Serializer
class UAdminSerializer(serializers.ModelSerializer):
    """Serializer for UAdmin model"""
    
    class Meta:
        model = UAdmin
        fields = ['id', 'name', 'u_name', 'p_phrase', 'powers']
        extra_kwargs = {
            'p_phrase': {'write_only': True},  # Don't include password in responses
        }
    
    def create(self, validated_data):
        """Create a new admin user"""
        return UAdmin.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        """Update an existing admin user"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


# Nested Serializers for Rich API Responses
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
    field_input_options = InputOptionsNestedSerializer(many=True, read_only=True, source='inputoptions_set')
    
    class Meta:
        model = ProjectAssoc
        fields = [
            'id', 'report_display_name', 'column_name', 'rank', 
            'field_type', 'input_type', 'options_available', 'multiple', 'field_input_options'
        ]
    
    def to_representation(self, instance):
        """Custom representation to match the expected format"""
        # Get input options for this field
        input_options = InputOptions.objects.filter(field_id=instance.id)
        options_data = InputOptionsNestedSerializer(input_options, many=True).data
        
        return {
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
    form_fields = ProjectAssocNestedSerializer(many=True, read_only=True)
    
    class Meta:
        model = FormSection
        fields = ['id', 'title', 'rank', 'project', 'form_fields']
    
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
    forms = FormSectionNestedSerializer(many=True, read_only=True)
    
    class Meta:
        model = Project
        fields = ['id', 'name', 'client', 'company', 'forms']
    
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
    projects = ProjectNestedSerializer(many=True, read_only=True)
    
    class Meta:
        model = Ba
        fields = ['id', 'name', 'phone', 'company', 'projects']
    
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