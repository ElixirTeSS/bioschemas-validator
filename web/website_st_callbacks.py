import streamlit as st
import src.command as command
import src.Classes.config as config


def input_changed(which):
    metadata = ""
    if which == "url":
        metadata = st.session_state.url
    elif which == "sitemap":
        metadata = st.session_state.sitemap
    elif which == "raw":
        metadata = st.session_state.raw
    else:
        print("OWDB: Error no metadata specified") 

    st.session_state.metadata = metadata
    with st.spinner(text='Performing Validation...'):

        validate(st.session_state.url,
                 static_jsonld=(which == "url"),
                 sitemap_convert=(which == "sitemap")
                 )


def validate(target_data, static_jsonld=False, csv="N", profile="N", convert=False, sitemap_convert=False):
    command.validateData(target_data,
                         static_jsonld,
                         csv,
                         profile,
                         convert,
                         sitemap_convert
                         )

    with config.OUTPUT_LOCATION.open() as resultFile:
        st.session_state.result = resultFile.read()
