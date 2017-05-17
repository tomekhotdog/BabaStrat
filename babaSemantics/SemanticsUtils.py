import collections
import itertools
import babaSemantics.Semantics as Semantics

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

    return Semantics.SemanticSet(intersection)


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
        pos = Semantics.Sentence(rv.symbol, random_variable=True)
        neg = Semantics.Sentence(rv.symbol, random_variable=True, negation=True)\

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
    contraries = [str(elem) for elem in baba.contraries]
    rvs = [str(elem) for elem in baba.random_variables]
    rules = [str(elem) for elem in baba.rules]

    return language, assumptions, contraries, rvs, rules
