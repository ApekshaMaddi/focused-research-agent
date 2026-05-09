FROM python:3.13-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Create non-root user — required by Hugging Face Spaces
RUN useradd -m -u 1000 appuser

WORKDIR /app

# Copy project files
COPY --chown=appuser:appuser pyproject.toml .
COPY --chown=appuser:appuser uv.lock .
COPY --chown=appuser:appuser src/ src/
COPY --chown=appuser:appuser start.sh .

# Switch to non-root user
USER appuser

# Install production dependencies only
RUN uv sync --frozen --no-dev

# Make start script executable
RUN chmod +x start.sh

# Expose Streamlit port — Hugging Face Spaces uses 7860
EXPOSE 7860

CMD ["./start.sh"]