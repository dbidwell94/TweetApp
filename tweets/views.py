from django.shortcuts import render
from django.http import HttpResponse, Http404, JsonResponse
from .models import Tweet


def home_page(request, *args, **kwargs):
    context = {}
    return render(request, "pages/home.html", context)


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
