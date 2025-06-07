# 🎤 面试语音情感分析API系统

一个专门为**面试场景**设计的高精度语音情感分析系统，提供RESTful API接口，可以轻松集成到现有的面试软件后端中。

## ✨ 主要特性

### 🧠 多模型集成
- **ExHuBERT**: 最新的语音情感识别模型，支持6维情感分析
- **HuBERT Large**: SUPERB基准测试顶级模型，专业的4类情感识别
- **Wav2Vec2 XLSR**: 多语言预训练模型，支持8种详细情感分类

### 🎯 面试专用功能
- **面试情感识别**: 识别紧张、自信、焦虑、平静等8种面试相关情感
- **情感稳定性分析**: 评估面试过程中的情绪变化
- **置信度评估**: 判断情感表达的清晰度
- **专业建议生成**: 基于情感分析结果提供面试改进建议

### 🔗 API接口
- **RESTful API**: 标准HTTP接口，支持任何编程语言集成
- **多种输入方式**: 支持文件上传和Base64编码数据
- **批量处理**: 支持分析整个面试会话
- **实时响应**: 快速的情感分析和评估

## 🚀 快速开始

### 环境要求
- Python 3.8+
- PyTorch 2.0+
- CUDA (推荐，用于GPU加速)

### 安装依赖
```bash
pip install -r requirements.txt
```

### 启动API服务器

#### 1. 使用启动脚本（推荐）
```bash
python start_api_server.py
```

#### 2. 直接启动API
```bash
python emotion_api.py
```

服务器将在 `http://localhost:5000` 启动

### 测试API功能
```bash
python test_api.py
```

## 📋 API接口文档

### 1. 健康检查
```http
GET /health
```

### 2. 单个音频分析
```http
POST /analyze
```

**输入方式**:
- 文件上传: `multipart/form-data` 格式
- Base64数据: JSON格式

**示例请求**:
```bash
# 文件上传
curl -X POST -F "audio=@interview.wav" http://localhost:5000/analyze

# Base64数据
curl -X POST -H "Content-Type: application/json" \
  -d '{"audio_data": "base64编码的音频数据"}' \
  http://localhost:5000/analyze
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
    "base64编码的音频片段2"
  ]
}
```

## 🎯 面试情感类别

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

## 💻 集成示例

### Python集成
```python
import requests

def analyze_interview_audio(audio_file_path):
    with open(audio_file_path, 'rb') as f:
        files = {'audio': f}
        response = requests.post('http://localhost:5000/analyze', files=files)
    
    if response.status_code == 200:
        result = response.json()['data']
        return {
            'emotion': result['final_result']['recommended_emotion'],
            'score': result['interview_assessment']['score'],
            'confidence': result['final_result']['confidence'],
            'recommendations': result['interview_assessment']['recommendations']
        }
    return None

# 使用示例
result = analyze_interview_audio('interview.wav')
if result:
    print(f"情感: {result['emotion']}")
    print(f"评分: {result['score']}")
    print(f"建议: {result['recommendations']}")
```

### JavaScript集成
```javascript
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
```

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

## 📊 评分机制

### 情感评分
- **基础分**: 根据情感类别的基础分数(35-90分)
- **置信度调整**: 根据AI模型的置信度进行微调(±20分)
- **最终分数**: 0-100分，分数越高表示面试表现越好

### 稳定性分析
- **高稳定性** (>0.7): 情绪变化小，表现一致
- **中等稳定性** (0.4-0.7): 适度的情感变化
- **低稳定性** (<0.4): 情绪波动较大

## 🔧 部署建议

### 生产环境
```bash
# 使用gunicorn部署
gunicorn -w 4 -b 0.0.0.0:5000 emotion_api:app
```

### Docker部署
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "emotion_api:app"]
```

## 📚 技术文档

- **API集成指南**: `api_integration_guide.md`
- **部署指南**: `DEPLOYMENT_GUIDE.md`
- **测试工具**: `python test_api.py`

## 🎯 应用场景

### 1. 在线面试平台
- 实时分析面试者情感状态
- 提供面试质量评估
- 辅助面试官决策

### 2. HR系统集成
- 批量分析面试录音
- 生成情感分析报告
- 面试流程优化

### 3. 面试培训系统
- 模拟面试情感分析
- 提供改进建议
- 面试技能训练

## 💡 使用建议

### 音频质量要求
- **采样率**: 建议16kHz
- **格式**: WAV, MP3, M4A等
- **时长**: 建议1-30秒的语音片段
- **环境**: 避免背景噪音

### 最佳实践
1. **多模型验证**: 参考多个模型的结果
2. **置信度参考**: 高置信度结果更可靠
3. **批量分析**: 分析整个面试会话获得更准确的评估
4. **结合人工**: API结果作为辅助参考，不替代人工判断

## 🔍 故障排除

### 常见问题
1. **模型下载失败**: 检查网络连接，使用镜像源
2. **CUDA内存不足**: 减少批处理大小或使用CPU
3. **音频格式不支持**: 确保音频为常见格式
4. **API超时**: 检查音频文件大小和网络状况

### 获取帮助
- 查看 `DEPLOYMENT_GUIDE.md` 详细部署指南
- 运行 `python test_api.py` 进行系统诊断
- 访问 `http://localhost:5000/health` 检查服务状态

---

**🎉 这个API系统让您的面试软件拥有专业的语音情感分析能力！** 