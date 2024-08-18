import shutil
from pathlib import Path

from fastapi.staticfiles import StaticFiles
from loguru import logger
import uvicorn
import yaml
from fastapi import FastAPI, HTTPException, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import PlainTextResponse
from sse_starlette import EventSourceResponse

from ..web_configs import API_CONFIG, WEB_CONFIGS
from .routers import llm, products, streamer_info, users
from .server_info import SERVER_PLUGINS_INFO
from .utils import ChatItem, streamer_sales_process

app = FastAPI()

# 注册路由
app.include_router(users.router)
app.include_router(products.router)
app.include_router(llm.router)
app.include_router(streamer_info.router)


# 挂载静态文件目录，以便访问上传的文件
WEB_CONFIGS.UPLOAD_FILE_SAVE_DIR = str(Path(WEB_CONFIGS.UPLOAD_FILE_SAVE_DIR).absolute())
Path(WEB_CONFIGS.UPLOAD_FILE_SAVE_DIR).mkdir(parents=True, exist_ok=True)
logger.info(f"上传文件挂载路径 {WEB_CONFIGS.UPLOAD_FILE_SAVE_DIR}")
logger.info(f"上传文件访问 URL {API_CONFIG.REQUEST_FILES_URL}")
app.mount(
    f"/{API_CONFIG.REQUEST_FILES_URL.split('/')[-1]}",
    StaticFiles(directory=WEB_CONFIGS.UPLOAD_FILE_SAVE_DIR),
    name=API_CONFIG.REQUEST_FILES_URL.split("/")[-1],
)


@app.get("/")
async def hello():
    return {"message": "Hello Streamer-Sales"}


@app.get("/streamer-sales/plugins_info")
async def get_plugins_info():
    return {
        "rag": True,
        "asr": SERVER_PLUGINS_INFO.asr_server_enabled,
        "tts": SERVER_PLUGINS_INFO.tts_server_enabled,
        "digital_human": SERVER_PLUGINS_INFO.digital_human_server_enabled,
        "agent": SERVER_PLUGINS_INFO.agent_enabled,
    }


@app.post("/streamer-sales/chat")
async def streamer_sales_chat(chat_item: ChatItem, response: Response):
    # 对话总接口
    response.headers["Content-Type"] = "text/event-stream"
    response.headers["Cache-Control"] = "no-cache"
    return EventSourceResponse(streamer_sales_process(chat_item))


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """调 API 入参错误的回调接口

    Args:
        request (_type_): _description_
        exc (_type_): _description_

    Returns:
        _type_: _description_
    """
    logger.info(request.json())
    logger.info(exc)
    return PlainTextResponse(str(exc), status_code=400)


# 执行
# uvicorn server.main:app --reload

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
