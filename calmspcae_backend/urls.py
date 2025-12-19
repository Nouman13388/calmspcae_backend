from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

from my_app.views import IndexView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', IndexView.as_view(), name='index'),
    path('dashboard/', TemplateView.as_view(template_name='dashboard.html'), name='dashboard'),
    path('subscriptions/', TemplateView.as_view(template_name='subscriptions.html'), name='subscriptions-ui'),
    path('api/', include('my_app.urls')),
    path('api/subscriptions/', include('my_app.subscription_urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
