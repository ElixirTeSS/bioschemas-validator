import toml

red = '#FF0000'


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


def status(level_report_str):
    level_report = level_report_str  #level_report_str.replace('\n','\n\n')
    return level_report


