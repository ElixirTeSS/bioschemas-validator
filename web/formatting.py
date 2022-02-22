import toml

red = '#FF0000'

# Available in streamlit config:
# primaryColor, backgroundColor, secondaryBackgroundColor, textColor, font


def header(text):
    theme = toml.load('.streamlit/config.toml')
    return f'<span style="color:{theme["theme"]["primaryColor"]}">{text}</span>'


def validity(valid):
    theme = toml.load('.streamlit/config.toml')

    if valid == 'True':
        return f'<span style="color:{theme["theme"]["textColor"]}">Metadata is valid</span>'
    else:
        return f'<span style="color:{red}">Metadata is NOT valid</span>'


def status(line):
    print(repr(line))
