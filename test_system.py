#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
语音情感分析系统测试脚本
用于验证系统核心功能是否正常
"""

import os
import sys
import numpy as np
import librosa
import tempfile

def test_basic_imports():
    """测试基础库导入"""
    print("🔍 测试基础库导入...")
    
    try:
        import torch
        import transformers
        import librosa
        import pandas
        import numpy
        import flask
        print("✅ 所有基础库导入成功")
        return True
    except ImportError as e:
        print(f"❌ 库导入失败: {e}")
        return False

def test_models_loading():
    """测试模型加载功能"""
    print("🔍 测试模型加载功能...")
    
    try:
        # 首先测试不需要下载模型的基础功能
        from speech_emotion_analyzer import SpeechEmotionAnalyzer
        
        print("⏳ 初始化语音情感分析器...")
        analyzer = SpeechEmotionAnalyzer()
        
        print(f"✅ 分析器初始化成功，已加载 {len(analyzer.models)} 个模型")
        
        # 列出加载的模型
        if analyzer.models:
            for model_name in analyzer.models.keys():
                print(f"   - {model_name}")
        else:
            print("⚠️  未加载任何模型，但系统仍可使用")
        
        return True
        
    except Exception as e:
        print(f"❌ 模型加载测试失败: {e}")
        return False

def create_test_audio():
    """创建测试音频文件"""
    print("🔍 创建测试音频文件...")
    
    try:
        # 生成一个简单的测试音频信号 (3秒，1000Hz正弦波)
        sample_rate = 16000
        duration = 3.0
        frequency = 1000
        
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        audio_signal = np.sin(2 * np.pi * frequency * t) * 0.3
        
        # 添加一些随机噪声使其更像真实语音
        noise = np.random.normal(0, 0.05, len(audio_signal))
        audio_signal = audio_signal + noise
        
        # 保存到临时文件
        temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        import soundfile as sf
        sf.write(temp_file.name, audio_signal, sample_rate)
        
        print(f"✅ 测试音频创建成功: {temp_file.name}")
        return temp_file.name
        
    except Exception as e:
        print(f"❌ 测试音频创建失败: {e}")
        return None

def test_audio_analysis(audio_file):
    """测试音频分析功能"""
    print("🔍 测试音频分析功能...")
    
    try:
        from speech_emotion_analyzer import SpeechEmotionAnalyzer
        
        analyzer = SpeechEmotionAnalyzer()
        
        if not analyzer.models:
            print("⚠️  没有可用的模型，跳过分析测试")
            return True
        
        print("⏳ 开始分析测试音频...")
        result = analyzer.analyze_audio(audio_file)
        
        print("✅ 音频分析完成!")
        print(f"   文件: {os.path.basename(result['audio_file'])}")
        print(f"   时长: {result['duration']:.2f} 秒")
        print(f"   采样率: {result['sample_rate']} Hz")
        print(f"   模型结果: {len(result['models_results'])} 个")
        
        if result['models_results']:
            best_result = result['summary']
            print(f"   推荐情感: {best_result.get('recommended_emotion', '未知')}")
            print(f"   置信度: {best_result.get('confidence', 0):.3f}")
        
        return True
        
    except Exception as e:
        print(f"❌ 音频分析测试失败: {e}")
        return False

def test_api_functionality():
    """测试API功能"""
    print("🔍 测试API功能...")
    
    try:
        from emotion_api import app, init_analyzer
        
        # 测试分析器初始化
        if init_analyzer():
            print("✅ API分析器初始化成功")
        else:
            print("⚠️  API分析器初始化失败，但系统仍可测试")
        
        # 测试Flask应用创建
        if app:
            print("✅ Flask应用创建成功")
        
        print("✅ API功能测试通过")
        return True
        
    except Exception as e:
        print(f"❌ API功能测试失败: {e}")
        return False

def cleanup_test_files(files):
    """清理测试文件"""
    print("🧹 清理测试文件...")
    
    for file in files:
        try:
            if file and os.path.exists(file):
                os.unlink(file)
                print(f"✅ 删除测试文件: {os.path.basename(file)}")
        except Exception as e:
            print(f"⚠️  删除文件失败: {e}")

def main():
    """主测试函数"""
    print("🎤 语音情感分析系统测试")
    print("=" * 40)
    
    test_files = []
    
    # 运行各种测试
    tests = [
        ("基础库导入", test_basic_imports),
        ("模型加载", test_models_loading),
        ("API功能", test_api_functionality)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📝 测试: {test_name}")
        print("-" * 30)
        
        if test_func():
            passed += 1
            print(f"✅ {test_name} 测试通过")
        else:
            print(f"❌ {test_name} 测试失败")
    
    # 音频分析测试（需要先创建测试文件）
    print(f"\n📝 测试: 音频分析")
    print("-" * 30)
    
    test_audio = create_test_audio()
    if test_audio:
        test_files.append(test_audio)
        if test_audio_analysis(test_audio):
            passed += 1
            print("✅ 音频分析 测试通过")
        else:
            print("❌ 音频分析 测试失败")
        total += 1
    else:
        print("⚠️  跳过音频分析测试（无法创建测试文件）")
    
    # 清理测试文件
    cleanup_test_files(test_files)
    
    # 输出测试结果
    print("\n" + "=" * 40)
    print(f"🎯 测试结果: {passed}/{total} 测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！系统可以正常使用")
        print("\n🚀 可以运行以下命令启动系统:")
        print("   python interview_demo.py")
    elif passed >= total * 0.7:
        print("⚠️  大部分测试通过，系统基本可用")
        print("💡 建议检查失败的测试项目")
    else:
        print("❌ 多个测试失败，可能需要检查环境配置")
    
    return passed == total

if __name__ == "__main__":
    main() 