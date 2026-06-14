# Vercel serverless entry point — imports the full FastAPI app.
# Vercel's Python runtime discovers `app` automatically.
from app.main import app  # noqa: F401
