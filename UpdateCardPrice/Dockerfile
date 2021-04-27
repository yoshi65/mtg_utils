FROM public.ecr.aws/lambda/python:3.8

COPY lambda_function.py ./
COPY requirements.txt ./
RUN pip install -r requirements.txt

CMD ["lambda_function.lambda_handler"]
