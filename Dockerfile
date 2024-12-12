FROM python:3.9-slim

WORKDIR /app

COPY . .

# Generate points and update visualization
RUN python3 generate_points.py

EXPOSE 8000

CMD ["python", "server.py"]
