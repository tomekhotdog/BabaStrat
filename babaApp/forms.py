from django import forms


class AssumptionForm(forms.Form):
    assumption = forms.CharField(required=True)


class ContraryForm(forms.Form):
    contrary = forms.CharField(required=True)


class RandomVariableForm(forms.Form):
    random_variable = forms.CharField(required=True)


trading_choices = [('yes', 'YES'), ('no', 'NO')]
trading_options = [('buy', 'BUY'), ('sell', 'SELL'), ('buy_and_sell', 'BUY and SELL')]


class SettingsForm(forms.Form):
    enable_trading = forms.MultipleChoiceField(
        widget=forms.RadioSelect,
        choices=trading_choices,
    )
    trading_options = forms.MultipleChoiceField(
        widget=forms.RadioSelect,
        choices=trading_options,
    )
    required_trade_confidence = forms.FloatField(label='Required trade confidence (%)')
    close_position_yield = forms.FloatField(label='Close position yield (%)')
    close_position_loss_limit = forms.FloatField(label='Close position loss limit (%)')
