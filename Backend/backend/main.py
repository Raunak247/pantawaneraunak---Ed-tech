import uvicorn
from src.app import create_app
import os

app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    # Use app directly instead of a module string
    uvicorn.run(app, host="0.0.0.0", port=port)
