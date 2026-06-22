FROM python:3.13-slim

WORKDIR /app

COPY . .

ENV LEAD_TOOL_HOST=0.0.0.0
ENV PORT=10000

EXPOSE 10000

CMD ["python", "server.py"]
