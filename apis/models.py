from django.db import models
import secrets

# Create your models here.

class User(models.Model):
    """User model representing field agents/users"""
    name = models.CharField(max_length=64)
    username = models.CharField(max_length=64, unique=True)
    password = models.CharField(max_length=64)
    region = models.CharField(max_length=64)
    active_status = models.IntegerField(default=1)
    place_holder = models.IntegerField(default=0)
    agency = models.ForeignKey('Agency', on_delete=models.CASCADE, related_name='users', null=True, blank=True)
    
    class Meta:
        db_table = 'user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.name} ({self.username})"
    
    @property
    def is_active(self):
        """Check if user is active"""
        return self.active_status == 1


class Agency(models.Model):
    """Agency model representing companies/agencies"""
    name = models.CharField(max_length=128)
    country = models.CharField(max_length=64)
    holding_table = models.TextField()
    
    class Meta:
        db_table = 'agency'
        verbose_name = 'Agency'
        verbose_name_plural = 'Agencies'
    
    def __str__(self):
        return f"{self.name} ({self.country})"


class Project(models.Model):
    """Project model representing different projects"""
    name = models.TextField()
    client = models.TextField()
    top_table = models.TextField()
    rank = models.IntegerField()
    combined = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    location_status = models.CharField(max_length=64, default='off')
    company = models.IntegerField()
    image_required = models.CharField(max_length=64, default='NO')
    
    class Meta:
        db_table = 'project'
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'
    
    def __str__(self):
        return f"{self.name} ({self.client})"
    
    @property
    def is_active(self):
        """Check if project is active"""
        return self.status == 1


class ProjectHead(models.Model):
    """Project Head model representing project managers"""
    name = models.CharField(max_length=128)
    company = models.IntegerField()
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    aka_name = models.CharField(max_length=128)
    
    class Meta:
        db_table = 'project_head'
        verbose_name = 'Project Head'
        verbose_name_plural = 'Project Heads'
    
    def __str__(self):
        return f"{self.name} ({self.aka_name})"


class Branch(models.Model):
    """Branch model representing branch locations"""
    name = models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = 'branch'
        verbose_name = 'Branch'
        verbose_name_plural = 'Branches'
    
    def __str__(self):
        return self.name or f"Branch {self.id}"


class Outlet(models.Model):
    """Outlet model representing retail outlets/stores"""
    name = models.TextField(null=True, blank=True)
    longitude = models.FloatField(default=0)
    latitude = models.FloatField(default=0)
    t_date = models.DateField(null=True, blank=True)
    t_time = models.TimeField(null=True, blank=True)
    update_by = models.IntegerField(default=0)
    photo = models.TextField(null=True, blank=True)
    type = models.CharField(max_length=64, null=True, blank=True)
    location = models.CharField(max_length=128, null=True, blank=True)
    owner_name = models.CharField(max_length=128, null=True, blank=True)
    contact = models.CharField(max_length=128, null=True, blank=True)
    region = models.TextField(null=True, blank=True)
    outlet_location = models.TextField(null=True, blank=True)
    items_given = models.TextField(null=True, blank=True)
    feedback = models.TextField(null=True, blank=True)
    t_shirt = models.IntegerField(default=0)
    money_bag = models.IntegerField(default=0)
    table_mat = models.IntegerField(default=0)
    parasol = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'outlet'
        verbose_name = 'Outlet'
        verbose_name_plural = 'Outlets'
    
    def __str__(self):
        return self.name or f"Outlet {self.id}"


class UserOutlet(models.Model):
    """User Outlet model representing many-to-many relationship between users and outlets"""
    user = models.IntegerField()
    outlet = models.IntegerField()
    
    class Meta:
        db_table = 'user_outlet'
        verbose_name = 'User Outlet'
        verbose_name_plural = 'User Outlets'
    
    def __str__(self):
        return f"User {self.user} - Outlet {self.outlet}"


class UAdmin(models.Model):
    """Admin User model for authentication, matching the u_admin table schema"""
    name = models.TextField(null=True, blank=True)
    u_name = models.TextField()
    p_phrase = models.TextField()
    powers = models.CharField(max_length=64)
    
    class Meta:
        db_table = 'u_admin'
        verbose_name = 'Admin User'
        verbose_name_plural = 'Admin Users'

    def __str__(self):
        return self.u_name

    @property
    def is_authenticated(self):
        return True


class AdminAuthToken(models.Model):
    """Stores authentication tokens for admin users"""
    key = models.CharField(max_length=40, primary_key=True)
    admin = models.ForeignKey(
        UAdmin, related_name='auth_tokens', on_delete=models.CASCADE, verbose_name="Admin User"
    )
    created = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super().save(*args, **kwargs)

    def generate_key(self):
        return secrets.token_hex(20)

    def __str__(self):
        return self.key


class BaAuthToken(models.Model):
    """Stores authentication tokens for BA users"""
    key = models.CharField(max_length=40, primary_key=True)
    ba = models.ForeignKey(
        'Ba', related_name='auth_tokens', on_delete=models.CASCADE, verbose_name="BA User"
    )
    created = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super().save(*args, **kwargs)

    def generate_key(self):
        return secrets.token_hex(20)

    def __str__(self):
        return self.key


# Data collection tables (these are large tables with many fields)
# For now, I'll create a generic model that can be extended

class DataCollectionBase(models.Model):
    """Base model for data collection tables"""
    project = models.IntegerField()
    image_url = models.TextField(null=True, blank=True)
    longitude = models.TextField(null=True, blank=True)
    latitude = models.TextField(null=True, blank=True)
    t_date = models.DateField(auto_now_add=True)
    
    class Meta:
        abstract = True


