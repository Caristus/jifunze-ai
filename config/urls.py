from apps.dashboard import analytics_views, api_docs_views
from apps.accounts import extra_views
from apps.accounts import bulk_views
from apps.governance import centre_views
from apps.learning import ask_views
from apps.learning import progress_views
from apps.resources import semantic_views
from apps.resources import library_views
from django.contrib import admin
from django.urls import path, include
from apps.institutions import views as institutions_views
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
    path("theme/set/<str:name>/", accounts_views.set_theme, name="set_theme"),
    path("api/learning/", include("apps.learning.urls")),
    path("api/teacher/", include("apps.teacher_studio.urls")),
    path("api/governance/", include("apps.governance.urls")),
    path("", accounts_views.home, name="home"),
    path("learn/", learning_views.companion_page, name="companion"),
    path("studio/", studio_views.studio_page, name="studio"),
    path("governance/", governance_views.centre_page, name="governance"),
    path("health/", governance_views.system_health, name="health"),
    path("health/", governance_views.system_health, name="health"),
    path("ai-config/", ai_gateway_views.ai_config, name="ai_config"),
    path("onboard/", institutions_views.bulk_onboard, name="bulk_onboard"),
    path("ai-config/", ai_gateway_views.ai_config, name="ai_config"),
    path("onboard/", institutions_views.bulk_onboard, name="bulk_onboard"),
    path("upload/", resources_views.upload_resource, name="upload"),
    path("library/", library_views.library_page, name="library"),
    path("api/learn/progress/", progress_views.progress),
    path("api/resources/semantic_search/", semantic_views.search),
    path("api/learn/ask/", ask_views.ask),
    path("api/learn/has_sources/", ask_views.has_sources),
    path("api/learn/history/", ask_views.history),
    path("onboard/", bulk_views.onboard_page),
    path("onboard/run/", bulk_views.onboard_run),
    path("onboard/csv/", bulk_views.onboard_csv),
    path("sovereignty/", centre_views.centre_page),
    path("sovereignty/action/", centre_views.centre_action),
    path("sovereignty/export/", centre_views.centre_export),
    path("approvals/", extra_views.approvals_page),
    path("approvals/action/", extra_views.approval_action),
    path("approvals/require/", extra_views.require_approval_toggle),
    path("community/", extra_views.community_page),
    path("share/toggle/", extra_views.share_toggle),
    path("bookmark/toggle/", extra_views.bookmark_toggle),
    path("parent/", extra_views.parent_page),
    path("accounts/2fa/", extra_views.twofa_page),
    path("accounts/verify/send/", extra_views.verify_send),
    path("accounts/verify/<str:token>/", extra_views.verify_confirm),
    path("analytics/", analytics_views.analytics_page),
    path("api/docs/", api_docs_views.api_docs_page),
    path("offline/", lambda request: __import__("django.shortcuts").shortcuts.render(request, "offline.html"), name="offline"),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)












