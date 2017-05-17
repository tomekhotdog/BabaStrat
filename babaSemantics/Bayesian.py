import functools as tools

import babaSemantics.Semantics as Semantics


# A representation of the Bayesian Network governing
# the set of a random variables in a BABA network
class BayesianNetwork:

    def __init__(self, values):
        self.values = values  # dictionary: Semantic.Sentence.symbol : value
                              # or: Semantic.Sentence.symbol : ConditionalProbability
        self.validate()

    def validate(self):
        for _, item in self.values.items():  # Item can be ConditionalProbability object or absolute value
            if isinstance(item, ConditionalProbability):
                continue

            elif item < 0 or item > 1:
                raise InvalidRandomVariableException("Random Variable value must be within bound [0 <= value <= 1]")

    def p(self, sentence, conditional_variables=[]):
        if sentence.symbol not in self.values:
            raise InvalidRandomVariableException(str(sentence) + " is not random variable in this Bayesian network")

        rv_probability = self.values[sentence.symbol]

        if isinstance(rv_probability, ConditionalProbability):
            rv_probability = rv_probability.p(conditional_variables)

        return rv_probability if not sentence.negation else (1 - rv_probability)

    def p_world(self, random_variables):
        if not all([rv.symbol in self.values for rv in random_variables]):
            raise InvalidRandomVariableWorldException("This is not a valid world in this Bayesian network")

        return tools.reduce(lambda x, y: x*y,
                            [self.p(sentence, conditional_variables=random_variables) for sentence in random_variables])


# Encapsulates a random variable's conditional probability
class ConditionalProbability:

    def __init__(self, sentence, conditional_variables, conditional_probabilities):
        self.sentence = sentence
        self.conditional_variables = conditional_variables
        self.conditional_probabilities = conditional_probabilities  # dictionary: random variable key -> probability

    # Equality defined by structure (variables present, not probabilities)
    def __eq__(self, other):
        match_sentence = self.sentence == other.sentence
        match_variables = len(self.conditional_variables) == len(other.conditional_variables)
        all([elem in self.conditional_variables for elem in other.conditional_variables])
        match_probabilities = len(self.conditional_probabilities) == len(other.conditional_probabilities)

        return match_sentence and match_variables and match_probabilities

    #  TODO: define validate()

    def sum(self):
        return sum([prob for _, prob in self.conditional_probabilities.items()])

    def p(self, conditional_variables):
        if self.conditional_probability_key(conditional_variables) not in self.conditional_probabilities:
            raise InvalidConditionalProbabilityException(
                "Probability calculation requires all conditional random variables")

        return self.conditional_probabilities[self.conditional_probability_key(conditional_variables)]

    def conditional_probability_key(self, cond_variables):
        required_variables = [rv for rv in cond_variables
                              if Semantics.Sentence(rv.symbol, random_variable=True) in self.conditional_variables]
        sorted_variables = sorted(required_variables, key=lambda rv: rv.symbol)
        return ''.join([str(rv) for rv in sorted_variables])


class InvalidRandomVariableException(Exception):
    def __init__(self, message):
        self.message = message


class InvalidRandomVariableWorldException(Exception):
    def __init__(self, message):
        self.message = message


class InvalidConditionalProbabilityException(Exception):
    def __init__(self, message):
        self.message = message
