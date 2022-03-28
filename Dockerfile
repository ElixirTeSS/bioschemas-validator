FROM python:3.8
ENV PYTHONUNBUFFERED 1

WORKDIR /

RUN apt-get update

ADD requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

COPY ./ /validator
WORKDIR /validator

RUN python command.py buildprofile 

EXPOSE 8501
ENTRYPOINT ["streamlit", "run", "--server.port", "$PORT"]
CMD ["website_st.py"]

