# 🎤 语音情感分析API集成指南

## 📋 概述

这是一个专门为面试软件后端设计的语音情感分析API服务。您可以轻松地将其集成到现有的面试系统中。

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install flask flask-cors
```

### 2. 启动API服务器
```bash
python emotion_api.py
```

服务器将在 `http://localhost:5000` 启动

## 📋 API接口文档

### 1. 健康检查
**接口**: `GET /health`

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
**接口**: `POST /analyze`

#### 方式1: 文件上传
```bash
curl -X POST -F "audio=@test.wav" http://localhost:5000/analyze
```

#### 方式2: Base64数据
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"audio_data": "base64编码的音频数据"}' \
  http://localhost:5000/analyze
```

**响应示例**:
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
    "models_results": [
             {
         "model_name": "ExHuBERT",
         "predicted_emotion": "自信",
         "confidence": 0.756,
         "emotions_scores": {
           "自信": 0.756,
           "平静": 0.123,
           "紧张": 0.121,
           "焦虑": 0.089,
           "沉着": 0.067,
           "专注": 0.024
         }
       }
    ],
         "final_result": {
       "recommended_emotion": "自信",
       "confidence": 0.756,
       "best_model": "ExHuBERT",
       "average_confidence": 0.652,
       "models_consensus": true
     },
     "interview_assessment": {
       "emotion_type": "excellent",
       "emotion_description": "表现出色",
       "score": 95.1,
       "confidence_level": "高",
       "recommendations": ["情感表达非常自信，表现优秀", "继续保持这种状态"],
       "detailed_analysis": {
         "detected_emotion": "自信",
         "confidence_score": 0.756,
         "base_score": 90,
         "confidence_adjustment": 5.1
       }
     }
  }
}
```

### 3. 批量分析（面试会话）
**接口**: `POST /batch_analyze`

**请求示例**:
```json
{
  "audio_segments": [
    "base64编码的音频片段1",
    "base64编码的音频片段2",
    "base64编码的音频片段3"
  ]
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "批量分析完成，共处理 3 个片段",
  "data": {
    "segments_results": [...],
    "         overall_report": {
           "total_segments": 3,
           "valid_segments": 3,
           "average_score": 82.5,
           "overall_performance": "良好",
           "dominant_emotion": "平静",
           "emotion_distribution": {
             "平静": 2,
             "自信": 1
           },
           "emotional_stability": 0.667,
           "stability_level": "中",
           "performance_breakdown": {
             "excellent_segments": 1,
             "good_segments": 2,
             "poor_segments": 0
           },
           "interview_suggestions": ["状态稳定，可以适当增加一些积极表达"]
         }
  }
}
```

## 🎯 面试情感类别

本系统专门针对面试场景设计，识别以下8种面试相关情感：

### 正面情感（高分）
- **自信** (90分基础分): 表现出色，充满自信
- **沉着** (85分基础分): 沉稳可靠，处变不惊 
- **专注** (80分基础分): 专注投入，认真对待
- **平静** (75分基础分): 状态良好，心态平和

### 中性情感（中等分）
- **兴奋** (70分基础分): 略显激动，需要控制

### 负面情感（低分）
- **紧张** (45分基础分): 显得紧张，需要放松
- **焦虑** (40分基础分): 较为焦虑，需要调整心态
- **不满** (35分基础分): 情绪不佳，需要情绪管理

### 评分机制
- **基础分**: 根据情感类别的基础分数
- **置信度调整**: 根据AI模型的置信度进行微调 (+/-20分)
- **最终分数**: 0-100分，分数越高表示面试表现越好

## 💻 集成示例代码

### Python集成示例

```python
import requests
import base64

def analyze_interview_audio(audio_file_path):
    """分析面试音频文件"""
    
    # 方式1: 文件上传
    with open(audio_file_path, 'rb') as f:
        files = {'audio': f}
        response = requests.post('http://localhost:5000/analyze', files=files)
    
    if response.status_code == 200:
        result = response.json()
        if result['success']:
            return result['data']
        else:
            print(f"分析失败: {result['message']}")
            return None
    else:
        print(f"请求失败: {response.status_code}")
        return None

def analyze_with_base64(audio_bytes):
    """使用Base64数据分析"""
    
    # 编码音频数据
    audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
    
    # 发送请求
    data = {'audio_data': audio_b64}
    response = requests.post(
        'http://localhost:5000/analyze',
        json=data,
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code == 200:
        return response.json()['data']
    return None

# 使用示例
result = analyze_interview_audio('interview_audio.wav')
if result:
    print(f"情感: {result['final_result']['recommended_emotion']}")
    print(f"评分: {result['interview_assessment']['score']}")
    print(f"建议: {result['interview_assessment']['recommendations']}")
```

### JavaScript集成示例

