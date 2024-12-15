import logging
import datetime
import random
import math

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.db import transaction
from django.core.paginator import Paginator
from django.db.models import Q
from django.db.models.functions import Lower
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from .models import Movie, Genre, Comments, Profile, Viewing
from .forms import (
    CommentForm,
    UserSignUpForm,
    UserLoginForm,
    ChangeUserPasswordForm,
    DeleteAccountForm,
    ProfileUpdateForm
)


logger = logging.getLogger(__name__)

def homepage(request):
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    popular_movies = Movie.objects.order_by('-popularity').filter(is_active=True)[:6]  # Самые популярные 6 фильмов
    latest_movies = Movie.objects.order_by('-release_date').filter(is_active=True, release_date__range=("2004-01-01", today))
    paginator = Paginator(latest_movies, 20)
    page_number = request.GET.get("page")
    genres = Genre.objects.all()  
    last_movies = paginator.get_page(page_number)

    random_movie = None
    active_movies = Movie.objects.filter(is_active=True)
    if active_movies.exists():
        random_movie = random.choice(active_movies)
    
    context = {
        'popular_movies': popular_movies,
        'genres': genres,
        'last_movies': last_movies,
        'random_movie_slug': random_movie.slug if random_movie else None
    }
    return render(request, 'index.html', context=context)   
        
def header(request):
    genres = Genre.objects.all()
    context = {
        'genres': genres
    }
    return render(request, 'components/header.html', context=context)

def most_popular_movies_view(request):
    popular_movies = Movie.objects.order_by('-popularity').filter(is_active=True)
    paginator = Paginator(popular_movies, 20)
    page_number = request.GET.get("page")
    p_movies = paginator.get_page(page_number,)
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    movies = Movie.objects.order_by('-release_date').filter(is_active=True, release_date__range=("2004-01-01", today))
    context = dict(popular_movies=p_movies, page_title='Популярные фильмы.')
    return render(request, 'movie_app/most-popular-movies.html', context=context)


def category_view(request, category_slug):
    category = get_object_or_404(Genre,slug=category_slug, is_active=True)
    category_movies = Movie.objects.filter(genre=category)
    paginator = Paginator(category_movies,20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    genres = Genre.objects.all()  
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    movies = Movie.objects.order_by('-release_date').filter(is_active=True, release_date__range=("2004-01-01", today))
    context = dict(genres=genres,   category=category,category_movies=page_obj, page_title=category.title, movies=movies )
    return render(request, 'category.html', context=context)



def movie_detail_view(request, movie_slug):
    movie = get_object_or_404(Movie, slug=movie_slug, is_active=True)
    form = CommentForm(request.POST or None)

    movie_comments = Comments.objects.filter(movie=movie)
    paginator = Paginator(movie_comments, 10)
    page_number = request.GET.get('page')
    paginated_page = paginator.get_page(page_number)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.user = request.user 
        comment.movie = movie
        comment.save()
        messages.success(request, 'Ваш коментарий успешно оставлен.')
        return redirect(reverse('movie_app:movie_detail_view', args=(movie.slug,)))

    if movie.vote_average is not None:
        rounded_rating = round(movie.vote_average * 2) / 2
        stars = []
        for i in range(5):
            if i < math.floor(rounded_rating):
                stars.append('fa-star')
            elif i < rounded_rating:
                stars.append('fa-star-half-o')
            else:
                stars.append('fa-star-o')
    else:
        stars = ['fa-star-o'] * 5

    genres = Genre.objects.all()

    context = {
        'movie': movie,
        'genres': genres,
        'movie_stars': stars,
        'form': form,
        'movie_comments': paginated_page,
    }

    return render(request, 'details.html', context)


@login_required
def watching(request, slug):
    movie = get_object_or_404(Movie, slug=slug)
    genres = Genre.objects.all()
    
    Viewing.objects.get_or_create(
        user=request.user, 
        movie=movie,
        defaults={
            'status': 'completed', 
        }
    )
    
    context = {
        'movie': movie,
        'genres': genres,
    }
    return render(request, 'watch.html', context)

def search(request):    
    search_term = request.GET.get('query', '')
    
    if search_term:
        movie_items = Movie.objects.filter(
            Q(title__icontains=search_term) | 
            Q(overview__icontains=search_term)
        ).annotate(
            title_lower=Lower('title'),
            overview_lower=Lower('overview')
        ).filter(
            Q(title_lower__icontains=search_term) | 
            Q(overview_lower__icontains=search_term)
        ).distinct() 
    else:
        movie_items = Movie.objects.none()

    paginator = Paginator(movie_items, 20)
    page_number = request.GET.get('page')
    obj = paginator.get_page(page_number)
    genres = Genre.objects.all()

    context = {
        'search_movies': obj,
        'genres': genres,
        'search_term': search_term,
        'total_results': movie_items.count() 
    }
    return render(request, 'search.html', context=context)


def login_view(request):
    if request.user.is_authenticated:
        messages.info(request, f"Добро пожаловать {request.user.get_full_name()}! Вы уже авторизованы!")
        return redirect('/')
    form = UserLoginForm(request.POST or None)
    genres = Genre.objects.all()
    context = dict(form=form, genres=genres, page_title='Login')
    if form.is_valid():
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'{request.user.username} Вы успешно вошли!')
            return redirect('/')
        messages.warning(request, 'Неправильный пароль или имя пользователя. Проверьте и повторите попытку.')
        return render(request, 'login.html', context=context)
    return render(request, 'login.html', context=context)

