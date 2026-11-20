from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.accounts import views as accounts_views
from apps.learning import views as learning_views
from apps.teacher_studio import views as studio_views
from apps.governance import views as governance_views
from apps.resources import views as resources_views
from apps.ai_gateway import views as ai_gateway_views
from apps.ai_gateway import views as ai_gateway_views
urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("apps.accounts.urls")),
    path("api/learning/", include("apps.learning.urls")),
    path("api/teacher/", include("apps.teacher_studio.urls")),
    path("api/governance/", include("apps.governance.urls")),
    path("", accounts_views.home, name="home"),
    path("learn/", learning_views.companion_page, name="companion"),
    path("studio/", studio_views.studio_page, name="studio"),
    path("governance/", governance_views.centre_page, name="governance"),
    path("ai-config/", ai_gateway_views.ai_config, name="ai_config"),
    path("onboard/", institutions_views.bulk_onboard, name="bulk_onboard"),
    path("ai-config/", ai_gateway_views.ai_config, name="ai_config"),
    path("onboard/", institutions_views.bulk_onboard, name="bulk_onboard"),
    path("upload/", resources_views.upload_resource, name="upload"),
    path("library/", resources_views.resource_library, name="library"),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)







