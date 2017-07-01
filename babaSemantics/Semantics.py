import collections
import itertools

GROUNDED = 1
SCEPTICALLY_PREFERRED = 2
IDEAL = 3


# Bayesian Assumption-Based Argumentation
class BABA:
    # BABA = (F^A, BN, RV) where F^A = ABA framework: (L, R, A, _) (Language, Rules, Assumptions, Contraries),
        # BN = Bayesian network,
        # RV = Random variables
    # rules = [Rule(Sentence, [Sentence])...]
    # contraries = {Sentence (assumption) : Contrary}
    # random_variables = [RandomVariable(Sentence, Probability)...]
    def __init__(self, language, rules, assumptions, contraries, random_variables, BN):
        self.language = language
        self.rules = rules
        self.assumptions = assumptions
        self.contraries = contraries
        self.random_variables = random_variables
        self.BN = BN
        self.rv_world = []

        self.validate()

    # Validates BABA framework
    def validate(self):
        self.validate_language_covers_all_sentences()
        self.validate_is_flat()
        self.validate_random_variables()

    # Sets the world of random variables for semantics calculations
    def set_random_variable_world(self, random_variable_world):
        self.rv_world = random_variable_world

    # Checks whether all atoms defined in rules, assumptions,
    # contraries and random variables are included in the language
    def validate_language_covers_all_sentences(self):
        exception_message = "Language must include all sentences defined in network"
        for rule in self.rules:
            if rule.head not in self.language:
                raise InvalidBABAException(exception_message)
            for element in rule.body:
                if element not in self.language:
                    raise InvalidBABAException(exception_message)

        for assumption in self.assumptions:
            if assumption not in self.language:
                raise InvalidBABAException(exception_message)

        for assumption, contrary in self.contraries.items():
            if assumption not in self.language or contrary.contrary not in self.language:
                raise InvalidBABAException(exception_message)

        for random_variable in self.random_variables:
            if random_variable not in self.language:
                raise InvalidBABAException(exception_message)

    # Checks if underlying ABA network is flat
    def validate_is_flat(self):
        for rule in self.rules:
            if rule.head in self.assumptions:
                raise InvalidBABAException("Framework is not flat")

    # Ensures no random variables as heads of rules
    def validate_random_variables(self):
        for rule in self.rules:
            if rule.head in self.random_variables:
                raise InvalidBABAException("Random variables cannot be in the heads of rules")


class Sentence:
    def __init__(self, symbol, random_variable=False, negation=False):
        self.symbol = symbol
        self.random_variable = random_variable
        self.negation = negation

    def __hash__(self):
        return hash(self.symbol) + hash(self.random_variable) + hash(self.negation)

    def __eq__(self, other):
        return self.symbol == other.symbol and self.random_variable == other.random_variable\
           and self.negation == other.negation

    def __str__(self):
        return self.symbol if not self.negation else "~" + self.symbol


class Rule:
    def __init__(self, head, body=[]):
        self.head = head
        self.body = body

    def __hash__(self):
        return hash(self.head) + sum([hash(item) for item in self.body])

    def __eq__(self, other):
        head_equal = self.head == other.head
        body_equal = all([elem in other.body for elem in self.body]) and len(self.body) == len(other.body)
        return head_equal and body_equal

    def __str__(self):
        return str(self.head) + " :- " + ', '.join([str(elem) for elem in self.body])


class Contrary:
    def __init__(self, assumption, contrary):
        if assumption == contrary:
            raise InvalidContraryException(
                "An assumption cannot be a contrary of itself")

        self.assumption = assumption
        self.contrary = contrary

    def __hash__(self):
        return hash(self.assumption) + hash(self.contrary)

    def __eq__(self, other):
        return self.assumption == other.assumption and self.contrary == other.contrary

    def __str__(self):
        return str(self.assumption) + ", " + str(self.contrary)


# A set of sentences, 'support', derives the contrary of the 'attacked' sentence
class Attack:
    def __init__(self, attacked, support):
        self.attacked = attacked
        self.support = support

    def __hash__(self):
        return hash(self.attacked) + sum([hash(item) for item in self.support])

    def __eq__(self, other):
        return (self.attacked == other.attacked and
                all([s in other.support for s in self.support]) and
                len(self.support) == len(other.support))


