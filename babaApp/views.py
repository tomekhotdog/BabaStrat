from django.shortcuts import render, get_list_or_404
from babaSemantics import SemanticsUtils as Utils
from babaSemantics import BABAProgramParser as Parser
from .models import Framework


def index(request):
    context = {}
    return render(request, 'babaApp/index.html', context)


def frameworks(request):
    framework_list = get_list_or_404(Framework)

    framework = framework_list[0]
    framework_string = framework.string_representation
    baba = Parser.BABAProgramParser(string=framework_string).parse()
    language, assumptions, contraries, rvs, rules = Utils.string_representation(baba)

    context = {'frameworks': framework_list,
               'language': language, 'assumptions': assumptions, 'contraries': contraries,
               'random_variables': rvs, 'rules': rules}

    return render(request, 'babaApp/frameworks.html', context)


# def index(request):
#     latest_question_list = Question.objects.order_by('-pub_date')[:5]
#     context = {'latest_question_list': latest_question_list}
#     return render(request, 'polls/index.html', context)