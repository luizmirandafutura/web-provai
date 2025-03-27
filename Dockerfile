# Use Python 3.13
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies required for some Python packages
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . .

# Instala o uv
RUN pip install uv

# Instala as dependências e cria o ambiente virtual
RUN uv sync --frozen --no-cache

# Expõe a porta do streamlit
EXPOSE 8501

# Set environment variables for Streamlit
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Run the Streamlit app
CMD ["uv", "run", "streamlit", "run", "app.py"]
