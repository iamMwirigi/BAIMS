from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, AgencyViewSet, ProjectViewSet, ProjectHeadViewSet, BranchViewSet,
    OutletViewSet, UserOutletViewSet, AirtelCombinedViewSet, CokeCombinedViewSet,
    BaimsCombinedViewSet, KspcaCombinedViewSet, SaffCombinedViewSet,
    RedbullOutletViewSet, TotalKenyaViewSet, AppDataViewSet, BaViewSet,
    BackendViewSet, BaProjectViewSet, ProjectAssocViewSet, ContainersViewSet,
    ContainerOptionsViewSet, CoopViewSet, Coop2ViewSet, FormSectionViewSet,
    FormSubSectionViewSet, InputGroupViewSet, InputOptionsViewSet, LoginView,
    AdminLoginView, UAdminViewSet, BaLoginView, ProjectHeadWithProjectsView,
    ProjectFormFieldsView
)
from .rich_views import BaRichDataView, BaDataWithRecordsView
from .data_views import WideDataFilterView, ProjectDataView

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'agencies', AgencyViewSet, basename='agency')
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'forms', ProjectViewSet, basename='project')
router.register(r'project-heads', ProjectHeadViewSet, basename='projecthead')
router.register(r'branches', BranchViewSet, basename='branch')
router.register(r'outlets', OutletViewSet, basename='outlet')
router.register(r'user-outlets', UserOutletViewSet, basename='useroutlet')
router.register(r'data/airtel-combined', AirtelCombinedViewSet, basename='airtelcombined')
router.register(r'data/coke-combined', CokeCombinedViewSet, basename='cokecombined')
router.register(r'data/baims-combined', BaimsCombinedViewSet, basename='baimscombined')
router.register(r'data/kspca-combined', KspcaCombinedViewSet, basename='kspcacombined')
router.register(r'data/saff-combined', SaffCombinedViewSet, basename='saffcombined')
router.register(r'data/redbull-outlet', RedbullOutletViewSet, basename='redbulloutlet')
router.register(r'data/total-kenya', TotalKenyaViewSet, basename='totalkenya')
router.register(r'data/app-data', AppDataViewSet, basename='appdata')
router.register(r'data/ba', BaViewSet, basename='ba')
router.register(r'data/backend', BackendViewSet, basename='backend')
router.register(r'data/ba-project', BaProjectViewSet, basename='baproject')
router.register(r'data/project-assoc', ProjectAssocViewSet, basename='projectassoc')
router.register(r'data/containers', ContainersViewSet, basename='containers')
router.register(r'data/container-options', ContainerOptionsViewSet, basename='containeroptions')
router.register(r'data/coop', CoopViewSet, basename='coop')
router.register(r'data/coop2', Coop2ViewSet, basename='coop2')
router.register(r'data/form-section', FormSectionViewSet, basename='formsection')
router.register(r'data/form-sub-section', FormSubSectionViewSet, basename='formsubsection')
router.register(r'data/input-group', InputGroupViewSet, basename='inputgroup')
router.register(r'data/input-options', InputOptionsViewSet, basename='inputoptions')
router.register(r'u-admin', UAdminViewSet, basename='u-admin')

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('admin-login/', AdminLoginView.as_view(), name='admin-login'),
    path('ba-login/', BaLoginView.as_view(), name='ba-login'),
    
    # Rich API endpoints
    path('rich/ba/<int:ba_id>/', BaRichDataView.as_view(), name='ba-rich-data'),
    path('rich/ba/', BaRichDataView.as_view(), name='ba-rich-data-all'),
    path('rich/ba/<int:ba_id>/with-data/', BaDataWithRecordsView.as_view(), name='ba-data-with-records'),
    
    # Data filtering endpoints
    path('data/filter/', WideDataFilterView.as_view(), name='wide-data-filter'),
    path('data/project/<int:project_id>/', ProjectDataView.as_view(), name='project-data'),
    
    path('project-heads-with-forms/', ProjectHeadWithProjectsView.as_view(), name='project-heads-with-forms'),
    path('project-form-fields/', ProjectFormFieldsView.as_view(), name='project-form-fields'),
    path('project-form-fields/<int:project_id>/', ProjectFormFieldsView.as_view(), name='project-form-fields-by-id'),
    path('project-form-fields/form-field/<int:form_field_id>/', ProjectFormFieldsView.as_view(), name='project-form-field-detail'),
    
    path('', include(router.urls)),
]
