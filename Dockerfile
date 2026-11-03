FROM python:3.12-slim

WORKDIR /app

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY app.py .

# Streamlit 配置（Render 會注入 PORT 環境變數，預設 10000）
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_ENABLE_CORS=false
ENV STREAMLIT_CLIENT_TOOLBAR_MODE=minimal

EXPOSE 10000

# 啟動命令（shell form 讓 $PORT 展開，Render 會注入 PORT 環境變數）
CMD streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
