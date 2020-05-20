from random import randint
from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404, JsonResponse
from django.conf import settings
from django.utils.http import is_safe_url
from .models import Tweet
from .forms import TweetForm

ALLOWED_HOSTS = settings.ALLOWED_HOSTS

def home_page(request, *args, **kwargs):
    context = {}
    return render(request, "pages/home.html", context)


def tweet_list_view(request, *args, **kwargs):
    """
    REST Api view: returns JSON data of all tweets
    to be consumed by JavaScript
    """
    query_set = Tweet.objects.all()
    tweets_list = [tweet.serialize() for tweet in query_set]
    data = {
        "isUser": False,
        "response": tweets_list
    }
    return JsonResponse(data)


def tweet_detail_view(request, tweet_id, *args, **kwargs):
    """
    REST Api view: return JSON data
    Consume by JavaScript
    """
    data = {
        "id": tweet_id,
    }
    status = 200
    try:
        tweet = Tweet.objects.get(id=tweet_id)
        data['content'] = tweet.content
    except:
        data['message'] = "Not Found"
        status = 404

    return JsonResponse(data, status=status)


def tweet_create_view(request, *args, **kwags):
    tweet_form = TweetForm(request.POST or None)
    next_url = request.POST.get('next') or None
    if tweet_form.is_valid():
        obj = tweet_form.save(commit=False)
        obj.save()
        if request.is_ajax():
            return JsonResponse(obj.serialize(), status=201)
        if next_url is not None and is_safe_url(next_url, ALLOWED_HOSTS):
            return redirect(next_url)
        tweet_form = TweetForm()
    if tweet_form.errors:
        if request.is_ajax():
            return JsonResponse(tweet_form.errors, status=400)
    context = {'form': tweet_form}
    return render(request, 'components/form.html', context)
