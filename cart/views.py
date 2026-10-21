from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from movies.models import Movie
from .utils import calculate_cart_total
from .models import Order, Item
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum


def index(request):
    cart_total = 0
    movies_in_cart = []
    cart = request.session.get('cart', {})
    movie_ids = list(cart.keys())
    if (movie_ids != []):
        movies_in_cart = Movie.objects.filter(id__in=movie_ids)
        cart_total = calculate_cart_total(cart,
            movies_in_cart)
    template_data = {}
    template_data['title'] = 'Cart'
    template_data['movies_in_cart'] = movies_in_cart
    template_data['cart_total'] = cart_total
    return render(request, 'cart/index.html',
        {'template_data': template_data})
def add(request, id):
    get_object_or_404(Movie, id=id)
    cart = request.session.get('cart', {})
    cart[id] = request.POST['quantity']
    request.session['cart'] = cart
    return redirect('cart.index')
def clear(request):
    request.session['cart'] = {}
    return redirect('cart.index')
# Create your views here.

@login_required
def purchase(request):
    cart = request.session.get('cart', {})
    movie_ids = list(cart.keys())
    if (movie_ids == []):
        return redirect('cart.index')
    movies_in_cart = Movie.objects.filter(id__in=movie_ids)
    cart_total = calculate_cart_total(cart, movies_in_cart)
    order = Order()
    order.user = request.user
    order.total = cart_total
    order.save()
    for movie in movies_in_cart:
        item = Item()
        item.movie = movie
        item.price = movie.price
        item.order = order
        item.quantity = cart[str(movie.id)]
        item.save()
    request.session['cart'] = {}
    template_data = {}
    template_data['title'] = 'Purchase confirmation'
    template_data['order_id'] = order.id
    return render(request, 'cart/purchase.html',
        {'template_data': template_data})


@user_passes_test(lambda u: u.is_staff)
def top_buyer(request):
    topB = ( Item.objects.values('order__user__username')
            .annotate(movies_purchased = Sum('quantity'))
            .order_by('-movies_purchased','order__user__username')
            .first()
            )
    template_data = {}
    template_data['title'] = 'Top Buyer'
    if topB:
        template_data['username'] = topB['order__user__username']
        template_data['movies_purchased'] = topB['movies_purchased']
    else:
        template_data['username'] = None
        template_data['movies_purchased'] =0
    return render(request, 'cart/top_buyer.html',
            {'template_data': template_data})


@user_passes_test(lambda u: u.is_staff)
def top_buyers(request):
    topB = list(
        Item.objects.values('order__user__username')
        .annotate(movies_purchased=Sum('quantity'))
        .order_by('-movies_purchased', 'order__user__username')
        .all()
    )
    print(topB)
    if request.method == 'POST':
        size = request.POST.get('size')
        topB = topB[:int(size)] if size else topB

    template_data = {
        "title": 'Top Buyers',
        "users": topB
    }
    return render(
        request,
        'cart/top_buyers.html',
        {'template_data': template_data}
    )
