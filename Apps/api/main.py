
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from services.mongodb_vector_store import MongoDBVectorStoreManager

# Import routers
from routers.process_router import router as process_router, set_mongodb_manager as set_process_manager
from routers.search_router import router as search_router, set_mongodb_manager as set_search_manager
from routers.generate_router import router as generate_router, set_mongodb_manager as set_generate_manager
from routers.videos_router import router as videos_router, set_mongodb_manager as set_videos_manager
from routers.stats_router import router as stats_router, set_mongodb_manager as set_stats_manager
from routers.root_router import router as root_router
from routers.health_router import router as health_router


# Load environment variables
load_dotenv()


# Global MongoDB vector store manager
mongodb_manager: MongoDBVectorStoreManager = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup and shutdown logic
    global mongodb_manager
    api_key = os.getenv("GOOGLE_API_KEY")
    mongodb_uri = os.getenv("MONGODB_URI")
    if api_key and mongodb_uri:
        try:
            mongodb_manager = MongoDBVectorStoreManager(api_key=api_key, mongodb_uri=mongodb_uri)
            print("✅ MongoDB Vector Store Manager initialized")
            # Inject manager into routers
            set_process_manager(mongodb_manager)
            set_search_manager(mongodb_manager)
            set_generate_manager(mongodb_manager)
            set_videos_manager(mongodb_manager)
            set_stats_manager(mongodb_manager)
        except Exception as e:
            print(f"❌ ERROR: Failed to connect to MongoDB: {str(e)}")
    else:
        print("❌ ERROR: GOOGLE_API_KEY or MONGODB_URI not set!")
    yield
    if mongodb_manager:
        mongodb_manager.close()
    print("👋 Application shutdown complete")


app = FastAPI(
    title="YouTube RAG Pipeline API",
    description="RAG pipeline for YouTube videos",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(root_router)
app.include_router(health_router)
app.include_router(process_router)
app.include_router(search_router)
app.include_router(generate_router)
app.include_router(videos_router)
app.include_router(stats_router)


if __name__ == "__main__":
    import uvicorn
    import sys
    if not os.getenv("GOOGLE_API_KEY"):
        print("=" * 60)
        print("ERROR: GOOGLE_API_KEY environment variable not set!")
        print("=" * 60)
        print("\nPlease set your Google API key:")
        print("  export GOOGLE_API_KEY='your-api-key-here'")
        print("\nOr create a .env file with:")
        print("  GOOGLE_API_KEY=your-api-key-here")
        print("=" * 60)
        exit(1)
    is_debugging = sys.gettrace() is not None
    if is_debugging:
        print("🐛 Running in DEBUG mode (breakpoints enabled)")
        uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
    else:
        print("🚀 Running in DEVELOPMENT mode (auto-reload enabled)")
        uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
