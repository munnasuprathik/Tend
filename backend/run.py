"""
Simple script to run the FastAPI server
Run this from the backend directory: python run.py
Or use uvicorn directly: uvicorn server:app --reload
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["."]
    )

