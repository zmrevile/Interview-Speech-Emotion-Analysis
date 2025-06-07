#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
语音情感分析API服务器
专门用于集成到面试软件后端
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import tempfile
import logging
from speech_emotion_analyzer import SpeechEmotionAnalyzer
import traceback
import base64
import io

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建Flask应用
app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 全局变量 - 模型加载器（避免重复加载）
analyzer = None

def init_analyzer():
    """初始化语音情感分析器"""
    global analyzer
    try:
        if analyzer is None:
            logger.info("正在初始化语音情感分析器...")
            analyzer = SpeechEmotionAnalyzer()
            logger.info(f"分析器初始化完成，已加载 {len(analyzer.models)} 个模型")
        return True
    except Exception as e:
        logger.error(f"分析器初始化失败: {e}")
        return False

def create_response(success=True, data=None, message="", error_code=None):
    """创建标准化的API响应"""
    response = {
        "success": success,
        "message": message,
        "data": data
    }
    if error_code:
        response["error_code"] = error_code
    return jsonify(response)

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    try:
        if analyzer is None:
            return create_response(False, None, "分析器未初始化", "ANALYZER_NOT_READY")
        
        return create_response(True, {
            "status": "healthy",
            "models_loaded": len(analyzer.models),
            "available_models": list(analyzer.models.keys())
        }, "服务运行正常")
    except Exception as e:
        return create_response(False, None, f"健康检查失败: {str(e)}", "HEALTH_CHECK_ERROR")

@app.route('/analyze', methods=['POST'])
def analyze_emotion():
    """
    语音情感分析接口
    
    支持两种输入方式：
    1. 文件上传 (multipart/form-data)
    2. Base64编码的音频数据 (JSON)
    """
    try:
        if analyzer is None:
            return create_response(False, None, "分析器未初始化", "ANALYZER_NOT_READY")
        
        audio_file_path = None
        
        # 方式1: 文件上传
        if 'audio' in request.files:
            audio_file = request.files['audio']
            if audio_file.filename == '':
                return create_response(False, None, "未选择文件", "NO_FILE_SELECTED")
            
            # 保存临时文件
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            audio_file.save(temp_file.name)
            audio_file_path = temp_file.name
            
        # 方式2: Base64编码数据
        elif request.is_json:
            data = request.get_json()
            if 'audio_data' not in data:
                return create_response(False, None, "缺少audio_data字段", "MISSING_AUDIO_DATA")
            
            # 解码Base64音频数据
            try:
                audio_data = base64.b64decode(data['audio_data'])
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
                temp_file.write(audio_data)
                temp_file.close()
                audio_file_path = temp_file.name
            except Exception as e:
                return create_response(False, None, f"音频数据解码失败: {str(e)}", "DECODE_ERROR")
        
        else:
            return create_response(False, None, "请提供音频文件或Base64编码的音频数据", "NO_AUDIO_PROVIDED")
        
        # 进行情感分析
        logger.info(f"开始分析音频文件: {audio_file_path}")
        result = analyzer.analyze_audio(audio_file_path)
        
        # 清理临时文件
        try:
            os.unlink(audio_file_path)
        except:
            pass
        
        # 格式化响应数据
        response_data = format_analysis_result(result)
        
        return create_response(True, response_data, "分析完成")
        
    except Exception as e:
        logger.error(f"分析过程中发生错误: {str(e)}")
        logger.error(traceback.format_exc())
        return create_response(False, None, f"分析失败: {str(e)}", "ANALYSIS_ERROR")

def format_analysis_result(result):
    """格式化分析结果为API友好的格式"""
    try:
        # 提取基本信息
        basic_info = {
            "duration": result.get("duration", 0),
            "sample_rate": result.get("sample_rate", 0),
            "models_count": len(result.get("models_results", []))
        }
        
        # 提取模型结果
        models_results = []
        for model_result in result.get("models_results", []):
            models_results.append({
                "model_name": model_result.get("model", "unknown"),
                "predicted_emotion": model_result.get("predicted_emotion", "unknown"),
                "confidence": round(float(model_result.get("confidence", 0)), 3),
                "emotions_scores": {k: round(float(v), 3) for k, v in model_result.get("emotions", {}).items()}
            })
        
        # 提取综合结果
        summary = result.get("summary", {})
        final_result = {
            "recommended_emotion": summary.get("recommended_emotion", "unknown"),
            "confidence": round(float(summary.get("confidence", 0)), 3),
            "best_model": summary.get("best_model", "unknown"),
            "average_confidence": round(float(summary.get("average_confidence", 0)), 3),
            "models_consensus": summary.get("consensus", False)
        }
        
        # 生成面试评分和建议
        interview_assessment = generate_interview_assessment(final_result)
        
        return {
            "basic_info": basic_info,
            "models_results": models_results,
            "final_result": final_result,
            "interview_assessment": interview_assessment
        }
        
    except Exception as e:
        logger.error(f"格式化结果时发生错误: {str(e)}")
        return {"error": "格式化结果失败"}

