#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
简化的API服务器启动脚本
"""

import os
import sys
import subprocess
import time
import threading

def check_dependencies():
    """检查依赖包"""
    print("🔍 检查依赖包...")
    
    required_packages = [
        'flask',
        'flask-cors', 
        'transformers',
        'torch',
        'librosa',
        'soundfile'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  缺少依赖包: {', '.join(missing_packages)}")
        print("请运行: pip install", ' '.join(missing_packages))
        return False
    
    print("✅ 所有依赖包已安装")
    return True

def start_api_server():
    """启动API服务器"""
    print("\n🚀 启动语音情感分析API服务器...")
    
    try:
        # 导入API模块
        from emotion_api import app, init_analyzer
        
        # 初始化分析器
        if init_analyzer():
            print("✅ 分析器初始化成功")
            
            print("\n🎤 语音情感分析API服务器")
            print("=" * 40)
            print("🌐 服务地址: http://localhost:5000")
            print("📋 可用接口:")
            print("  GET  /health - 健康检查")
            print("  POST /analyze - 单个音频分析") 
            print("  POST /batch_analyze - 批量音频分析")
            print("=" * 40)
            print("\n💡 提示:")
            print("  - 按 Ctrl+C 停止服务器")
            print("  - 在另一个终端运行 python test_api.py 测试API")
            print("  - 查看 api_integration_guide.md 了解集成方法")
            print("\n🔥 服务器启动中...")
            
            # 启动Flask服务器
            app.run(
                host='0.0.0.0',
                port=5000,
                debug=False,
                threaded=True,
                use_reloader=False
            )
        else:
            print("❌ 分析器初始化失败")
            return False
            
    except ImportError as e:
        print(f"❌ 导入模块失败: {e}")
        print("请确保 speech_emotion_analyzer.py 文件存在")
        return False
    except KeyboardInterrupt:
        print("\n\n🛑 服务器已停止")
        return True
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        return False

def run_tests():
    """在新线程中运行测试"""
    time.sleep(10)  # 等待服务器启动
    print("\n🧪 自动运行API测试...")
    
    try:
        result = subprocess.run([sys.executable, 'test_api.py'], 
                              capture_output=True, text=True, timeout=120)
        print(result.stdout)
        if result.stderr:
            print("错误信息:", result.stderr)
    except subprocess.TimeoutExpired:
        print("⏱️  测试超时")
    except Exception as e:
        print(f"⚠️  测试执行失败: {e}")

def main():
    """主函数"""
    print("🎤 语音情感分析API服务器启动器")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        input("\n按Enter键退出...")
        return
    
    # 询问是否自动运行测试
    auto_test = input("\n❓ 是否在服务器启动后自动运行测试？(y/n): ").lower().strip()
    
    if auto_test == 'y':
        # 在后台线程中运行测试
        test_thread = threading.Thread(target=run_tests, daemon=True)
        test_thread.start()
    
    # 启动服务器
    start_api_server()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 再见！")
    except Exception as e:
        print(f"\n💥 意外错误: {e}")
        input("按Enter键退出...") 