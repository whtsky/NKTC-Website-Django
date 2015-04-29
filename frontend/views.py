from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Q
from django.views.decorators.csrf import csrf_protect

from frontend.models import MainMenu, Slider, SecondaryMenu, News, Article, Activity
# Create your views here.


def index(request):
    mains = MainMenu.objects.order_by("order")
    q = Q(id=-1)
    nktc = MainMenu.objects.filter(codename="nktc")
    nktc = SecondaryMenu.objects.filter(parent=nktc)
    for item in nktc:
        q = q | Q(category=item)
    slider = Slider.objects.order_by("push__pub_date")[:5]
    news = ()
    for obj in News.category_choice:
        news = news + (News.objects.filter(category=obj).order_by("push__pub_date")[:7],)
    articles = Article.objects.order_by("pub_date")[:10]
    activities = Activity.objects.filter(q).filter(end_date__gte=timezone.now())[:4]
    context = {
        "mains": mains,
        "slider": slider,
        "news": news,
        "articles": articles,
        "activities": activities
    }
    return render(request, "frontend/index.html", context)


def main_menu(request, main):
    main = MainMenu.objects.get(codename=main)
    mains = MainMenu.objects.order_by("order")
    secondaries = SecondaryMenu.objects.filter(parent=main).order_by("order")
    q = Q(id=-1)
    for item in secondaries:
        q = q | Q(parent=item)
    article = Article.objects.filter(q)
    articles = ()
    for item in Article.category_choices:
        articles = articles + (article.filter(category=item[0])[:10],)
    context = {
        "main": main,
        "mains": mains,
        "secondaries": secondaries,
        "articles": articles
    }
    return render(request, "frontend/list-main.html", context)


def secondary_menu(request, main, secondary):
    main = MainMenu.objects.get(codename=main)
    secondary = SecondaryMenu.objects.get(codename=secondary)
    mains = MainMenu.objects.order_by("order")
    secondaries = SecondaryMenu.objects.filter(parent=main).order_by("order")
    articles = ()
    for item in Article.category_choices:
        articles = articles + (Article.objects.filter(category=item[0])[:10],)
    slider = Slider.objects.filter(category=secondary)
    activities = Activity.objects.filter(category=secondary)
    hot = Article.objects.filter(parent=secondary).order_by("hits")
    context = {
        "main": main,
        "secondary": secondary,
        "mains": mains,
        "secondaries": secondaries,
        "articles": articles,
        "slider": slider,
        "activities": activities,
        "hot": hot
    }
    return render(request, "frontend/list-secondary.html", context)


def main_menu_all(request, main):
    main = MainMenu.objects.get(codename=main)
    mains = MainMenu.objects.order_by("order")
    secondaries = SecondaryMenu.objects.filter(parent=main).order_by("order")
    q = Q(id=-1)
    for item in secondaries:
        q = q | Q(parent=item)
    article = Article.objects.filter(q)
    articles = ()
    for item in Article.category_choices:
        articles = articles + (article.filter(category=item[0]),)
    context = {
        "main": main,
        "mains": mains,
        "secondaries": secondaries,
        "articles": articles
    }
    return render(request, "frontend/list-main-all.html", context)


def secondary_menu_all(request, main, secondary):
    main = MainMenu.objects.get(codename=main)
    secondary = SecondaryMenu.objects.get(codename=secondary)
    mains = MainMenu.objects.order_by("order")
    secondaries = SecondaryMenu.objects.filter(parent=main).order_by("order")
    articles = ()
    for item in Article.category_choices:
        articles = articles + (Article.objects.filter(parent=secondary).filter(category=item[0]),)
    context = {
        "main": main,
        "secondary": secondary,
        "mains": mains,
        "secondaries": secondaries,
        "articles": articles,
    }
    return render(request, "frontend/list-secondary-all.html", context)


@csrf_protect
def search(request):
    if request.method == "POST":
        keyword = request.POST["content"]
        if keyword is None:
            return redirect("index")
        q = Q(title__contains=keyword) | Q(text__contains=keyword) | Q(author__nickname=keyword)
        articles = Article.objects.filter(q)
        q = Q(title__contains=keyword) | Q(text__contains=keyword)
        activities = Activity.objects.filter(q)
        context = {
            "articles": articles,
            "activities": activities
        }
        return render(request, "frontend/search-result.html", context)

    if request.method == "GET":
        return redirect("index")


def content(request, main, secondary, id):
    main = MainMenu.objects.get(codename=main)
    secondary = SecondaryMenu.objects.get(codename=secondary)
    article = Article.objects.get(pk=id)
    article.hit()
    mains = MainMenu.objects.order_by("order")
    secondaries = SecondaryMenu.objects.filter(parent=main).order_by("order")
    q = Q(id=-1)
    for item in secondaries:
        q = q | Q(parent=item)
    hot = Article.objects.filter(q).order_by("hits")[:10]
    context = {
        "main": main,
        "secondary": secondary,
        "mains": mains,
        "secondaries": secondaries,
        "article": article,
        "hot": hot
    }
    return render(request, "frontend/content-page.html", context)