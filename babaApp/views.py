from django.shortcuts import render, get_list_or_404
from django.http import JsonResponse
from babaSemantics import BABAProgramParser as Parser
from babaSemantics import Semantics as Semantics
from babaApp.extras import specificStyling
from .models import Framework
from .forms import AssumptionForm, ContraryForm, RandomVariableForm


POST = 'POST'


def index(request):
    context = {}
    return render(request, 'babaApp/index.html', context)


def frameworks_default(request):
    framework_list = get_list_or_404(Framework)
    framework = framework_list[0]
    return frameworks(request, framework)


def frameworks(request, framework_name):

    if request.method == POST:
        process_form_submission(request)

    if not Framework.objects.filter(framework_name=framework_name).exists():
        return frameworks_default(request)

    ##################################################################
    framework_list = get_list_or_404(Framework)
    framework = Framework.objects.get(framework_name=framework_name)

    framework_string = framework.string_representation
    baba = Parser.BABAProgramParser(string=framework_string).parse()
    language, assumptions, contraries, rvs, rules = Semantics.string_representation(baba)

    semantic_probabilities = Semantics.compute_semantic_probability(Semantics.GROUNDED, baba)
    ##################################################################

    assumption_form = AssumptionForm
    contrary_form = ContraryForm
    random_variable_form = RandomVariableForm

    context = {'frameworks': framework_list, 'framework_name': framework_name,
               'language': language, 'assumptions': assumptions, 'contraries': contraries,
               'random_variables': rvs, 'rules': rules, 'semantic_probabilities': semantic_probabilities,
               'assumption_form': assumption_form,
               'contrary_form': contrary_form,

               'random_variable_form': random_variable_form}

    return render(request, 'babaApp/frameworks.html', context)


def learn(request):
    framework_list = get_list_or_404(Framework)
    context = {'frameworks': framework_list,
               'style': specificStyling.get_sidebar_styling('learn')}

    return render(request, 'babaApp/learn.html', context)


def settings(request):
    framework_list = get_list_or_404(Framework)
    context = {'frameworks': framework_list,
               "style": specificStyling.get_sidebar_styling('settings')}

    return render(request, 'babaApp/settings.html', context)


def reports(request):
    framework_list = get_list_or_404(Framework)
    context = {'frameworks': framework_list,
               "style": specificStyling.get_sidebar_styling('reports')}

    return render(request, 'babaApp/reports.html', context)


def process_form_submission(request):
    if 'assumption' in request.POST:
        form = AssumptionForm(request.POST)
        if form.is_valid():
            new_assumption = form.cleaned_data['assumption']

    elif 'contrary' in request.POST:
        form = ContraryForm(request.POST)
        if form.is_valid():
            t = 4

    elif 'random_variable' in request.POST:
        form = RandomVariableForm(request.POST)
        if form.is_valid():
            t = 5

    # do something


def chart_data(request):
    data = {'data': {'1': '100', '2': 200, '3': 300}, 'data_name': 'data'}

    return JsonResponse(data)
