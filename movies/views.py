from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Review, Rating
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Avg, Count

def index(request):
    search_term = request.GET.get('search')
    if search_term:
        movies = Movie.objects.filter(name__icontains=search_term)
    else:
        movies = Movie.objects.all()
    template_data = {}
    template_data['title'] = 'Movies'
    template_data['movies'] = movies
    return render(request, 'movies/index.html',
                  {'template_data': template_data})
def show(request, id):
    movie = Movie.objects.get(id=id)
    reviews = Review.objects.filter(movie=movie, reported=False)

    template_data = {}
    template_data['title'] = movie.name
    template_data['movie'] = movie
    template_data['reviews'] = reviews
    template_data['average_rating'] = Rating.objects.filter(movie=movie).aggregate(Avg('score'))['score__avg']
    template_data['user_rating'] = None
    if request.user.is_authenticated:
        template_data['user_rating'] = Rating.objects.filter(movie=movie, user=request.user).first()
    return render(request, 'movies/show.html',
                  {'template_data': template_data})
@login_required
def rate(request, id):
    if request.method == 'POST':
        score = request.POST.get('score')
        if score in ['1', '2', '3', '4', '5']:
            movie = get_object_or_404(Movie, id=id)
            Rating.objects.update_or_create(
                movie = movie,
                user = request.user,
                defaults = {'score': int(score)},
            )
    return redirect('movies.show', id=id)

@login_required
def create_review(request, id):
    if request.method == 'POST' and request.POST['comment']!= '':
        movie = Movie.objects.get(id=id)
        review = Review()
        review.comment = request.POST['comment']
        review.movie = movie
        review.user = request.user
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)

@login_required
def edit_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user != review.user:
        return redirect('movies.show', id=id)
    if request.method == 'GET':
        template_data = {}
        template_data['title'] = 'Edit Review'
        template_data['review'] = review
        return render(request, 'movies/edit_review.html',
            {'template_data': template_data})
    elif request.method == 'POST' and request.POST['comment'] != '':
        review = Review.objects.get(id=review_id)
        review.comment = request.POST['comment']
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)

@login_required
def delete_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id,
        user=request.user)
    review.delete()
    return redirect('movies.show', id=id)

@login_required
def report_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)
    review.reported = True
    review.save()
    return redirect('movies.show', id=id)

@user_passes_test(lambda u: u.is_staff)
def top_commenter(request):
    top = (
        Review.objects
        .values('user__username')
        .annotate(comment_count=Count('id'))
        .order_by('-comment_count')
        .first()
    )
    template_data = {}
    template_data['title'] = 'Top Commenter'
    if top:
        template_data['username'] = top['user__username']
        template_data['comment_count'] = top['comment_count']
    else:
        template_data['username'] = None
        template_data['comment_count'] = 0
    return render(request, 'movies/top_commenter.html',
                  {'template_data': template_data})