FROM python:3.11

# Install minimal SDL2 dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsdl2-2.0-0 \
    libsdl2-image-2.0-0 \
    libsdl2-mixer-2.0-0 \
    libsdl2-ttf-2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy game files
COPY . .

# Set environment variables for pygame
ENV PYGAME_HIDE_SUPPORT_PROMPT=1
# Remove dummy drivers to allow graphics

# Default command
CMD ["python", "main.py"]