import web.formatting as fmt
import pandas as pd


def generate_report_summary(result):
    markdown = f"""
##### {fmt.header("Validating input:")}
##### {fmt.header("Against profile:")}  {result['Profile Name']} {result['Profile Version']}
## {fmt.header("Result:")}              {fmt.validity(result['Valid'])}
## {fmt.header("Summary:")}
    """
    return markdown


def generate_report_body(result):
    markdown = f"""
### {fmt.header("Validation Report")}
{get_errors_block(result['Error Messages'])}
### {fmt.header("Marginality Report")}
###### Minimum
{get_marginality_block('Minimum', result['Minimum'])}
###### Recommended
{get_marginality_block('Recommended', result['Recommended'])}
###### Optional
{get_marginality_block('Optional', result['Optional'])}
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
    block = ""
    # if len(subsection['Error']) > 0:
    #     for parameter in subsection['Error']:
    #         block = f'{block}\n\nAn error is reported for parameter {fmt.colour(parameter, "red")}'
    # else:
    #     block = f'{block}\n\nNo errors are reported at {level_name} level'

    if len(subsection['Missing']) > 0:
        for parameter in subsection['Missing']:
            block = f'{block}\n\nFor compliance with {level_name}, {fmt.colour(parameter, "red")} is needed'
    else:
        block = f'{block}\n\nAll parameters to comply with {level_name} are present.'

    # if len(subsection['Implemented']) > 0:
    #     block = f'{block}\n\nThe following parameters have been implemented: {*subsection["Implemented"],}'
    # else:
    #     block = f'{block}\n\nNo parameters have been implemented at {level_name} level'

    return block


def get_errors_block(error_strings):
    block = ""
    for Id, error in enumerate(error_strings):
        tag = fmt.colour(f'[Error {Id}]', 'red')
        block = f"{block}\n\n{tag} {error}"
    return block
