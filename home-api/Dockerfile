FROM 3.7-alpine

WORKDIR /usr/src/app

ENV FLASK_APP=api/app.py

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["flask", "run"]