import json

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from .handle_emails import get_unseen_emails


def get_emails(request):
    output = get_unseen_emails()
    return JsonResponse(output, safe=False)


def list_categories(request):
    categories = Category.objects.all()
    cats = [[c.path, c.name] for c in categories]
    return JsonRespone(cats)


def show_categories(request):
    categories = Category.objects.all()
    cats = [[c.path, c.name]  for c in categories]
    return render("protocol/categories.html", cats)

