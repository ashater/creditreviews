#FROM public.ecr.aws/lambda/python:3.12
FROM ubuntu:20.04

ARG DEBIAN_FRONTEND=noninteractive

# Copy requirements.txt
COPY requirements.txt ${LAMBDA_TASK_ROOT}

RUN apt-get update

RUN apt-get install -y python3 pip  libleptonica-dev tesseract-ocr libtesseract-dev python3-pil tesseract-ocr-eng tesseract-ocr-script-latn poppler-utils

# Install the specified packages
RUN pip install -r requirements.txt

# Copy function code
COPY lambda_function.py ${LAMBDA_TASK_ROOT}

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "lambda_function.handler" ]
