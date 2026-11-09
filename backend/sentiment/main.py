"""
启动程序入口
"""

import uvicorn

from sentiment.engines.contract.settings import get_settings

if __name__ == '__main__':
    uvicorn.run(app="sentiment.app.app:app", host=get_settings().HOST, port=get_settings().PORT)