```javascript
// 分析音频文件
async function analyzeAudio(audioFile) {
    const formData = new FormData();
    formData.append('audio', audioFile);
    
    try {
        const response = await fetch('http://localhost:5000/analyze', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        if (result.success) {
            return result.data;
        } else {
            console.error('分析失败:', result.message);
            return null;
        }
    } catch (error) {
        console.error('请求失败:', error);
        return null;
    }
}

// 使用Base64数据分析
async function analyzeWithBase64(audioBase64) {
    try {
        const response = await fetch('http://localhost:5000/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                audio_data: audioBase64
            })
        });
        
        const result = await response.json();
        return result.success ? result.data : null;
    } catch (error) {
        console.error('分析失败:', error);
        return null;
    }
}

// 批量分析示例
async function batchAnalyze(audioSegments) {
    try {
        const response = await fetch('http://localhost:5000/batch_analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                audio_segments: audioSegments
            })
        });
        
        const result = await response.json();
        return result.success ? result.data : null;
    } catch (error) {
        console.error('批量分析失败:', error);
        return null;
    }
}
```

### Java集成示例

```java
import okhttp3.*;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.File;
import java.util.Base64;

public class EmotionAnalysisClient {
    private final OkHttpClient client = new OkHttpClient();
    private final String baseUrl = "http://localhost:5000";
    private final ObjectMapper mapper = new ObjectMapper();
    
    public AnalysisResult analyzeAudio(File audioFile) throws Exception {
        RequestBody requestBody = new MultipartBody.Builder()
            .setType(MultipartBody.FORM)
            .addFormDataPart("audio", audioFile.getName(),
                RequestBody.create(audioFile, MediaType.parse("audio/wav")))
            .build();
        
        Request request = new Request.Builder()
            .url(baseUrl + "/analyze")
            .post(requestBody)
            .build();
        
        try (Response response = client.newCall(request).execute()) {
            if (response.isSuccessful()) {
                String responseBody = response.body().string();
                ApiResponse apiResponse = mapper.readValue(responseBody, ApiResponse.class);
                return apiResponse.isSuccess() ? apiResponse.getData() : null;
            }
        }
        return null;
    }
    
    public AnalysisResult analyzeWithBase64(byte[] audioData) throws Exception {
        String audioBase64 = Base64.getEncoder().encodeToString(audioData);
        
        RequestData requestData = new RequestData();
        requestData.setAudioData(audioBase64);
        
        RequestBody requestBody = RequestBody.create(
            mapper.writeValueAsString(requestData),
            MediaType.parse("application/json")
        );
        
        Request request = new Request.Builder()
            .url(baseUrl + "/analyze")
            .post(requestBody)
            .build();
        
        try (Response response = client.newCall(request).execute()) {
            if (response.isSuccessful()) {
                String responseBody = response.body().string();
                ApiResponse apiResponse = mapper.readValue(responseBody, ApiResponse.class);
                return apiResponse.isSuccess() ? apiResponse.getData() : null;
            }
        }
        return null;
    }
}
```

## 🏗️ 架构建议

### 1. 微服务部署
将情感分析API作为独立的微服务部署：

```yaml
# docker-compose.yml
version: '3.8'
services:
  emotion-analysis:
    build: .
    ports:
      - "5000:5000"
    environment:
      - CUDA_VISIBLE_DEVICES=0  # 如果有GPU
    volumes:
      - ./models:/app/models
    restart: unless-stopped
```

### 2. 负载均衡
如果面试量大，可以使用Nginx进行负载均衡：

```nginx
upstream emotion_api {
    server localhost:5000;
    server localhost:5001;
    server localhost:5002;
}

server {
    listen 80;
    location /emotion/ {
        proxy_pass http://emotion_api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3. 缓存策略
对于相同的音频文件，可以使用Redis缓存结果：

```python
import redis
import hashlib

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def get_audio_hash(audio_data):
    return hashlib.md5(audio_data).hexdigest()

def cache_result(audio_hash, result):
    redis_client.setex(f"emotion:{audio_hash}", 3600, json.dumps(result))

def get_cached_result(audio_hash):
    cached = redis_client.get(f"emotion:{audio_hash}")
    return json.loads(cached) if cached else None
```

## 🔧 部署建议

### 1. 生产环境部署
```bash
# 使用gunicorn部署
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 emotion_api:app
```

### 2. 性能优化
- 使用GPU加速推理
- 模型预加载（避免每次请求重新加载）
- 批量处理音频
- 异步处理（对于非实时需求）

### 3. 监控和日志
```python
import logging
from prometheus_client import Counter, Histogram

# 监控指标
request_count = Counter('emotion_api_requests_total', 'Total requests')
request_duration = Histogram('emotion_api_request_duration_seconds', 'Request duration')

# 在接口中添加监控
@request_duration.time()
def analyze_emotion():
    request_count.inc()
    # ... 分析逻辑
```

## 🔒 安全考虑

### 1. API认证
```python
from functools import wraps

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key != 'your-secret-key':
            return create_response(False, None, "未授权", "UNAUTHORIZED"), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/analyze', methods=['POST'])
@require_api_key
def analyze_emotion():
    # ... 分析逻辑
```

### 2. 速率限制
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["100 per hour"]
)

@app.route('/analyze', methods=['POST'])
@limiter.limit("10 per minute")
def analyze_emotion():
    # ... 分析逻辑
```

## 📞 技术支持

如有集成问题，请参考：
1. 检查API服务器状态：`GET /health`
2. 查看服务器日志
3. 确保音频格式正确（16kHz WAV推荐）
4. 验证Base64编码正确性

---

**这个API设计简单易用，您只需要关注业务逻辑，我们处理所有AI模型的复杂性！** 🚀 