class AirtelCombined(DataCollectionBase):
    """Airtel combined data collection table"""
    # This table has many sub_1_* fields (sub_1_1 to sub_1_41)
    # For now, I'll add a few key fields and use a JSON field for the rest
    
    class Meta:
        db_table = 'airtel_combined'
        verbose_name = 'Airtel Combined Data'
        verbose_name_plural = 'Airtel Combined Data'


class CokeCombined(DataCollectionBase):
    """Coke combined data collection table"""
    
    class Meta:
        db_table = 'coke_combined'
        verbose_name = 'Coke Combined Data'
        verbose_name_plural = 'Coke Combined Data'


class BaimsCombined(DataCollectionBase):
    """Baims combined data collection table"""
    
    class Meta:
        db_table = 'baims_combined'
        verbose_name = 'Baims Combined Data'
        verbose_name_plural = 'Baims Combined Data'


class KspcaCombined(DataCollectionBase):
    """KPSCA combined data collection table"""
    
    class Meta:
        db_table = 'kspca_combined'
        verbose_name = 'KPSCA Combined Data'
        verbose_name_plural = 'KPSCA Combined Data'


class SaffCombined(DataCollectionBase):
    """Safaricom combined data collection table"""
    
    class Meta:
        db_table = 'saff_combined'
        verbose_name = 'Safaricom Combined Data'
        verbose_name_plural = 'Safaricom Combined Data'


class RedbullOutlet(models.Model):
    """Redbull outlet data collection table"""
    # This table structure wasn't fully visible in the SQL dump
    # Adding basic fields based on naming convention
    
    class Meta:
        db_table = 'redbull_outlet'
        verbose_name = 'Redbull Outlet'
        verbose_name_plural = 'Redbull Outlets'


class TotalKenya(models.Model):
    """Total Kenya data collection table"""
    
    class Meta:
        db_table = 'total_kenya'
        verbose_name = 'Total Kenya Data'
        verbose_name_plural = 'Total Kenya Data'


class AppData(models.Model):
    """App data table"""
    
    class Meta:
        db_table = 'app_data'
        verbose_name = 'App Data'
        verbose_name_plural = 'App Data'


class Ba(models.Model):
    """BA table"""
    name = models.CharField(max_length=128)
    phone = models.CharField(max_length=64)
    company = models.IntegerField()
    pass_code = models.CharField(max_length=1000)
    
    class Meta:
        db_table = 'ba'
        verbose_name = 'BA'
        verbose_name_plural = 'BAs'


class Backend(models.Model):
    """Backend table"""
    
    class Meta:
        db_table = 'backend'
        verbose_name = 'Backend'
        verbose_name_plural = 'Backends'


class BaProject(models.Model):
    """BA Project table"""
    ba_id = models.IntegerField()
    project_id = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    
    class Meta:
        db_table = 'ba_project'
        verbose_name = 'BA Project'
        verbose_name_plural = 'BA Projects'


class ProjectAssoc(models.Model):
    """Project Association table"""
    project = models.IntegerField()
    report_display_name = models.TextField()
    column_name = models.TextField()
    rank = models.IntegerField()
    field_type = models.CharField(max_length=128)
    multiple = models.IntegerField()
    options_available = models.IntegerField()
    options_id = models.IntegerField()
    formula_id = models.IntegerField()
    
    class Meta:
        db_table = 'project_assoc'
        verbose_name = 'Project Association'
        verbose_name_plural = 'Project Associations'


class Containers(models.Model):
    """Containers table"""
    
    class Meta:
        db_table = 'containers'
        verbose_name = 'Container'
        verbose_name_plural = 'Containers'


class ContainerOptions(models.Model):
    """Container Options table"""
    
    class Meta:
        db_table = 'container_options'
        verbose_name = 'Container Option'
        verbose_name_plural = 'Container Options'


class Coop(models.Model):
    """Coop table"""
    
    class Meta:
        db_table = 'coop'
        verbose_name = 'Coop'
        verbose_name_plural = 'Coops'


class Coop2(models.Model):
    """Coop2 table"""
    
    class Meta:
        db_table = 'coop2'
        verbose_name = 'Coop2'
        verbose_name_plural = 'Coop2s'


class FormSection(models.Model):
    """Form Section table"""
    
    class Meta:
        db_table = 'form_section'
        verbose_name = 'Form Section'
        verbose_name_plural = 'Form Sections'


class FormSubSection(models.Model):
    """Form Sub Section table"""
    
    class Meta:
        db_table = 'form_sub_section'
        verbose_name = 'Form Sub Section'
        verbose_name_plural = 'Form Sub Sections'


class InputGroup(models.Model):
    """Input Group table"""
    
    class Meta:
        db_table = 'input_group'
        verbose_name = 'Input Group'
        verbose_name_plural = 'Input Groups'


class InputOptions(models.Model):
    """Input Options table"""
    field_id = models.IntegerField()
    title = models.TextField()
    rank = models.IntegerField()
    next_section = models.IntegerField()
    value = models.IntegerField()
    container_id = models.IntegerField()
    
    class Meta:
        db_table = 'input_options'
        verbose_name = 'Input Option'
        verbose_name_plural = 'Input Options'


class AuthToken(models.Model):
    """Stores authentication tokens for custom users"""
    key = models.CharField(max_length=40, primary_key=True)
    user = models.ForeignKey(
        User, related_name='auth_tokens', on_delete=models.CASCADE, verbose_name="User"
    )
    created = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super().save(*args, **kwargs)

    def generate_key(self):
        return secrets.token_hex(20)

    def __str__(self):
        return self.key
