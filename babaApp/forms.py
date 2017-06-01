from django import forms
from .models import Market, Strategy


class AssumptionForm(forms.Form):
    assumption = forms.CharField(required=True)


class ContraryForm(forms.Form):
    contrary = forms.CharField(required=True)


class RandomVariableForm(forms.Form):
    random_variable = forms.CharField(required=True)


class RuleForm(forms.Form):
    rule = forms.CharField(required=True,
                           label='',
                           help_text='Add a rule. (BUY :- assumption, random variable, other element)')


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
    buy_quantity = forms.IntegerField(
        min_value=0,
    )
    sell_quantity = forms.IntegerField(
        min_value=0,
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


class StrategyPreferencesSelectionForm(forms.Form):
    strategy_selection = forms.ModelChoiceField(
        queryset=Strategy.objects,
        empty_label=' ',
        widget=forms.Select(attrs={'onchange': 'this.form.submit();'}))


class StrategySelectionForm(forms.Form):
    strategy_selection = forms.ModelChoiceField(
        queryset=Strategy.objects,
        empty_label='select strategy',
        widget=forms.Select(attrs={'onchange': 'this.form.submit();'})
    )


class NewStrategyForm(forms.Form):
    new_strategy = forms.CharField(required=True)