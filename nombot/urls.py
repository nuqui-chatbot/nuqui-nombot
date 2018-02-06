"""nombot URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import url

from nombot.views import HelloWorldView, EventView, MealView, UpdatesView, RecipeView, IngredientsView

urlpatterns = [
    url(r'meal', MealView.as_view()),
    url(r'event', EventView.as_view()),
    url(r'updates', UpdatesView.as_view()),
    url(r'hello', HelloWorldView.as_view()),
    url(r'recipe', RecipeView.as_view()),
    url(r'ingredients', IngredientsView.as_view())
]