# A container class for a list of sentences
class SemanticSet:
    def __init__(self, elements):
        self.elements = elements

    def __hash__(self):
        return sum([hash(item) for item in self.elements])

    def __eq__(self, other):
        return all([elem in other.elements for elem in self.elements]) \
               and len(self.elements) == len(other.elements)

    def __str__(self):
        return "[" + ', '.join([str(elem) for elem in self.elements]) + "]"


class InvalidBABAException(Exception):
    def __init__(self, message):
        self.message = message


class InvalidContraryException(Exception):
    def __init__(self, message):
        self.message = message


class InvalidSemanticsException(Exception):
    def __init__(self, message):
        self.message = message


# Returns whether a claim is derivable in a BABA framework from a set of sentences
def derivable(baba, claim, sentences):
    if claim in sentences or claim in baba.rv_world:
        return True
    for rule in baba.rules:
        if claim == rule.head:
            if all([derivable(baba, element, sentences) for element in rule.body]):
                return True
    return False


# Returns the complete set of sentences derivable from the BABA framework given a set of sentences
def derivable_set(baba, sentences):
    for sentence in baba.language:
        if sentence not in sentences and derivable(baba, sentence, sentences):
            return derivable_set(baba, sentences + [sentence])
    return sentences


# Returns a list of lists of sentences required to derive a claim
def required_to_derive(baba, claim):
    if claim in baba.assumptions or claim in baba.random_variables:
        return [[claim]]

    required = []
    for rule in baba.rules:
        required_to_derive_claim = []
        if rule.head == claim:
            for sentence in rule.body:
                required_to_derive_sentence = required_to_derive(baba, sentence)
                required_to_derive_claim = list_combinations(required_to_derive_claim, required_to_derive_sentence)

            for derivation in required_to_derive_claim:
                if derivable(baba, claim, derivation):
                    required.append(derivation)

    return required


# Returns a set of contraries to the given set of sentences in the BABA framework
def contraries(baba, sentences):
    contrary_set = set()
    for sentence in sentences:
        if sentence in baba.contraries:
            contrary_set.add(baba.contraries[sentence].contrary)
    return contrary_set


# Returns a set of all potential Attacks against elements of attacked
def generate_attacks(baba, attacked):
    attack_set = set()
    for element in attacked:
        if element not in baba.contraries:
            continue

        contrary = baba.contraries[element].contrary
        required_to_derive_contrary = required_to_derive(baba, contrary)
        if len(required_to_derive_contrary) == 0:
            if derivable(baba, contrary, []):
                attack_set.add(Attack(element, set([])))
        else:
            for given_list in required_to_derive_contrary:
                attack_set.add(Attack(element, set(given_list)))

    return attack_set


# Returns whether the given attack holds in the given baba framework and random variable world
def valid_attack(baba, attack):
    return all([(elem in baba.assumptions or elem in baba.rv_world) for elem in attack.support])


# Returns whether the set of assumptions defends the claim -
# where A defends a iff A attacks all sets of assumptions that attack a)
def defends(baba, assumptions, claim):
    attacks = generate_attacks(baba, [claim])
    for attack in attacks:

        if not valid_attack(baba, attack):
            continue

        support_contraries = contraries(baba, attack.support)
        if len(attack.support) == 0:  # Attack cannot be countered
            is_counter_attacked = False
        elif len(support_contraries) == 0:  # Attack support has no contrary
            is_counter_attacked = True
        else:
            is_counter_attacked = any([derivable(baba, elem, assumptions + baba.rv_world) for elem in support_contraries])

        if not is_counter_attacked:
            return False

    return True


# Returns whether the list of assumptions is conflict free
def conflict_free(baba, assumptions):
    contrary_set = contraries(baba, derivable_set(baba, assumptions))
    return not any([derivable(baba, contrary, assumptions) for contrary in contrary_set])


# Returns whether the list of assumptions is admissible in the BABA framework
def admissible(baba, assumptions):
    if not conflict_free(baba, assumptions):
        return False

    for attack in generate_attacks(baba, assumptions):
        if not valid_attack(baba, attack):
            continue

        support_contraries = contraries(baba, attack.support)
        if not any(derivable(baba, s, (assumptions + baba.rv_world)) for s in support_contraries)\
                and len(support_contraries) > 0:
            return False

    return True


# Generates the complete set of admissible sets of assumptions
def generate_admissible(baba):
    return set([SemanticSet(elem) for elem in powerset(baba.assumptions) if admissible(baba, elem)])


