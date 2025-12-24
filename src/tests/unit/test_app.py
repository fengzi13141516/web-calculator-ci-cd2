import sys
import os

# 将项目根目录添加到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)  # tests目录的父目录是src
project_root = os.path.dirname(src_dir)  # src的父目录是项目根目录

sys.path.insert(0, project_root)

from src.app import app
import pytest

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index(client):
    """测试首页"""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Web Calculator API" in response.data

def test_health(client):
    """测试健康检查"""
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json['status'] == 'healthy'

def test_add(client):
    """测试加法"""
    response = client.get('/add/5&3')
    assert response.status_code == 200
    assert response.json['result'] == 8.0
    assert response.json['operation'] == 'add'

def test_subtract(client):
    """测试减法"""
    response = client.get('/subtract/10&4')
    assert response.status_code == 200
    assert response.json['result'] == 6.0

def test_multiply(client):
    """测试乘法"""
    response = client.get('/multiply/6&7')
    assert response.status_code == 200
    assert response.json['result'] == 42.0

def test_divide(client):
    """测试除法"""
    response = client.get('/divide/20&4')
    assert response.status_code == 200
    assert response.json['result'] == 5.0

def test_divide_by_zero(client):
    """测试除以零"""
    response = client.get('/divide/10&0')
    assert response.status_code == 400
    assert 'error' in response.json

def test_invalid_input(client):
    """测试无效输入"""
    response = client.get('/add/abc&xyz')
    assert response.status_code == 400