def generate_interview_assessment(final_result):
    """生成面试评估"""
    emotion = final_result.get("recommended_emotion", "unknown")
    confidence = final_result.get("confidence", 0)
    
    # 面试情感分类和评分
    emotion_scoring = {
        # 正面情感 (高分)
        "自信": {"base_score": 90, "type": "excellent", "desc": "表现出色"},
        "沉着": {"base_score": 85, "type": "excellent", "desc": "沉稳可靠"}, 
        "平静": {"base_score": 75, "type": "good", "desc": "状态良好"},
        "专注": {"base_score": 80, "type": "good", "desc": "专注投入"},
        
        # 中性情感 (中等分)
        "兴奋": {"base_score": 70, "type": "neutral", "desc": "略显激动"},
        
        # 负面情感 (低分)
        "紧张": {"base_score": 45, "type": "poor", "desc": "显得紧张"},
        "焦虑": {"base_score": 40, "type": "poor", "desc": "较为焦虑"},
        "不满": {"base_score": 35, "type": "poor", "desc": "情绪不佳"}
    }
    
    # 获取情感评分信息
    emotion_info = emotion_scoring.get(emotion, {"base_score": 60, "type": "neutral", "desc": "状态中等"})
    base_score = emotion_info["base_score"]
    emotion_type = emotion_info["type"]
    emotion_desc = emotion_info["desc"]
    
    # 根据置信度调整分数
    confidence_bonus = (confidence - 0.5) * 20  # 置信度超过0.5才加分
    final_score = min(100, max(0, base_score + confidence_bonus))
    
    # 生成建议
    recommendations = []
    
    if emotion == "自信":
        recommendations.append("情感表达非常自信，表现优秀")
        recommendations.append("继续保持这种状态")
    elif emotion == "沉着":
        recommendations.append("表现沉着冷静，给人可靠感")
        recommendations.append("适当增加一些积极表达")
    elif emotion == "平静":
        recommendations.append("状态平和稳定")
        recommendations.append("可以适当表现更多自信")
    elif emotion == "专注":
        recommendations.append("展现出很好的专注力")
        recommendations.append("保持这种投入状态")
    elif emotion == "兴奋":
        recommendations.append("表现出积极的态度")
        recommendations.append("注意控制情绪，保持专业")
    elif emotion == "紧张":
        recommendations.append("适度紧张是正常的，注意放松")
        recommendations.append("可以通过深呼吸缓解紧张感")
        recommendations.append("多做准备有助于增强信心")
    elif emotion == "焦虑":
        recommendations.append("建议调整心态，保持冷静")
        recommendations.append("专注于问题本身，不要过度担心")
        recommendations.append("提前准备可以减少焦虑")
    elif emotion == "不满":
        recommendations.append("注意情绪管理，保持专业态度")
        recommendations.append("即使遇到困难也要积极应对")
    
    # 根据置信度添加建议
    if confidence < 0.4:
        recommendations.append("情感表达不够清晰，建议更明确地表达想法")
    elif confidence > 0.8:
        recommendations.append("情感表达很清晰，继续保持")
    
    return {
        "emotion_type": emotion_type,
        "emotion_description": emotion_desc,
        "score": round(final_score, 1),
        "confidence_level": "高" if confidence > 0.7 else ("中" if confidence > 0.4 else "低"),
        "recommendations": recommendations,
        "detailed_analysis": {
            "detected_emotion": emotion,
            "confidence_score": round(float(confidence), 3),
            "base_score": int(base_score),
            "confidence_adjustment": round(float(confidence_bonus), 1)
        }
    }