def signup_View(request):
    if request.user.is_authenticated:
        messages.info(request, 'Вы уже авторизованы.')
        return redirect(reverse('movie_app:home'))

    form = UserSignUpForm(request.POST or None)
    genres = Genre.objects.all()
    context = {'form': form, 'genres': genres, 'page_title': 'Signup'}
    
    if request.method == 'POST':
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save(commit=False)
                    user.set_password(form.cleaned_data.get('password'))
                    user.is_active = True 
                    user.save()

                    profile, created = Profile.objects.get_or_create(
                        user=user,
                        defaults={
                            'avatar': '/default-avatar.webp',
                            'is_active': True
                        }
                    )

                    login(request, user)
                    
                    messages.success(request, 'Ваш аккаунт успешно создан!')
                    return redirect(reverse('movie_app:profile', kwargs={'profile_slug': profile.slug}))
            
            except Exception as e:
                logger.error(f"Ошибка при регистрации: {e}", exc_info=True)
                messages.error(request, 'Произошла ошибка при создании аккаунта. Пожалуйста, попробуйте снова.')
                transaction.set_rollback(True)
        
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
            
            logger.warning(f"Ошибки формы регистрации: {form.errors}")

    return render(request, 'signup.html', context)

def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request,'Вы вышли!')
        return redirect('/')
    else:
        if request.META.get('HTTP_REFERER'):
            return redirect(request.META['HTTP_REFERER'])
        else:
            return redirect('/')


def profile_detail_view(request, profile_slug):
    profile = get_object_or_404(Profile, slug=profile_slug, is_active=True)
    
    comments_list = Comments.objects.filter(user=profile.user).order_by('-created_at')
    
    paginator = Paginator(comments_list, 5)
    page_number = request.GET.get('page', 1)
    user_comments = paginator.get_page(page_number)
    
    viewed_movies = Viewing.objects.filter(
        user=profile.user, 
        status='completed'
    ).select_related('movie').order_by('-watched_date')
    
    context = {
        'profile': profile,
        'user_comments': user_comments,
        'viewed_movies': viewed_movies,
    }
    return render(request, 'profile.html', context)

def custom_404_view(request, exception):
    return render(request, '404.html', status=404)

def popular_movies(request):
    
    popular_movies = Movie.objects.filter(is_active=True).order_by('-popularity')
    
    paginator = Paginator(popular_movies, 20)
    page_number = request.GET.get("page")
    pop_movies = paginator.get_page(page_number)

    genres = Genre.objects.all()
    
    context = {
        'popular_movies': popular_movies,
        'genres': genres,
        'pop': pop_movies,
    }
    
    return render(request, 'all_popular.html', context=context)

def create_movie_view(request):
    genres = Genre.objects.filter(is_active=True)
    
    if request.method == "POST":
        movie_id = request.POST['movie_id']
        title = request.POST['title']
        overview = request.POST['overview']
        genre_ids = request.POST.getlist('genre')
        popularity = request.POST['popularity']
        vote_average = request.POST['vote_average']
        poster = request.POST.get('poster', '')
        video = request.POST.get('video', '')
        release_date = request.POST['release_date']
        language = request.POST['language']

        movie = Movie.objects.create(
            movie_id=movie_id,
            title=title,
            overview=overview,
            popularity=popularity,
            vote_average=vote_average,
            poster=poster,
            video=video,
            release_date=release_date,
            language=language,
        )
        movie.genre.set(genre_ids)
        movie.save()
        
        messages.success(request, "Фильм успешно добавлен!")
        return redirect('movie_app:home')

    return render(request, 'create_movie.html', {'genres': genres})

def category_list_view(request):
    categories = Genre.objects.all()
    return render(request, 'categories.html', {'categories': categories})