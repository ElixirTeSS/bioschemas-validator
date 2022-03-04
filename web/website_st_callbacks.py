import os

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
        validate(st.session_state.metadata,
                 static_jsonld  =(which == "url"),
                 sitemap_convert=(which == "sitemap")
                 )


def validate(target_data, static_jsonld=False, csv=True, profile=None, convert=False, sitemap_convert=False):
    # Perform validation
    result = command.validateData(target_data,
                                  static_jsonld=static_jsonld,
                                  csvNeeded=csv,
                                  profile=profile,
                                  convert=convert,
                                  sitemap_convert=sitemap_convert
                                  )
    st.session_state.result = result.result

    ## Parse result file
    with config.OUTPUT_LOCATION.open() as result_file:
        st.session_state.result_file = result_file.read()
