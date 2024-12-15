from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

from django.contrib import sitemaps
from django.contrib.sitemaps.views import sitemap
from core.sitemaps import GenreSitemap, MovieSitemap

sitemaps = {
    'categories': GenreSitemap,
    'movies': MovieSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include('movie_app.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


handler404 = 'movie_app.views.custom_404_view'