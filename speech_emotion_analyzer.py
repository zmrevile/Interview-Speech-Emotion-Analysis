import torch
import librosa
import numpy as np
import pandas as pd
from transformers import (
    AutoModelForAudioClassification, 
    Wav2Vec2FeatureExtractor,
    HubertForSequenceClassification,
    pipeline
)
import warnings
warnings.filterwarnings('ignore')

class SpeechEmotionAnalyzer:
    """
    高精度语音情感分析器
    集成多个SOTA模型用于面试语音情感分析
    """
    
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"使用设备: {self.device}")
        
        # 初始化多个模型
        self.models = {}
        self.feature_extractors = {}
        self.load_models()
    
    def load_models(self):
        """加载多个高精度语音情感分析模型"""
        print("正在加载语音情感分析模型...")
        
        try:
            # 1. ExHuBERT - 高精度多语言情感模型 (推荐用于面试场景)
            print("加载 ExHuBERT 模型...")
            self.models['exhubert'] = AutoModelForAudioClassification.from_pretrained(
                "amiriparian/ExHuBERT", 
                trust_remote_code=True
            ).to(self.device)
            self.feature_extractors['exhubert'] = Wav2Vec2FeatureExtractor.from_pretrained(
                "facebook/hubert-base-ls960"
            )
            print("✓ ExHuBERT 模型加载完成")
            
        except Exception as e:
            print(f"ExHuBERT 模型加载失败: {e}")
        
        try:
            # 2. HuBERT Large - SUPERB基准测试模型
            print("加载 HuBERT Large 模型...")
            self.models['hubert_large'] = HubertForSequenceClassification.from_pretrained(
                "superb/hubert-large-superb-er"
            ).to(self.device)
            self.feature_extractors['hubert_large'] = Wav2Vec2FeatureExtractor.from_pretrained(
                "superb/hubert-large-superb-er"
            )
            print("✓ HuBERT Large 模型加载完成")
            
        except Exception as e:
            print(f"HuBERT Large 模型加载失败: {e}")
        
        try:
            # 3. Wav2Vec2 XLSR - 多语言情感识别模型
            print("加载 Wav2Vec2 XLSR 模型...")
            self.models['wav2vec2_xlsr'] = AutoModelForAudioClassification.from_pretrained(
                "ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition"
            ).to(self.device)
            self.feature_extractors['wav2vec2_xlsr'] = Wav2Vec2FeatureExtractor.from_pretrained(
                "ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition"
            )
            print("✓ Wav2Vec2 XLSR 模型加载完成")
            
        except Exception as e:
            print(f"Wav2Vec2 XLSR 模型加载失败: {e}")
        
        if not self.models:
            raise Exception("所有模型加载失败，请检查网络连接和模型可用性")
    
    def preprocess_audio(self, audio_path, target_sr=16000, max_length=48000):
        """
        预处理音频文件
        Args:
            audio_path: 音频文件路径
            target_sr: 目标采样率
            max_length: 最大长度（3秒 * 16kHz = 48000）
        """
        try:
            # 加载音频文件
            waveform, sr = librosa.load(audio_path, sr=target_sr)
            
            # 填充或截断到固定长度
            if len(waveform) > max_length:
                waveform = waveform[:max_length]
            else:
                waveform = np.pad(waveform, (0, max_length - len(waveform)))
            
            return waveform, target_sr
        
        except Exception as e:
            raise Exception(f"音频预处理失败: {e}")
    
    def map_to_interview_emotions(self, original_emotions, scores):
        """将原始情感映射到面试相关情感"""
        # 面试情感映射规则
        mapping = {
            # 原始情感 -> 面试情感
            '愤怒': '紧张',
            '悲伤': '焦虑', 
            '恐惧': '紧张',
            '厌恶': '不满',
            '高兴': '自信',
            '中性': '平静',
            '惊讶': '兴奋',
            '平静': '平静',
            
            # ExHuBERT特殊映射
            '低唤醒-负面': '焦虑',
            '低唤醒-中性': '平静', 
            '低唤醒-正面': '沉着',
            '高唤醒-负面': '紧张',
            '高唤醒-中性': '专注',
            '高唤醒-正面': '自信'
        }
        
        # 面试相关情感类别
        interview_emotions = ['紧张', '焦虑', '平静', '自信', '沉着', '专注', '兴奋', '不满']
        
        # 创建面试情感得分字典
        interview_scores = {emotion: 0.0 for emotion in interview_emotions}
        
        # 映射和累积得分
        for i, original_emotion in enumerate(original_emotions):
            if original_emotion in mapping:
                interview_emotion = mapping[original_emotion]
                interview_scores[interview_emotion] += float(scores[i])
        
        # 找到最高得分的情感
        predicted_emotion = max(interview_scores, key=interview_scores.get)
        confidence = interview_scores[predicted_emotion]
        
        # 确保所有值都是Python原生类型
        interview_scores = {k: float(v) for k, v in interview_scores.items()}
        
        return interview_scores, predicted_emotion, float(confidence)

    def analyze_with_exhubert(self, waveform):
        """使用ExHuBERT模型进行情感分析"""
        if 'exhubert' not in self.models:
            return None
        
        try:
            # 预处理
            inputs = self.feature_extractors['exhubert'](
                waveform, 
                sampling_rate=16000, 
                padding='max_length', 
                max_length=48000,
                return_tensors="pt"
            )
            
            # 推理
            with torch.no_grad():
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
                output = self.models['exhubert'](**inputs)
                probs = torch.nn.functional.softmax(output.logits, dim=-1)
            
            # ExHuBERT的6个类别
            original_emotions = ['低唤醒-负面', '低唤醒-中性', '低唤醒-正面', '高唤醒-负面', '高唤醒-中性', '高唤醒-正面']
            scores = probs.cpu().numpy()[0]
            
            # 映射到面试情感
            interview_scores, predicted_emotion, confidence = self.map_to_interview_emotions(original_emotions, scores)
            
            result = {
                'model': 'ExHuBERT',
                'emotions': interview_scores,
                'predicted_emotion': predicted_emotion,
                'confidence': float(confidence)
            }
            
            return result
            
        except Exception as e:
            print(f"ExHuBERT 分析失败: {e}")
            return None
    
    def analyze_with_hubert_large(self, waveform):
        """使用HuBERT Large模型进行情感分析"""
        if 'hubert_large' not in self.models:
            return None
        
        try:
            # 预处理
            inputs = self.feature_extractors['hubert_large'](
                waveform, 
                sampling_rate=16000, 
                padding=True, 
                return_tensors="pt"
            )
            
            # 推理
            with torch.no_grad():
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
                output = self.models['hubert_large'](**inputs)
                probs = torch.nn.functional.softmax(output.logits, dim=-1)
            
            # IEMOCAP的4个类别
            original_emotions = ['愤怒', '高兴', '中性', '悲伤']
            scores = probs.cpu().numpy()[0]
            
            # 映射到面试情感
            interview_scores, predicted_emotion, confidence = self.map_to_interview_emotions(original_emotions, scores)
            
            result = {
                'model': 'HuBERT Large',
                'emotions': interview_scores,
                'predicted_emotion': predicted_emotion,
                'confidence': float(confidence)
            }
            
            return result
            
        except Exception as e:
            print(f"HuBERT Large 分析失败: {e}")
            return None
    
    def analyze_with_wav2vec2_xlsr(self, waveform):
        """使用Wav2Vec2 XLSR模型进行情感分析"""
        if 'wav2vec2_xlsr' not in self.models:
            return None
        
        try:
            # 预处理
            inputs = self.feature_extractors['wav2vec2_xlsr'](
                waveform, 
                sampling_rate=16000, 
                return_tensors="pt"
            )
            
            # 推理
            with torch.no_grad():
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
                output = self.models['wav2vec2_xlsr'](**inputs)
                probs = torch.nn.functional.softmax(output.logits, dim=-1)
            
            # RAVDESS的8个情感类别
            original_emotions = ['愤怒', '平静', '厌恶', '恐惧', '高兴', '中性', '悲伤', '惊讶']
            scores = probs.cpu().numpy()[0]
            
            # 映射到面试情感
            interview_scores, predicted_emotion, confidence = self.map_to_interview_emotions(original_emotions, scores)
            
            result = {
                'model': 'Wav2Vec2 XLSR',
                'emotions': interview_scores,
                'predicted_emotion': predicted_emotion,
                'confidence': float(confidence)
            }
            
            return result
            
        except Exception as e:
            print(f"Wav2Vec2 XLSR 分析失败: {e}")
            return None
    
    def analyze_audio(self, audio_path):
        """
        完整的音频情感分析流程
        Args:
            audio_path: 音频文件路径
        Returns:
            dict: 包含所有模型分析结果的字典
        """
        print(f"开始分析音频文件: {audio_path}")
        
        # 预处理音频
        waveform, sr = self.preprocess_audio(audio_path)
        
        results = {
            'audio_file': audio_path,
            'sample_rate': sr,
            'duration': len(waveform) / sr,
            'models_results': []
        }
        
        # 使用所有可用模型进行分析
        model_functions = [
            self.analyze_with_exhubert,
            self.analyze_with_hubert_large,
            self.analyze_with_wav2vec2_xlsr
        ]
        
        for analyze_func in model_functions:
            result = analyze_func(waveform)
            if result:
                results['models_results'].append(result)
        
        # 生成综合分析结果
        results['summary'] = self.generate_summary(results['models_results'])
        
        return results
    
    def generate_summary(self, model_results):
        """生成综合分析摘要"""
        if not model_results:
            return {"error": "没有可用的分析结果"}
        
        # 收集所有情感预测
        predictions = [result['predicted_emotion'] for result in model_results]
        confidences = [result['confidence'] for result in model_results]
        
        # 计算平均置信度
        avg_confidence = float(np.mean(confidences))
        
        # 找出最高置信度的预测
        best_result_idx = int(np.argmax(confidences))
        best_prediction = model_results[best_result_idx]
        
        summary = {
            'recommended_emotion': best_prediction['predicted_emotion'],
            'confidence': float(best_prediction['confidence']),
            'best_model': best_prediction['model'],
            'average_confidence': avg_confidence,
            'all_predictions': predictions,
            'consensus': len(set(predictions)) == 1  # 是否所有模型预测一致
        }
        
        return summary
    
    def analyze_interview_session(self, audio_segments):
        """
        分析整个面试会话的情感变化
        Args:
            audio_segments: 音频片段列表
        Returns:
            dict: 面试情感分析报告
        """
        session_results = []
        
        for i, segment in enumerate(audio_segments):
            print(f"分析第 {i+1}/{len(audio_segments)} 个音频片段...")
            result = self.analyze_audio(segment)
            result['segment_id'] = i + 1
            session_results.append(result)
        
        # 生成面试情感报告
        report = self.generate_interview_report(session_results)
        
        return {
            'session_results': session_results,
            'interview_report': report
        }
    
    def generate_interview_report(self, session_results):
        """生成面试情感分析报告"""
        emotions = []
        confidences = []
        timestamps = []
        
        for result in session_results:
            if result['summary'].get('recommended_emotion'):
                emotions.append(result['summary']['recommended_emotion'])
                confidences.append(result['summary']['confidence'])
                timestamps.append(result['segment_id'])
        
        if not emotions:
            return {"error": "无法生成报告，没有有效的分析结果"}
        
        # 统计情感分布
        emotion_counts = pd.Series(emotions).value_counts()
        
        # 计算情感稳定性
        emotion_stability = len(set(emotions)) / len(emotions)  # 越小越稳定
        
        # 平均置信度
        avg_confidence = np.mean(confidences)
        
        # 主导情感
        dominant_emotion = emotion_counts.index[0] if len(emotion_counts) > 0 else "未知"
        
        report = {
            'dominant_emotion': dominant_emotion,
            'emotion_distribution': emotion_counts.to_dict(),
            'emotional_stability': 1 - emotion_stability,  # 转换为稳定性分数
            'average_confidence': avg_confidence,
            'total_segments': len(session_results),
            'emotion_timeline': list(zip(timestamps, emotions, confidences)),
            'recommendations': self.generate_recommendations(dominant_emotion, emotion_stability, avg_confidence)
        }
        
        return report
    
    def generate_recommendations(self, dominant_emotion, stability, confidence):
        """根据分析结果生成面试建议"""
        recommendations = []
        
        # 基于主导情感的建议
        emotion_advice = {
            '中性': "表现较为平稳，建议适当表达更多积极情感",
            '高兴': "表现出良好的积极态度，继续保持",
            '平静': "表现沉着冷静，这是面试的优势",
            '愤怒': "建议控制情绪，保持专业态度",
            '悲伤': "可能需要调整心态，展现更积极的一面",
            '恐惧': "建议放松心态，增强自信",
            '惊讶': "反应敏锐，但注意保持专业性",
            '厌恶': "建议调整态度，保持开放的心态"
        }
        
        if dominant_emotion in emotion_advice:
            recommendations.append(emotion_advice[dominant_emotion])
        
        # 基于稳定性的建议
        if stability < 0.7:
            recommendations.append("情绪变化较大，建议保持更稳定的表现")
        else:
            recommendations.append("情绪表现稳定，这是面试的加分项")
        
        # 基于置信度的建议
        if confidence < 0.6:
            recommendations.append("情感表达可能不够明确，建议更清晰地表达想法")
        
        return recommendations

if __name__ == "__main__":
    # 测试代码
    analyzer = SpeechEmotionAnalyzer()
    print("语音情感分析器初始化完成！")
    print(f"已加载 {len(analyzer.models)} 个模型") 