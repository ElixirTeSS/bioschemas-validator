FROM python:3.8
ENV PYTHONUNBUFFERED 1

WORKDIR /

RUN apt-get update

ADD requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

COPY ./ /validator
WORKDIR /validator

RUN python command.py buildprofile 

ENV PORT=${PORT:-8501}
EXPOSE 8501

ENTRYPOINT streamlit run --server.port $PORT website_st.py
#CMD ["website_st.py"]

