from frameworkExtensions import macroElements
from babaApp.models import DataSet

NEW_LINE = '\n'


# Parses MacroRules (in strategy framework_extension) and returns appropriate BABA rules
# i.e. calculates truth value of MacroRule body and returns BABA rule for MacroRule head with empty body
#
# example: given MacroRule: Uptrend :- Close > 10DaySMA
# parses to MacroRule: MacroRuleHead: Close, MacroRuleBody: Close > 10DaySMA
# calculates truth value for given date: Close > 10DaySMA == True
# returns BABA rules with empty body when MacroRuleBody true: myRule(Uptrend, []).
def compute_framework_rules(strategy, datetime):
    rules = ''
    try:
        data_set = DataSet.objects.get(dataset_name=strategy.market.market_name)

        framework_extension = strategy.framework_extension
        macro_rules = framework_extension.splitlines()
        for rule_string in macro_rules:
            try:
                macro_rule = macroElements.MacroRule(rule_string)
                result = macro_rule.calculate(data_set, datetime)

                if result:
                    rules += '\n' + 'myRule(' + macro_rule.macroRuleHead.identifier + ', []).'

            except macroElements.MacroElementParseException:
                continue

    except DataSet.DoesNotExist:
        pass

    return rules
