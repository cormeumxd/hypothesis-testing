FROM python:3.11

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8501 8888

CMD ["sh", "-c", "streamlit run dashboard.py --server.port=8501 & jupyter notebook --port=8888 --ip=0.0.0.0 --allow-root"]
