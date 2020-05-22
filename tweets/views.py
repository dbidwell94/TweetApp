from random import randint
from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404, JsonResponse
from django.conf import settings
from django.utils.http import is_safe_url
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from .models import Tweet
from .forms import TweetForm
from .serializers import (TweetSerializer,
                          TweetActionSerializer,
                          TweetCreateSerializer)

ALLOWED_HOSTS = settings.ALLOWED_HOSTS

def home_page(request, *args, **kwargs):
    context = {}
    return render(request, "pages/home.html", context)

@api_view(['GET']) # HTTP client must use GET
def tweet_list_view(request, *args, **kwargs):
    qs = Tweet.objects.all()
    serializer = TweetSerializer(qs, many=True)
    return Response(serializer.data)
    
@api_view(['POST']) # HTTP client has to use POST
@permission_classes([IsAuthenticated])
def tweet_create_view(request, *args, **kwags):
    """ REST API tweet creation """
    data = request.POST
    serializer = TweetCreateSerializer(data=data)
    if serializer.is_valid(raise_exception=True):
        serializer.save(user=request.user)
        return Response(serializer.data, status=201)
    return Response({}, status=400)

@api_view(['GET']) # HTTP client must use GET
def tweet_detail_view(request, tweet_id, *args, **kwargs):
    qs = Tweet.objects.filter(id=tweet_id)
    if not qs.exists():
        return Response({}, status=404)
    obj = qs.first()
    serializer = TweetSerializer(obj)
    return Response(serializer.data, status=200)

@api_view(['DELETE', 'POST']) # HTTP client must use either DELETE or POST
@permission_classes([IsAuthenticated])
def tweet_delete_view(request, tweet_id, *args, **kwargs):
    qs = Tweet.objects.filter(id=tweet_id)
    if not qs.exists():
        return Response({}, status=404)
    qs = qs.filter(user=request.user)
    if not qs.exists():
        return Response({"message": "You cannot delete this tweet..."}, status=401)
    obj = qs.first()
    obj.delete()
    return Response({"message": "Tweet removed..."}, status=200)

@api_view(['POST']) # HTTP client must use either DELETE or POST
@permission_classes([IsAuthenticated])
def tweet_action_view(request, *args, **kwargs):
    """
    Tweet_id is required
    Action options: Like, Unlike, Re-Tweet
    """
    serializer = TweetActionSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        data = serializer.validated_data
        tweet_id = data.get("id")
        action = data.get("action")
        content = data.get("content")
        qs = Tweet.objects.filter(id=tweet_id)
        if not qs.exists():
            return Response({}, status=404)
        obj = qs.first()
        if action == "like":
            obj.likes.add(request.user)
            serializer = TweetSerializer(obj)
            return JsonResponse(serializer.data, status=200)
        elif action == "unlike":
            obj.likes.remove(request.user)
            serializer = TweetSerializer(obj)
            return JsonResponse(serializer.data, status=200)
        elif action == "retweet":
            new_tweet = Tweet.objects.create(
                user=request.user,
                parent=obj,
                content=content)
            serializer = TweetSerializer(new_tweet)
            return JsonResponse(serializer.data, status=201)
            
    return Response({}, status=200)

def tweet_detail_view_pure_django(request, tweet_id, *args, **kwargs):
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

def tweet_create_view_pure_django(request, *args, **kwags):
    user = request.user
    if not request.user.is_authenticated:
        user = None
        if request.is_ajax():
            return JsonResponse({}, status=401)
        else:
            return redirect(settings.LOGIN_URL)
    tweet_form = TweetForm(request.POST or None)
    next_url = request.POST.get('next') or None
    if tweet_form.is_valid():
        obj = tweet_form.save(commit=False)
        obj.user = user
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

def tweet_list_view_pure_django(request, *args, **kwargs):
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