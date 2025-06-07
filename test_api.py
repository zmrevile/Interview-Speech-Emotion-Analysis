#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
API功能测试脚本
"""

import requests
import base64
import tempfile
import numpy as np
import soundfile as sf
import time

def create_test_audio():
    """创建测试音频文件"""
    # 生成测试音频信号
    sample_rate = 16000
    duration = 3.0
    frequency = 1000
    
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    audio_signal = np.sin(2 * np.pi * frequency * t) * 0.3
    noise = np.random.normal(0, 0.05, len(audio_signal))
    audio_signal = audio_signal + noise
    
    # 保存到临时文件
    temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
    sf.write(temp_file.name, audio_signal, sample_rate)
    
    return temp_file.name

def test_health_check():
    """测试健康检查接口"""
    print("🔍 测试健康检查接口...")
    try:
        response = requests.get('http://localhost:5000/health', timeout=10)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 健康检查通过: {result['message']}")
            print(f"   模型数量: {result['data']['models_loaded']}")
            return True
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
        return False

def test_file_upload():
    """测试文件上传分析"""
    print("🔍 测试文件上传分析...")
    
    # 创建测试音频
    audio_file = create_test_audio()
    
    try:
        with open(audio_file, 'rb') as f:
            files = {'audio': f}
            response = requests.post('http://localhost:5000/analyze', files=files, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                data = result['data']
                print("✅ 文件上传分析成功")
                print(f"   情感: {data['final_result']['recommended_emotion']}")
                print(f"   置信度: {data['final_result']['confidence']:.3f}")
                print(f"   评分: {data['interview_assessment']['score']}")
                print(f"   建议: {data['interview_assessment']['recommendations']}")
                return True
            else:
                print(f"❌ 分析失败: {result['message']}")
                return False
        else:
            print(f"❌ 请求失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 文件上传测试失败: {e}")
        return False
    finally:
        # 清理临时文件
        import os
        try:
            os.unlink(audio_file)
        except:
            pass

def test_base64_analysis():
    """测试Base64数据分析"""
    print("🔍 测试Base64数据分析...")
    
    # 创建测试音频
    audio_file = create_test_audio()
    
    try:
        # 读取音频文件并编码为Base64
        with open(audio_file, 'rb') as f:
            audio_data = f.read()
        
        audio_b64 = base64.b64encode(audio_data).decode('utf-8')
        
        # 发送请求
        data = {'audio_data': audio_b64}
        response = requests.post(
            'http://localhost:5000/analyze',
            json=data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                data = result['data']
                print("✅ Base64数据分析成功")
                print(f"   情感: {data['final_result']['recommended_emotion']}")
                print(f"   置信度: {data['final_result']['confidence']:.3f}")
                print(f"   评分: {data['interview_assessment']['score']}")
                return True
            else:
                print(f"❌ 分析失败: {result['message']}")
                return False
        else:
            print(f"❌ 请求失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Base64分析测试失败: {e}")
        return False
    finally:
        # 清理临时文件
        import os
        try:
            os.unlink(audio_file)
        except:
            pass

def test_batch_analysis():
    """测试批量分析"""
    print("🔍 测试批量分析...")
    
    try:
        # 创建多个测试音频片段
        audio_segments = []
        temp_files = []
        
        for i in range(3):
            audio_file = create_test_audio()
            temp_files.append(audio_file)
            
            with open(audio_file, 'rb') as f:
                audio_data = f.read()
            audio_b64 = base64.b64encode(audio_data).decode('utf-8')
            audio_segments.append(audio_b64)
        
        # 发送批量分析请求
        data = {'audio_segments': audio_segments}
        response = requests.post(
            'http://localhost:5000/batch_analyze',
            json=data,
            headers={'Content-Type': 'application/json'},
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                data = result['data']
                print("✅ 批量分析成功")
                print(f"   处理片段: {data['overall_report']['total_segments']}")
                print(f"   平均评分: {data['overall_report']['average_score']}")
                print(f"   主导情感: {data['overall_report']['dominant_emotion']}")
                print(f"   稳定性: {data['overall_report']['stability_level']}")
                return True
            else:
                print(f"❌ 批量分析失败: {result['message']}")
                return False
        else:
            print(f"❌ 请求失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 批量分析测试失败: {e}")
        return False
    finally:
        # 清理临时文件
        import os
        for temp_file in temp_files:
            try:
                os.unlink(temp_file)
            except:
                pass

def main():
    """主测试函数"""
    print("语音情感分析API测试")
    print("=" * 50)
    
    # 等待API服务器启动
    print("⏳ 等待API服务器启动...")
    time.sleep(2)
    
    tests = [
        ("健康检查", test_health_check),
        ("文件上传分析", test_file_upload),
        ("Base64数据分析", test_base64_analysis),
        ("批量分析", test_batch_analysis)
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
        
        # 测试间隔
        time.sleep(1)
    
    print("\n" + "=" * 50)
    print(f"🎯 测试结果: {passed}/{total} 测试通过")
    
    if passed == total:
        print("所有API测试通过！")
        print("\nAPI服务器运行正常，可以集成到面试系统中")
        print("集成指南: 请查看 api_integration_guide.md")
    else:
        print("部分测试失败，请检查API服务器状态")

if __name__ == "__main__":
    main() 