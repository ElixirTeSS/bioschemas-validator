import toml


def get_theme_colour(name):
    # Available in streamlit config:
    # primaryColor, backgroundColor, secondaryBackgroundColor, textColor, font
    theme = toml.load('.streamlit/config.toml')

    colour = "black"
    try:
        colour = theme["theme"][name]
    except Exception as e:
        print(f"No colour found matching {name} - returning black \n\n {e}")

    return colour


def colour(msg, colour):
    return f'<span style="color:{colour}">{msg}</span>'


def header(text):
    return colour(text, get_theme_colour("primaryColor"))


def validity(valid):
    if valid == 'True':
        return colour("Metadata is valid", get_theme_colour("textColor"))
    else:
        return colour("Metadata is NOT valid", "red")


def folding_context(headline, context):
    upper = f'<details><summary><b>{headline}</b></summary><p>'
    details = '\n\n'.join([f'{colour(ii, "yellow")}: {entry.message}' for ii,entry in enumerate(context)])
    lower = '</p></details>'

    fold = f'{upper}{details}{lower}'
    return fold
