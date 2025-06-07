# 🎤 语音情感分析API部署指南

## 📋 项目概述

这是一个专门为面试场景设计的高精度语音情感分析系统，提供RESTful API接口，可以轻松集成到现有的面试软件后端中。

### 🎯 核心特性

- **高精度多模型集成**: 使用ExHuBERT、HuBERT Large、Wav2Vec2 XLSR等SOTA模型
- **面试专用评估**: 提供情感评分、稳定性分析、专业建议
- **简单易用API**: RESTful接口，支持文件上传和Base64数据
- **批量处理**: 支持分析整个面试会话
- **GPU加速**: 支持CUDA加速推理
- **实时监控**: 健康检查和性能监控

## 🏗️ 系统架构

```
面试软件后端
    ↓ HTTP API调用
语音情感分析API服务器 (Flask)
    ↓ 模型推理
AI模型集成器 (ExHuBERT + HuBERT + Wav2Vec2)
    ↓ 结果整合
面试评估引擎
    ↓ JSON响应
面试软件后端
```

## 📁 项目文件结构

```
yuying/
├── emotion_api.py              # API服务器主文件
├── speech_emotion_analyzer.py  # 核心分析器
├── start_api_server.py        # 启动脚本
├── test_api.py               # API测试脚本
├── api_integration_guide.md  # 集成指南
├── requirements.txt          # 依赖包
└── README.md                # 项目说明
```

## 🚀 快速部署

### 1. 环境准备

```bash
# 克隆项目（如果从其他地方获取）
# git clone <项目地址>
# cd yuying

# 安装依赖
pip install -r requirements.txt

# 验证安装
python -c "import torch; print('PyTorch版本:', torch.__version__)"
python -c "import transformers; print('Transformers版本:', transformers.__version__)"
```

### 2. 启动API服务器

```bash
# 方式1: 使用启动脚本（推荐）
python start_api_server.py

# 方式2: 直接启动
python emotion_api.py

# 方式3: 生产环境部署
gunicorn -w 4 -b 0.0.0.0:5000 emotion_api:app
```

### 3. 验证部署

```bash
# 健康检查
curl http://localhost:5000/health

# 运行完整测试
python test_api.py
```

## 🔗 API接口详情

### 基础URL
```
http://localhost:5000
```

### 1. 健康检查
```http
GET /health
```

**响应示例**:
```json
{
  "success": true,
  "message": "服务运行正常",
  "data": {
    "status": "healthy",
    "models_loaded": 3,
    "available_models": ["exhubert", "hubert_large", "wav2vec2_xlsr"]
  }
}
```

### 2. 单个音频分析
```http
POST /analyze
```

**输入方式**:
- 文件上传: `multipart/form-data` 格式，字段名 `audio`
- Base64数据: JSON格式，字段 `audio_data`

**响应格式**:
```json
{
  "success": true,
  "message": "分析完成",
  "data": {
    "basic_info": {
      "duration": 3.0,
      "sample_rate": 16000,
      "models_count": 3
    },
    "models_results": [...],
    "final_result": {
      "recommended_emotion": "高兴",
      "confidence": 0.756,
      "best_model": "ExHuBERT",
      "average_confidence": 0.652,
      "models_consensus": true
    },
    "interview_assessment": {
      "emotion_type": "positive",
      "score": 95.1,
      "confidence_level": "高",
      "recommendations": ["情感表现积极，继续保持"]
    }
  }
}
```

### 3. 批量分析
```http
POST /batch_analyze
```

**输入格式**:
```json
{
  "audio_segments": [
    "base64编码的音频片段1",
    "base64编码的音频片段2",
    "base64编码的音频片段3"
  ]
}
```

## 💻 集成示例

### Python集成
```python
import requests
import base64

# 分析音频文件
def analyze_interview_audio(audio_file_path):
    with open(audio_file_path, 'rb') as f:
        files = {'audio': f}
        response = requests.post('http://localhost:5000/analyze', files=files)
    
    if response.status_code == 200:
        result = response.json()
        if result['success']:
            data = result['data']
            return {
                'emotion': data['final_result']['recommended_emotion'],
                'score': data['interview_assessment']['score'],
                'confidence': data['final_result']['confidence'],
                'recommendations': data['interview_assessment']['recommendations']
            }
    return None

# 使用示例
result = analyze_interview_audio('interview_recording.wav')
if result:
    print(f"情感: {result['emotion']}")
    print(f"评分: {result['score']}")
    print(f"建议: {result['recommendations']}")
```

