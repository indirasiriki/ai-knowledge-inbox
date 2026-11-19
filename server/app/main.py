from app.config import config
from app.factory import create_app

# Imported by uvicorn as app.main:app. This opens the real SQLite file.
app = create_app()


def main():
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=config.port, reload=False)


if __name__ == "__main__":
    main()
