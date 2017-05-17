from django.shortcuts import render, get_list_or_404
from .models import Framework


def index(request):
    context = {}
    return render(request, 'babaApp/index.html', context)


def frameworks(request):
    framework_list = get_list_or_404(Framework)
    context = {'frameworks': framework_list,
               'tomek': "TOMEK IS A GENIUS", }
    return render(request, 'babaApp/frameworks.html', context)


# def index(request):
#     latest_question_list = Question.objects.order_by('-pub_date')[:5]
#     context = {'latest_question_list': latest_question_list}
#     return render(request, 'polls/index.html', context)