FROM python:3.12-slim

WORKDIR /app

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY app.py .

# Streamlit 配置（Cloud Run 通过 PORT 环境变量注入）
ENV STREAMLIT_SERVER_PORT=8080
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_ENABLE_CORS=false
ENV STREAMLIT_CLIENT_TOOLBAR_MODE=minimal

EXPOSE 8080

# 启动命令
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]
