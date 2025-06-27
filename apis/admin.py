from django.contrib import admin
from .models import (
    User, Agency, Project, ProjectHead, Branch, Outlet, UserOutlet, UAdmin, UAdminAgency, AdminAuthToken, BaAuthToken,
    AirtelCombined, CokeCombined, BaimsCombined, KspcaCombined, SaffCombined, RedbullOutlet, TotalKenya, AppData, Ba, Backend, BaProject, ProjectAssoc, Containers, ContainerOptions, Coop, Coop2, FormSection, FormSubSection, InputGroup, InputOptions, AuthToken, FormSubmission
)

models_to_register = [
    User, Agency, Project, ProjectHead, Branch, Outlet, UserOutlet, UAdmin, UAdminAgency, AdminAuthToken, BaAuthToken,
    AirtelCombined, CokeCombined, BaimsCombined, KspcaCombined, SaffCombined, RedbullOutlet, TotalKenya, AppData, Ba, Backend, BaProject, ProjectAssoc, Containers, ContainerOptions, Coop, Coop2, FormSection, FormSubSection, InputGroup, InputOptions, AuthToken, FormSubmission
]

for model in models_to_register:
    admin.site.register(model)
