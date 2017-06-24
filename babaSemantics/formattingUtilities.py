from babaSemantics import BABAProgramParser as Parser, Semantics


def get_semantic_probabilities_html(framework_string):
    baba = Parser.BABAProgramParser(string=framework_string).parse()
    sentence_probability_tuples = Semantics.compute_semantic_probabilities_for_semantics(baba, Semantics.IDEAL)

    html = ''
    for tuple in sentence_probability_tuples:
        tuple_html = tuple[0] + ': ' + tuple[1] + '<br/>'
        html += tuple_html

    return html