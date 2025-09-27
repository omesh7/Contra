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

# Install Flask for web server and pygbag for web game conversion
RUN pip install --no-cache-dir flask pygbag

# Copy game files
COPY . .

# Set environment variables for headless pygame
ENV SDL_VIDEODRIVER=dummy
ENV SDL_AUDIODRIVER=dummy
ENV PYGAME_HIDE_SUPPORT_PROMPT=1

# Expose port 8080
EXPOSE 8080

# Start the playable web game
CMD ["python", "simple_web_game.py"]