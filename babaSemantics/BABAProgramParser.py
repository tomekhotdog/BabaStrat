import re

import babaSemantics.Semantics as Semantics
import babaSemantics.Bayesian as Bayesian

FILENAME = 'filename'
STRING = 'string'
NEGATION_CHAR = '~'

######################################################
# BABA framework definition syntax

# Elements:
# assumptions: myAsm(<assumption>) -> myAsm(a)
# contraries: contrary(<assumption>, <assumption contrary>) -> contrary(a, _a)
# random variables: myRV(<random variable>, <probability>) -> myRV(a, 0.5)
# conditional random variables: myRV(<random variable>, <set of conditional variables>, <conditional probabilities>):
#   -> myRV(a, [b,c], [(a,b): 0.3, (~a,b): 0.4, (a,~b): 0.5, (~a,~b): 0.6]) -> conditional random variables

######################################################


# Class for parsing an BABA program from string or file
# The String or File is provided in the constructor (precedence for String)
# Example usage:
#    1) BABAProgramParser(string='~program input as string~')
#    2) BABAProgramParser(filename='file_location')
class BABAProgramParser:
    def __init__(self, *args, **kwargs):
        self.reset_program_elements()

        if STRING in kwargs:
            self.STRING = kwargs[STRING]
            self.FILENAME = None
        elif FILENAME in kwargs:
            self.FILENAME = kwargs[FILENAME]
            self.STRING = None

    def reset_program_elements(self):
        self.language = []
        self.assumptions = []
        self.rules = []
        self.contraries = {}
        self.random_variables = []
        self.bayesian_network = {}

    def parse(self):
        if self.STRING:
            return self.parse_program(self.STRING.split('\n'))
        elif self.FILENAME:
            file = open(self.FILENAME, 'r')
            baba = self.parse_program(file)
            file.close()
            return baba

    def parse_program(self, program):
        self.reset_program_elements()

        rules = []  # Parse rules at the end

        for line in program:

            if matches_rule_declaration(line):
                rules.append(line)

            elif matches_assumption_declaration(line):
                assumption = extract_assumption(line)
                self.assumptions.append(assumption)
                self.language.append(assumption)

            elif matches_contrary_declaration(line):
                contrary = extract_contrary(line)
                self.contraries[contrary.assumption] = contrary
                self.language.append(contrary.contrary)

            elif matches_random_variable_declaration(line):
                rv, probability = extract_random_variable(line)
                self.random_variables.append(rv)
                self.language.append(rv)
                self.bayesian_network[rv.symbol] = probability

            elif matches_conditional_random_variable_declaration(line):
                rv, probability = extract_conditional_random_variable(line)
                self.random_variables.append(rv)
                self.language.append(rv)
                self.bayesian_network[rv.symbol] = probability

        for rule in rules:
            extracted_rule = extract_rule(rule, self.random_variables)
            rule_elements = extracted_rule.body + [extracted_rule.head]
            for sentence in rule_elements:
                if sentence not in self.language:
                    self.language.append(sentence)

            self.rules.append(extracted_rule)

        return Semantics.BABA(self.language,
                              self.rules,
                              self.assumptions,
                              self.contraries,
                              self.random_variables,
                              Bayesian.BayesianNetwork(self.bayesian_network))


class ProgramParseException(Exception):
    def __init__(self, message):
        self.message = message


#########################################################################################
# The following boolean method return matches to the corresponding program element syntax
#########################################################################################

decimal_number_regex = '\d*\.?\d*'
assumption_regex = '\s*myAsm\([\w]+\)\.\s*$'
rule_regex = '\s*myRule\(\s*[\w]+\s*,\s*\[([\w+_\.]|,|\s*|~)+\]\)\.\s*$'
contrary_regex = '\s*contrary\(\s*[\w]+\s*,\s*[\w]+\s*\)\.\s*$'
random_variable_regex = '\s*myRV\(\s*~?\s*[\w]+\s*,\s*' + decimal_number_regex + '\s*\)\.\s*'
conditional_rv_regex = '\s*myRV\(\s*[\w]+\s*,\s*\[.*\]\s*,\s*\[.*\]\s*\)\.\s*$'


# myAsm(sentence).
def matches_assumption_declaration(assumption):
    return True if(re.match(assumption_regex, assumption)) else False


