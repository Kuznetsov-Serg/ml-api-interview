# main.py
import uvicorn

if __name__ == "__main__":
    # Запускаем приложение из модуля app.main
    # host="0.0.0.0" необходим для доступа извне контейнера Docker
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # В production заменить на False
        workers=1     # Для асинхронного кода с uvicorn обычно 1 worker, масштабирование через Docker/K8s
    )