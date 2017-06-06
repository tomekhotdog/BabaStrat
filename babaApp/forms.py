from django import forms
from django.contrib.admin import widgets
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


class MacroRuleForm(forms.Form):
    macro_rule = forms.CharField(required=True,
                           label='',
                           help_text='Add a macro rule. (Uptrend :- 50DayEMA > 100DayEMA and Close > 100DayEMA)')


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


class TimeIntervalSelectionForm(forms.Form):
    start_date = forms.DateField()
    end_date = forms.DateField()
    compare_strategy = forms.ModelChoiceField(
        queryset=Strategy.objects,
        empty_label=' ',
        label='Compare strategy',
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super(TimeIntervalSelectionForm, self).__init__(*args, **kwargs)
        # self.fields['start_date'].widget = widgets.AdminDateWidget()
        self.fields['end_date'].widget = widgets.AdminDateWidget()


class BackTestTimeIntervalSelectionForm(forms.Form):
    test_start_date = forms.DateTimeField(label='Start date')
    test_end_date = forms.DateTimeField(label='End date')
    test_compare_strategy = forms.ModelChoiceField(
        queryset=Strategy.objects,
        empty_label=' ',
        label='Compare strategy',
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super(BackTestTimeIntervalSelectionForm, self).__init__(*args, **kwargs)
        self.fields['test_start_date'].widget = widgets.AdminDateWidget()
        self.fields['test_end_date'].widget = widgets.AdminDateWidget()
