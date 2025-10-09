"""
Pytest fixtures and configuration
"""
import pytest
import asyncio
import os
from pathlib import Path


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_openrouter_response():
    """Mock OpenRouter API response"""
    return {
        'id': 'chatcmpl-test',
        'object': 'chat.completion',
        'created': 1234567890,
        'model': 'x-ai/grok-4-fast',
        'choices': [{
            'index': 0,
            'message': {
                'role': 'assistant',
                'content': '```json\n[{"type": "code", "description": "Test task", "priority": 1}]\n```'
            },
            'finish_reason': 'stop'
        }],
        'usage': {
            'prompt_tokens': 100,
            'completion_tokens': 50,
            'total_tokens': 150
        }
    }


@pytest.fixture
def sample_task():
    """Sample agent task"""
    return {
        'id': 'test-task-1',
        'conversation_id': 'test-conv-123',
        'type': 'code',
        'description': 'Port x86 trap handling to ARM64',
        'file_path': 'arch/x86/traps.c',
        'priority': 1
    }


@pytest.fixture
def sample_eterna_task():
    """Sample ETERNA port task"""
    return {
        'id': 'test-eterna-1',
        'conversation_id': 'test-conv-456',
        'type': 'port',
        'description': 'Port src/cpu/vcpu.rs to x86',
        'file_path': 'src/cpu/vcpu.rs',
        'target': 'code_window'
    }


@pytest.fixture
def x86_port_path(tmp_path):
    """Create temporary x86_port directory structure"""
    port_dir = tmp_path / "x86_port"
    port_dir.mkdir()
    
    # Create src directory
    src_dir = port_dir / "src"
    src_dir.mkdir()
    
    # Create Cargo.toml
    cargo_toml = port_dir / "Cargo.toml"
    cargo_toml.write_text("""
[package]
name = "hypervisor"
version = "0.1.0"
edition = "2021"

[dependencies]
""")
    
    # Create lib.rs
    lib_rs = src_dir / "lib.rs"
    lib_rs.write_text("""
#![no_std]

pub fn test_function() -> u64 {
    42
}
""")
    
    return port_dir


@pytest.fixture(autouse=True)
def set_test_env(monkeypatch):
    """Set test environment variables"""
    monkeypatch.setenv('OPENROUTER_API_KEY1', 'test-key-1')
    monkeypatch.setenv('OPENROUTER_API_KEY2', 'test-key-2')
    monkeypatch.setenv('OPENROUTER_API_KEY3', 'test-key-3')
    monkeypatch.setenv('DATABASE_URL', 'postgresql://test:test@localhost/test')
