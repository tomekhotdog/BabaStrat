from frameworkExtensions import macroElements
from babaApp.models import DataSet, ExchangeEvent

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
            except macroElements.MacroRuleCalculationError:
                continue

    except DataSet.DoesNotExist:
        pass

    except AttributeError:
        pass

    return rules


def extract_external_random_variables(framework):
    additional_framework_elements = ''
    for line in framework.splitlines():
        try:
            if 'myRule(' in line:
                elements = line.split('myRule(')
                rule_body_elements = elements[1]
                rule_body_elements = rule_body_elements.split(')')[0]
                rule_body_elements = rule_body_elements.split(',')[1]
                rule_body_elements = rule_body_elements.split('[')[1]
                rule_body_elements = rule_body_elements.split(']')[0]
                rule_body_elements = rule_body_elements.split(',')

                for element in rule_body_elements:
                    events = ExchangeEvent.objects.filter(event_name=element.strip())
                    if len(events) > 0:
                        event = events[0]
                        additional_framework_elements += '\nmyRV(' + event.event_name + ',' + str(event.probability / 100) + ').'

        except IndexError:
            pass

    return additional_framework_elements