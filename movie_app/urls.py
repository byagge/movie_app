from django.contrib import admin
from django.urls import path

from . import views

app_name = "movie_app"

urlpatterns = [
    path("", views.homepage, name="home"),
    path("movie/<slug:movie_slug>/", views.movie_detail_view, name="movie_detail_view"),
    path("categories/", views.category_list_view, name="categories"),
    path("category/<slug:category_slug>/", views.category_view, name="category_detail_view"),
    path('watching/<slug:slug>', views.watching, name='watching'),
    path('populars/', views.popular_movies, name='populars'),
    path("most-popular-movies/", views.most_popular_movies_view, name="most_popular_movies"),
    path('account/<slug:profile_slug>/', views.profile_detail_view, name='profile'),
    path('login/', views.login_view, name="login"),
    path("signup/", views.signup_View, name='signup'),
    path('logout/', views.logout_view, name="logout"),
    path('create/', views.create_movie_view, name='create_movie'),
    path('s', views.search, name="search"),
]