@app.route('/batch_analyze', methods=['POST'])
def batch_analyze():
    """批量分析接口（适用于分析整个面试会话）"""
    try:
        if analyzer is None:
            return create_response(False, None, "分析器未初始化", "ANALYZER_NOT_READY")
        
        if not request.is_json:
            return create_response(False, None, "请提供JSON格式数据", "INVALID_FORMAT")
        
        data = request.get_json()
        audio_segments = data.get('audio_segments', [])
        
        if not audio_segments:
            return create_response(False, None, "请提供音频片段数据", "NO_AUDIO_SEGMENTS")
        
        # 分析每个音频片段
        results = []
        for i, segment_data in enumerate(audio_segments):
            try:
                # 解码Base64音频数据
                audio_data = base64.b64decode(segment_data)
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
                temp_file.write(audio_data)
                temp_file.close()
                
                # 分析单个片段
                result = analyzer.analyze_audio(temp_file.name)
                formatted_result = format_analysis_result(result)
                formatted_result['segment_id'] = i + 1
                results.append(formatted_result)
                
                # 清理临时文件
                os.unlink(temp_file.name)
                
            except Exception as e:
                logger.error(f"分析片段 {i+1} 时发生错误: {str(e)}")
                results.append({
                    "segment_id": i + 1,
                    "error": str(e)
                })
        
        # 生成整体报告
        overall_report = generate_overall_report(results)
        
        return create_response(True, {
            "segments_results": results,
            "overall_report": overall_report
        }, f"批量分析完成，共处理 {len(audio_segments)} 个片段")
        
    except Exception as e:
        logger.error(f"批量分析失败: {str(e)}")
        return create_response(False, None, f"批量分析失败: {str(e)}", "BATCH_ANALYSIS_ERROR")

def generate_overall_report(results):
    """生成整体面试报告"""
    valid_results = [r for r in results if 'error' not in r]
    
    if not valid_results:
        return {"error": "没有有效的分析结果"}
    
    # 统计情感分布
    emotions = [r['final_result']['recommended_emotion'] for r in valid_results]
    emotion_counts = {}
    for emotion in emotions:
        emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
    
    # 计算平均分数
    scores = [r['interview_assessment']['score'] for r in valid_results]
    avg_score = sum(scores) / len(scores)
    
    # 主导情感
    dominant_emotion = max(emotion_counts, key=emotion_counts.get)
    
    # 情感稳定性
    stability = 1 - (len(set(emotions)) / len(emotions))
    
    # 面试表现分析
    excellent_count = sum(1 for r in valid_results if r['interview_assessment']['emotion_type'] == 'excellent')
    good_count = sum(1 for r in valid_results if r['interview_assessment']['emotion_type'] == 'good')
    poor_count = sum(1 for r in valid_results if r['interview_assessment']['emotion_type'] == 'poor')
    
    # 整体评价
    if avg_score >= 80:
        overall_performance = "优秀"
    elif avg_score >= 70:
        overall_performance = "良好"
    elif avg_score >= 60:
        overall_performance = "中等"
    else:
        overall_performance = "需要改进"
    
    # 生成面试建议
    interview_suggestions = []
    
    if dominant_emotion in ["紧张", "焦虑"]:
        interview_suggestions.append("建议在面试前做好充分准备，提高自信心")
        interview_suggestions.append("可以练习放松技巧，如深呼吸")
    elif dominant_emotion in ["自信", "沉着"]:
        interview_suggestions.append("表现非常出色，继续保持这种状态")
    elif dominant_emotion == "平静":
        interview_suggestions.append("状态稳定，可以适当增加一些积极表达")
    
    if stability < 0.5:
        interview_suggestions.append("情绪波动较大，建议保持情绪稳定")
    elif stability > 0.8:
        interview_suggestions.append("情绪表现稳定，非常好")
    
    return {
        "total_segments": len(results),
        "valid_segments": len(valid_results),
        "average_score": round(avg_score, 1),
        "overall_performance": overall_performance,
        "dominant_emotion": dominant_emotion,
        "emotion_distribution": emotion_counts,
        "emotional_stability": round(stability, 3),
        "stability_level": "高" if stability > 0.7 else ("中" if stability > 0.4 else "低"),
        "performance_breakdown": {
            "excellent_segments": excellent_count,
            "good_segments": good_count,
            "poor_segments": poor_count
        },
        "interview_suggestions": interview_suggestions
    }

@app.errorhandler(404)
def not_found(error):
    return create_response(False, None, "接口不存在", "NOT_FOUND"), 404

@app.errorhandler(500)
def internal_error(error):
    return create_response(False, None, "服务器内部错误", "INTERNAL_ERROR"), 500

if __name__ == "__main__":
    # 启动时初始化分析器
    logger.info("正在启动语音情感分析API服务器...")
    
    if init_analyzer():
        logger.info("API服务器启动成功！")
        print("🎤 语音情感分析API服务器")
        print("=" * 40)
        print("🌐 服务地址: http://localhost:5000")
        print("📋 可用接口:")
        print("  GET  /health - 健康检查")
        print("  POST /analyze - 单个音频分析") 
        print("  POST /batch_analyze - 批量音频分析")
        print("=" * 40)
        
        # 启动Flask服务器
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=False,
            threaded=True
        )
    else:
        logger.error("分析器初始化失败，无法启动服务器")
        exit(1) 