# myRule(sentence, [sentences]).
def matches_rule_declaration(rule):
    return True if re.match(rule_regex, rule) else False


# contrary(sentence, contrary).
def matches_contrary_declaration(contrary):
    return True if re.match(contrary_regex, contrary) else False


# myRV(sentence).
def matches_random_variable_declaration(text):
    return True if re.match(random_variable_regex, text) else False


# myRV(sentence, [conditional rvs], [conditional probabilities])
def matches_conditional_random_variable_declaration(text):
    return True if re.match(conditional_rv_regex, text) else False


############################################################################
# The following methods extract and return the corresponding program element
############################################################################

def extract_assumption(assumption):
    if not matches_assumption_declaration(assumption):
        raise ProgramParseException("Provided assumption does not match required format")
    return Semantics.Sentence(extract_from_parentheses(assumption))


def extract_rule(rule, random_variables):
    if not matches_rule_declaration(rule):
        raise ProgramParseException("Provided rule does not match required format")

    extracted = extract_from_parentheses(rule).split(',', 1)
    head = Semantics.Sentence(extracted[0].strip())
    body = []
    for elem in extract_from_square_brackets(extracted[1].strip()).split(','):
        if len(elem) == 0:
            continue

        rv = Semantics.Sentence(elem.strip(), random_variable=True)
        is_negation = elem.strip().startswith(NEGATION_CHAR)
        if is_negation:
            rv = Semantics.Sentence(elem.strip()[1:], random_variable=True)
        if rv in random_variables:
            body.append(Semantics.Sentence(rv.symbol, random_variable=True, negation=is_negation))
        else:
            body.append(Semantics.Sentence(elem.strip()))

    return Semantics.Rule(head, body)


def extract_contrary(contrary):
    if not matches_contrary_declaration(contrary):
        raise ProgramParseException("Provided contrary does not match required format")

    extracted = extract_from_parentheses(contrary).split(',')
    assumption = Semantics.Sentence(extracted[0].strip())
    contrary = Semantics.Sentence(extracted[1].strip())
    return Semantics.Contrary(assumption, contrary)


def extract_random_variable(random_variable):
    if not matches_random_variable_declaration(random_variable):
        raise ProgramParseException("Provided random variable does not match required format")

    extracted = extract_from_parentheses(random_variable).split(',')
    is_negation = extracted[0].strip().startswith(NEGATION_CHAR)
    probability = float(extracted[1].strip())
    if is_negation:
        rv = Semantics.Sentence(extracted[0].strip()[1:], random_variable=True, negation=True)
        return rv, (1 - probability)

    else:
        rv = Semantics.Sentence(extracted[0].strip(), random_variable=True)
        return rv, probability


def extract_conditional_random_variable(text):
    if not matches_conditional_random_variable_declaration(text):
        raise ProgramParseException("Provided conditional random variable does not match required format")

    rv_definition = extract_from_parentheses(text)
    arguments = rv_definition.split('[')
    sentence = Semantics.Sentence(arguments.pop(0).split(',')[0].strip(), random_variable=True)
    conditional_variables = extract_conditional_variables('[' + arguments.pop(0))
    conditional_probabilities = extract_conditional_probabilities('[' + ''.join(arguments))
    conditional_probability = Bayesian.ConditionalProbability(sentence, conditional_variables, conditional_probabilities)
    return sentence, conditional_probability


def extract_conditional_variables(text):
    variables = extract_from_square_brackets(text)
    return [Semantics.Sentence(v.strip(), random_variable=True) for v in variables.split(',')]


def extract_conditional_probabilities(text):
    probability_map_string = extract_from_square_brackets(text)
    probability_map = {}
    for probability_pair in probability_map_string.split(','):
        key_value = probability_pair.split(':')
        key = key_value[0].strip()
        value = float(key_value[1].strip())
        probability_map[key] = value

    return probability_map


# Utility method that extracts the string from input of format: [\w]*\(<element>\)[\w]*
def extract_from_parentheses(input_string):
    return (input_string.split('(')[1]).split(')')[0].strip()


# Utility method that extracts the string from input of format: [\w]*[(<element>\][\w]*
def extract_from_square_brackets(input_string):
    return (input_string.split('[')[1]).split(']')[0].strip()
