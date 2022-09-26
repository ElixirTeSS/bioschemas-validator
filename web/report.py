import streamlit as st
import pandas as pd

import web.formatting as fmt


def generate_report_summary(result):
    markdown = f"""
##### {fmt.header("Validating input:")} {st.session_state.metadata}
##### {fmt.header("Against profile:")}  {result['Profile Name']} {result['Profile Version']}
## {fmt.header("Result:")}              {fmt.validity(result['Valid'])}
## {fmt.header("Summary:")}
    """
    return markdown


def generate_report_body(result):
    markdown = f"""
### {fmt.header("Marginality Report")}
###### Minimum
{get_marginality_block('Minimum', result['Minimum'])}
###### Recommended
{get_marginality_block('Recommended', result['Recommended'])}
###### Optional
{get_marginality_block('Optional', result['Optional'])}
### {fmt.header("Validation Report")}
{get_errors_block(result['Error Messages'])}
"""
    return markdown


def color_severity(column):
    level_map = {"Minimum": "#ed2939", "Recommended": "#f3e260", "Optional": "#4fc3f7"}
    cmap = []

    for entry in column.items():
        row_name = entry[0]
        value = entry[1]
        if row_name == 'Implemented':
            cmap.append(f"background-color: {fmt.get_theme_colour('secondaryBackgroundColor')}; color: 'black'")
        else:
            bg_colour = level_map[column.name] if (value > 0) else fmt.get_theme_colour('secondaryBackgroundColor')
            fg_colour = 'white' if value > 0 else 'black'
            cmap.append(f"background-color: {bg_colour}; color: {fg_colour}")
    return cmap


def get_dataframe(result):
    result_totals = {}
    for marginality in (['Minimum', 'Recommended', 'Optional']):
        result_totals[marginality] = {}
        for severity in (['Error', 'Missing', 'Implemented']):
            result_totals[marginality][severity] = len(result[marginality][severity])

    report_dataframe = pd.DataFrame.from_dict(result_totals)
    report_dataframe = report_dataframe.style.apply(color_severity)

    return report_dataframe


def get_validation_message(subsection):
    f'{fmt.colour("Errors:","red")}'


def get_marginality_block(level_name, subsection):
    block = f'\n\nAll parameters to comply with {level_name} are present.'
    
    if len(subsection['Missing']) > 0:
        missing = ', '.join([fmt.colour(parameter, "red") for parameter in subsection['Missing']])
        block = f'\n\nNeeded for compliance with {level_name}: {missing}'

    return block


def get_errors_block(error_strings):
    block = ""
    for Id, error in enumerate(error_strings):
        message = error['message']
        context = error['context']

        tag = fmt.colour(f'[Error {Id}]', 'red')
        headline = f"{tag} {message}"
        block = f"{block}\n\n{fmt.folding_context(headline, context)}"

    return block