############################################################
# The following methods generate all lists of assumptions
# that satisfy the corresponding semantics

def preferred(baba, admissibles=None):
    admissible_sets = admissibles if admissibles is not None else generate_admissible(baba)
    preferred_sets = []

    for ad_set in admissible_sets:
        remaining_sets = admissible_sets - set([ad_set])
        if not any([all([elem in current.elements for elem in ad_set.elements])
                    for current in remaining_sets]):
            preferred_sets.append(ad_set)

    return preferred_sets


def sceptically_preferred(baba, admissibles=None):
    admissible_sets = admissibles if admissibles is not None else generate_admissible(baba)
    preferred_sets = preferred(baba, admissible_sets)
    return set([group_intersection(preferred_sets)])


def complete(baba, admissibles=None):
    admissible_sets = admissibles if admissibles is not None else generate_admissible(baba)
    complete_sets = []

    for ad_set in admissible_sets:
        elements_not_in_set = [elem for elem in baba.assumptions if elem not in ad_set.elements]
        if not any([defends(baba, ad_set.elements, element) for element in elements_not_in_set]):
            complete_sets.append(ad_set)

    return complete_sets


def grounded(baba, admissibles=None):
    admissible_sets = admissibles if admissibles is not None else generate_admissible(baba)
    return set(minimal_set(complete(baba, admissible_sets)))


# TODO: clear up definition. Definition provided: "ideal: iff it is maximally (w.r.t. ⊆) admissible and contained in
# all preferred sets of assumptions" - however, preferred === maximally admissible? (implementation appears to work)
def ideal(baba, admissibles=None):
    admissible_sets = admissibles if admissibles is not None else generate_admissible(baba)
    preferred_sets = preferred(baba, admissible_sets)
    return [p for p in admissible_sets if
            all([elem in other.elements for elem in p.elements for other in preferred_sets])]


def stable(baba, admissibles=None):
    admissible_sets = admissibles if admissibles is not None else generate_admissible(baba)
    stable_sets = []
    for admissible_set in admissible_sets:
        not_in_set = [elem for elem in baba.assumptions if elem not in admissible_set.elements]
        contraries_to_derive = contraries(baba, not_in_set)
        if all([derivable(baba, contrary, admissible_set.elements) for contrary in contraries_to_derive]):
            stable_sets.append(admissible_set)

    return stable_sets


#################################################################################################
#                                         Utility Methods
#################################################################################################


# Definition of BABA semantics: acceptance probability
# of a set of sentences (w.r.t. to a given semantics)
def semantic_probability(semantics, baba, sentences):
    if not all([s in baba.language for s in sentences]):
        raise InvalidBABAException("Semantic probability enquired for invalid set of sentences")

    worlds = generate_worlds(baba.random_variables)
    acceptability_probability = 0.0

    for world in worlds:
        baba.set_random_variable_world(world)

        if semantics == GROUNDED:
            semantic_sets = grounded(baba)
        elif semantics == SCEPTICALLY_PREFERRED:
            semantic_sets = sceptically_preferred(baba)
        elif semantics == IDEAL:
            semantic_sets = ideal(baba)
        else:
            raise InvalidSemanticsException("Invalid semantics chosen: " + str(semantics))

        can_derive_sentence = False

        for a_set in semantic_sets:
            can_derive_sentence = all([derivable(baba, s, a_set.elements + baba.rv_world) for s in sentences])

        if can_derive_sentence:
            acceptability_probability += baba.BN.p_world(world)

    return acceptability_probability


# Returns a dictionary of {symbol : semantic probability}
def compute_semantic_probability(semantics, baba):
    language_probability = {}
    for sentence in baba.language:
        language_probability[sentence.symbol] = 0.0

    worlds = generate_worlds(baba.random_variables)
    worlds = [[]] if len(worlds) == 0 else worlds

    for world in worlds:
        baba.set_random_variable_world(world)

        if semantics == GROUNDED:
            semantic_sets = grounded(baba)
        elif semantics == SCEPTICALLY_PREFERRED:
            semantic_sets = sceptically_preferred(baba)
        elif semantics == IDEAL:
            semantic_sets = ideal(baba)
        else:
            raise InvalidSemanticsException("Invalid semantics chosen: " + str(semantics))

        world_probability = baba.BN.p_world(world) if len(world) > 0 else 1.0

        for sentence in baba.language:
            if any(derivable(baba, sentence, a_set.elements + baba.rv_world) for a_set in semantic_sets):
                language_probability[sentence.symbol] += world_probability

    return language_probability


