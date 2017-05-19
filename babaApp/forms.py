from django import forms


class AssumptionForm(forms.Form):
    assumption = forms.CharField(required=True)


class ContraryForm(forms.Form):
    contrary = forms.CharField(required=True)


class RandomVariableForm(forms.Form):
    random_variable = forms.CharField(required=True)