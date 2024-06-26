# 基于FastAPI的csr_to_ca系统
## 介绍
本系统是基于高性能FastAPI框架的csr_to_ca系统
## 软件架构
FastAPI
## platform
Linux
## 部署
### docker 部署
```bash
chmod 777 docker-start.sh
docker build ./ -t csr_to_ca
docker run -itd -p 127.0.0.1:8011:8011/tcp csr_to_ca:latest
```
### 查看容器内生成的文件
```bash
docker exec -it 容器ID bash
```

## 接口文档
本系统支持swaggerUI，并且支持通过openapi.json在线导入到第三方工具，
下面是获取这两种文档格式的地址 
- 应用文档地址：http://127.0.0.1:8000/docs
- 应用openapi.json获取地址：http://127.0.0.1:8000/openapi.json
