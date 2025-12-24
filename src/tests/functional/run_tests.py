import requests
import time
import sys

def test_application():
    """测试应用程序是否正常运行"""
    
    print("=" * 60)
    print("Web计算器功能测试")
    print("=" * 60)
    
    # 等待应用启动
    print("\n1. 等待应用程序启动...")
    max_wait = 30  # 最大等待30秒
    start_time = time.time()
    
    for i in range(max_wait // 2):
        try:
            response = requests.get("http://localhost:5000/health", timeout=2)
            if response.status_code == 200:
                elapsed = time.time() - start_time
                print(f"   应用程序在 {elapsed:.1f} 秒后启动成功")
                break
        except requests.exceptions.RequestException:
            time.sleep(2)
            if (i + 1) % 5 == 0:
                print(f"   等待中... 已等待 {(i+1)*2} 秒")
    else:
        print("   错误: 应用程序启动超时")
        return False
    
    # 测试端点
    test_cases = [
        ("/", "首页", {"expected_status": 200}),
        ("/health", "健康检查", {"expected_status": 200}),
        ("/add/10&5", "加法", {"expected_status": 200, "expected_key": "result", "expected_value": 15.0}),
        ("/subtract/10&5", "减法", {"expected_status": 200, "expected_key": "result", "expected_value": 5.0}),
        ("/multiply/10&5", "乘法", {"expected_status": 200, "expected_key": "result", "expected_value": 50.0}),
        ("/divide/10&5", "除法", {"expected_status": 200, "expected_key": "result", "expected_value": 2.0}),
    ]
    
    passed = 0
    failed = 0
    
    print("\n2. 运行功能测试:")
    
    for endpoint, description, expected in test_cases:
        print(f"\n  测试: {description}")
        print(f"    端点: {endpoint}")
        
        try:
            response = requests.get(f"http://localhost:5000{endpoint}", timeout=5)
            
            if response.status_code == expected["expected_status"]:
                if response.status_code == 200:
                    data = response.json()
                    
                    # 检查是否有特定键值
                    if "expected_key" in expected:
                        if expected["expected_key"] in data:
                            actual_value = data[expected["expected_key"]]
                            if actual_value == expected["expected_value"]:
                                print(f"    ✓ 通过: {expected['expected_key']} = {actual_value}")
                                passed += 1
                            else:
                                print(f"    ✗ 失败: 期望 {expected['expected_key']}={expected['expected_value']}, 实际={actual_value}")
                                failed += 1
                        else:
                            print(f"    ✓ 通过: 状态码 {response.status_code}")
                            passed += 1
                    else:
                        print(f"    ✓ 通过: 状态码 {response.status_code}")
                        passed += 1
                else:
                    print(f"    ✓ 通过: 状态码 {response.status_code} (预期错误)")
                    passed += 1
            else:
                print(f"    ✗ 失败: 状态码 {response.status_code} (期望 {expected['expected_status']})")
                failed += 1
                
        except requests.exceptions.RequestException as e:
            print(f"    ✗ 失败: 请求异常 - {e}")
            failed += 1
        except ValueError as e:
            print(f"    ✗ 失败: JSON解析错误 - {e}")
            failed += 1
    
    # 显示结果
    print("\n" + "=" * 60)
    print("测试总结:")
    print(f"  通过: {passed}")
    print(f"  失败: {failed}")
    print(f"  总计: {passed + failed}")
    print("=" * 60)
    
    if failed == 0:
        print("\n🎉 所有测试通过！")
        return True
    else:
        print("\n❌ 部分测试失败")
        return False

if __name__ == "__main__":
    if test_application():
        sys.exit(0)
    else:
        sys.exit(1)