# Returns semantic probabilities for a BABA framework for given semantics
def compute_semantic_probabilities_for_semantics(baba, semantics):
    probabilities = compute_semantic_probability(semantics, baba)
    tuples = [(sentence, "{0:.3f}".format(probability)) for sentence, probability in probabilities.items()]
    tuples = sorted(tuples, key=lambda item: item[0])

    return tuples


# Returns a tuple of the semantic probabilities for a BABA
# (probabilities given as lists of (sentence, probability) string tuple
def compute_semantic_probabilities(baba):
    grounded_tuples = compute_semantic_probabilities_for_semantics(baba, GROUNDED)
    s_preferred_tuples = compute_semantic_probabilities_for_semantics(baba, SCEPTICALLY_PREFERRED)
    ideal_tuples = compute_semantic_probabilities_for_semantics(baba, IDEAL)

    return grounded_tuples, s_preferred_tuples, ideal_tuples

##############################################################

TURNSTILE = "&#x22a2;"


# Returns a product of the given lists or
# a concatenation in the case of an empty list
def list_combinations(first_list, second_list):
    if (len(first_list) == 0) or (len(second_list) == 0):
        return list(first_list + second_list)

    combinations = list(itertools.product(first_list, second_list))
    return [base_elements(combination) for combination in combinations]


# Returns all the root elements in a multi level list
def base_elements(a_list):
    return [item for sublist in a_list for item in sublist]


# Adapted from: http://stackoverflow.com/questions/1482308/whats-a-good-way-to-combinate-through-a-set
# example usage: powerset([a,b,c]) --> () (a) (b) (c) (a,b) (a,c) (b,c) (a,b,c)
def powerset(iterable):
    s = list(iterable)
    return [list(element) for element in
            list(itertools.chain.from_iterable(itertools.combinations(s, r) for r in range(len(s)+1)))]


# Returns the intersection of a set of SemanticSet objects
def group_intersection(semantic_sets):
    intersection = semantic_sets.pop().elements if len(semantic_sets) > 0 else []
    for element in semantic_sets:
        intersection = [elem for elem in element.elements if elem in intersection]

    return SemanticSet(intersection)


# Returns the minimal set of the given sentences (w.r.t. the given sets)
def minimal_set(semantic_sets):
    minimal_sets = []
    for semantic_set in semantic_sets:
        if not any(
            [all([elem in semantic_set.elements for elem in other.elements]) and
             len(semantic_set.elements) > len(other.elements) for other in semantic_sets]):
                minimal_sets.append(semantic_set)

    return minimal_sets


# Returns all the possible worlds created with the given random variables
def generate_worlds(random_variables):
    worlds = []

    for rv in random_variables:
        pos = Sentence(rv.symbol, random_variable=True)
        neg = Sentence(rv.symbol, random_variable=True, negation=True)\

        possible_world = [pos, neg]
        if len(worlds) == 0:
            worlds = [[pos], [neg]]
            continue

        worlds = list(itertools.product(worlds, possible_world))
        worlds = [flatten(list(world)) for world in worlds]

    return worlds


def flatten(items):
    return [elem for item in items for elem in flatten(item)] \
        if isinstance(items, collections.Iterable) else [items]


# Creates a list of strings representing a list of (SemanticSet, derivation set) tuples
def extensions_and_derivations_to_str_list(extension_derivation_tuples):
    string_list = []
    for extension, derivation in extension_derivation_tuples:
        string_list.append('{' + ', '.join([s.symbol for s in extension.elements]) + '}' + " |- " +
                           '{' + ', '.join([s.symbol for s in derivation]) + '}')
    return string_list


# Returns a tuple of lists of strings representing a baba framework
# ([language], [assumptions], [contraries], [random variables], [rules])
def string_representation(baba):
    language = [str(elem) for elem in baba.language]
    assumptions = [str(elem) for elem in baba.assumptions]
    contrary_elems = [str(baba.contraries[elem]) for elem in baba.contraries]
    rvs = [(str(elem) + ', ' + str(baba.BN.p(elem))) for elem in baba.random_variables]
    rules = [str(elem) for elem in baba.rules]

    return language, assumptions, contrary_elems, rvs, rules
