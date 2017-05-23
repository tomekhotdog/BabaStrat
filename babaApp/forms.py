from django import forms
from .models import Framework


class AssumptionForm(forms.Form):
    assumption = forms.CharField(required=True)


class ContraryForm(forms.Form):
    contrary = forms.CharField(required=True)


class RandomVariableForm(forms.Form):
    random_variable = forms.CharField(required=True)


trading_choices = [('yes', 'YES'), ('no', 'NO')]
trading_options = [(0, 'BUY'), (1, 'SELL'), (2, 'BUY and SELL')]


class SettingsForm(forms.Form):
    enable_trading = forms.MultipleChoiceField(
        widget=forms.RadioSelect,
        choices=trading_choices,
    )
    trading_options = forms.MultipleChoiceField(
        widget=forms.RadioSelect,
        choices=trading_options,
    )
    required_trade_confidence = forms.FloatField(
        label='Required trade confidence (%)',
        min_value=0.0,
        max_value=100.0
    )
    close_position_yield = forms.FloatField(
        label='Close position yield (%)',
        min_value=0.0,
        max_value=100.0
    )
    close_position_loss_limit = forms.FloatField(
        label='Close position loss limit (%)',
        min_value=0.0,
        max_value=100.0
    )


class FrameworkSelectionForm(forms.Form):
    framework_selection = forms.ModelChoiceField(
        queryset=Framework.objects,
        empty_label=' ',
        widget=forms.Select(attrs={'onchange': 'this.form.submit();'}))
