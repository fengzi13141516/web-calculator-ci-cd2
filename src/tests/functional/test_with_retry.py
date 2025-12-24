import requests
import time
import sys

def wait_for_app(timeout=60):
    """等待应用启动"""
    print("等待应用启动...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            response = requests.get("http://localhost:5000/health", timeout=2)
            if response.status_code == 200:
                print(f"应用已启动！耗时: {time.time() - start_time:.2f}秒")
                return True
        except requests.exceptions.RequestException:
            # 应用还未启动，继续等待
            time.sleep(2)
            print(".", end="", flush=True)
    
    print(f"\n等待超时（{timeout}秒），应用未启动")
    return False

def run_tests():
    """运行所有功能测试"""
    print("开始功能测试...")
    
    # 定义要测试的端点
    test_cases = [
        ("/", "首页", lambda data: "message" in data),
        ("/health", "健康检查", lambda data: data.get("status") == "healthy"),
        ("/add/10&5", "加法", lambda data: data.get("result") == 15.0),
        ("/subtract/10&5", "减法", lambda data: data.get("result") == 5.0),
        ("/multiply/10&5", "乘法", lambda data: data.get("result") == 50.0),
        ("/divide/10&5", "除法", lambda data: data.get("result") == 2.0),
        ("/add/3.5&2.1", "小数加法", lambda data: abs(data.get("result") - 5.6) < 0.0001),
        ("/divide/10&0", "除以零", lambda data: "error" in data and data.get("error") == "Division by zero"),
    ]
    
    passed = 0
    failed = 0
    
    for endpoint, description, validator in test_cases:
        print(f"\n测试: {description} ({endpoint})")
        
        try:
            response = requests.get(f"http://localhost:5000{endpoint}", timeout=5)
            
            if response.status_code == 400 and "error" in response.json():
                # 这是预期的错误情况（如除以零）
                print(f"  状态码: {response.status_code}")
                print(f"  响应: {response.json()}")
                
                if validator(response.json()):
                    print(f"  ✓ 通过（预期错误）")
                    passed += 1
                else:
                    print(f"  ✗ 失败：响应不符合预期")
                    failed += 1
                    
            elif response.status_code == 200:
                data = response.json()
                print(f"  状态码: {response.status_code}")
                print(f"  响应: {data}")
                
                if validator(data):
                    print(f"  ✓ 通过")
                    passed += 1
                else:
                    print(f"  ✗ 失败：验证未通过")
                    failed += 1
            else:
                print(f"  ✗ 失败：状态码 {response.status_code}")
                failed += 1
                
        except requests.exceptions.RequestException as e:
            print(f"  ✗ 失败：请求异常 - {e}")
            failed += 1
        except Exception as e:
            print(f"  ✗ 失败：其他异常 - {e}")
            failed += 1
    
    # 显示测试结果
    print("\n" + "="*50)
    print(f"测试结果：")
    print(f"  通过: {passed}")
    print(f"  失败: {failed}")
    print(f"  总计: {passed + failed}")
    print("="*50)
    
    return failed == 0

def main():
    """主函数"""
    print("="*50)
    print("Web计算器功能测试")
    print("="*50)
    
    # 等待应用启动
    if not wait_for_app():
        print("无法连接到应用程序，请确保应用已启动：")
        print("1. 打开另一个终端窗口")
        print("2. 进入项目目录：cd C:\\Users\\kong\\Desktop\\web-calculator-ci-cd2\\src")
        print("3. 运行：python app.py")
        sys.exit(1)
    
    # 运行测试
    success = run_tests()
    
    if success:
        print("\n🎉 所有测试通过！")
        sys.exit(0)
    else:
        print("\n❌ 部分测试失败")
        sys.exit(1)

if __name__ == "__main__":
    main()