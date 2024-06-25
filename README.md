# 基于FastAPI的患者管理系统
## 介绍
本系统是基于高性能FastAPI框架的csr_to_ca系统
## 软件架构
FastAPI
## platform
Linux
## python env

3.12.0

Python 安装方式：

1. 直接安装 Python 3.12.0
2. Pyenv 安装 Python 3.12.0
3. Anaconda 安装 Python 3.12.0

安装依赖命令

```bash
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
```

## 配置文件

1. settings.py
2. gunicorn.conf.py

## 部署
### uvicorn 部署
```bash
uvicorn main:app_api 
```
此时应用会在前台运行, 若需要后台运行则可使用 `screen` 或 `nohup` 命令.
### docker 部署
```bash
docker build . -t csr_to_ca:0.0.1
docker run csr_to_ca:0.0.1
```


## 接口文档
本系统支持swaggerUI，并且支持通过openapi.json在线导入到第三方工具，
下面是获取这两种文档格式的地址 
- 应用文档地址：http://127.0.0.1:8000/docs
- 后台管理文档地址：http://127.0.0.1:8000/admin_api/docs
- 应用openapi.json获取地址：http://127.0.0.1:8000/openapi.json
- 后台管理openapi.json获取地址：http://127.0.0.1:8000/admin_api/openapi.json

## 开发规范
