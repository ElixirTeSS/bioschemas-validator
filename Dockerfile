FROM python:3.10
ENV PYTHONUNBUFFERED 1

WORKDIR /

RUN apt-get update

ADD requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

WORKDIR /validator
RUN mkdir profile_json profile_marginality profileLive

COPY profile_yml profile_yml 

COPY command.py command.py
COPY website_st.py website_st.py
COPY src src

COPY .streamlit .streamlit
COPY web web

RUN python command.py buildprofile

ENV PORT=${PORT:-8501}
EXPOSE $PORT

CMD streamlit run --server.port $PORT website_st.py
#ENTRYPOINT streamlit run --server.port $PORT website_st.py
#CMD ["website_st.py"]

