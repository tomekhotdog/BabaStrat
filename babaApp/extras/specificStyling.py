

def get_sidebar_styling(selected_tab):
    style_dictionary = {
        selected_tab + '_li': "background: rgba(0, 0, 0, 0.15);box-shadow: inset 0 0 0.25em 0 rgba(0, 0, 0, 0.125);",
        selected_tab + '_span': "color: #e27689;"}

    return style_dictionary