### JavaScript集成
```javascript
// 分析音频文件
async function analyzeAudio(audioFile) {
    const formData = new FormData();
    formData.append('audio', audioFile);
    
    const response = await fetch('http://localhost:5000/analyze', {
        method: 'POST',
        body: formData
    });
    
    const result = await response.json();
    return result.success ? result.data : null;
}

// 使用示例
const audioFile = document.getElementById('audioInput').files[0];
const result = await analyzeAudio(audioFile);
if (result) {
    console.log('情感:', result.final_result.recommended_emotion);
    console.log('评分:', result.interview_assessment.score);
}
```

## 🏭 生产环境部署

### 1. Docker部署

创建 `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# 复制文件
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# 暴露端口
EXPOSE 5000

# 启动命令
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "emotion_api:app"]
```

创建 `docker-compose.yml`:
```yaml
version: '3.8'
services:
  emotion-api:
    build: .
    ports:
      - "5000:5000"
    environment:
      - CUDA_VISIBLE_DEVICES=0  # 如果有GPU
    volumes:
      - ./models:/app/models
    restart: unless-stopped
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]  # 如果使用GPU
```

### 2. 负载均衡配置

Nginx配置 (`/etc/nginx/sites-available/emotion-api`):
```nginx
upstream emotion_api {
    server localhost:5000;
    server localhost:5001;
    server localhost:5002;
}

server {
    listen 80;
    server_name your-domain.com;
    
    location /api/emotion/ {
        proxy_pass http://emotion_api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 60s;
    }
}
```

### 3. 监控和日志

添加到 `emotion_api.py`:
```python
import logging
from prometheus_client import Counter, Histogram, generate_latest

# 监控指标
REQUEST_COUNT = Counter('emotion_api_requests_total', 'Total requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('emotion_api_request_duration_seconds', 'Request duration')

@app.route('/metrics')
def metrics():
    return generate_latest()

# 在每个接口中添加监控
@REQUEST_DURATION.time()
def analyze_emotion():
    REQUEST_COUNT.labels('POST', '/analyze').inc()
    # ... 原有逻辑
```

## 🔒 安全配置

### 1. API密钥认证
```python
def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key != os.environ.get('API_SECRET_KEY'):
            return create_response(False, None, "未授权", "UNAUTHORIZED"), 401
        return f(*args, **kwargs)
    return decorated_function
```

### 2. 速率限制
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["1000 per hour", "100 per minute"]
)

@app.route('/analyze', methods=['POST'])
@limiter.limit("10 per minute")
def analyze_emotion():
    # ... 分析逻辑
```

## 📊 性能优化

### 1. 模型缓存
- 服务器启动时预加载所有模型
- 使用内存缓存避免重复加载
- GPU显存管理和复用

### 2. 请求优化
- 异步处理非实时请求
- 批量处理多个音频文件
- 结果缓存（相同音频文件）

### 3. 硬件建议
- **CPU**: 8核以上，推荐Intel i7或AMD Ryzen 7
- **内存**: 16GB以上（模型加载需要大量内存）
- **GPU**: NVIDIA RTX 3060以上（可选，用于加速推理）
- **存储**: SSD，用于快速模型加载

## 🐛 故障排除

### 常见问题

**1. 模型下载失败**
```bash
# 手动下载模型
export HF_ENDPOINT=https://hf-mirror.com
python -c "from transformers import AutoModel; AutoModel.from_pretrained('facebook/hubert-large-ls960-ft')"
```

**2. CUDA内存不足**
```python
# 在emotion_api.py中添加
import torch
torch.cuda.empty_cache()
```

**3. 音频格式不支持**
- 确保音频为16kHz采样率
- 支持WAV、MP3、M4A等格式
- 音频长度建议1-30秒

**4. API超时**
- 增加请求超时时间
- 检查网络连接
- 确认服务器资源充足

### 日志查看
```bash
# 查看API服务器日志
tail -f emotion_api.log

# Docker容器日志
docker logs emotion-api
```

## 📞 技术支持

### 监控检查清单
- [ ] API健康检查返回200状态码
- [ ] 所有模型成功加载
- [ ] GPU/CPU资源使用正常
- [ ] 内存使用在合理范围内
- [ ] 网络连接稳定
- [ ] 日志无异常错误

### 联系方式
- 技术文档: `api_integration_guide.md`
- 测试工具: `python test_api.py`
- 监控面板: `http://localhost:5000/health`

---

**🎉 部署完成后，您的面试软件就可以拥有专业的语音情感分析能力了！**

这个API设计简洁高效，专门针对面试场景优化，提供准确的情感分析和专业的评估建议。 