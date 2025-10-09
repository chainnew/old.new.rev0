"""
Test suite for agent functionality
"""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.primary_agent import PrimaryAgent
from agents.code_agent import CodeAgent
from agents.eterna_port_agent import EternaPortAgent


class TestPrimaryAgent:
    """Test PrimaryAgent functionality"""
    
    @pytest.mark.asyncio
    async def test_decompose_simple_task(self, mock_openrouter_response):
        """Test task decomposition"""
        agent = PrimaryAgent()
        
        # Mock the client response
        agent.client.chat_completion = AsyncMock(return_value=MagicMock(
            choices=[MagicMock(
                message=MagicMock(
                    content='```json\n[{"type": "code", "description": "Port traps.c", "priority": 1}]\n```'
                )
            )]
        ))
        
        result = await agent.decompose("Port x86 trap handling", "test-conv-1")
        
        assert isinstance(result, list)
        assert len(result) > 0
        assert result[0]['type'] == 'code'
        assert 'id' in result[0]
        assert 'conversation_id' in result[0]
    
    @pytest.mark.asyncio
    async def test_decompose_fallback(self):
        """Test fallback when decomposition fails"""
        agent = PrimaryAgent()
        
        # Mock client to raise error
        agent.client.chat_completion = AsyncMock(side_effect=Exception("API error"))
        
        result = await agent.decompose("Test task", "test-conv-2")
        
        # Should return fallback single task
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]['type'] == 'code'
    
    @pytest.mark.asyncio
    async def test_integrate_results(self):
        """Test result integration"""
        agent = PrimaryAgent()
        
        # Mock client response
        agent.client.chat_completion = AsyncMock(return_value=MagicMock(
            choices=[MagicMock(
                message=MagicMock(content='Successfully completed all tasks.')
            )]
        ))
        
        results = [
            {'status': 'completed', 'output': {'summary': 'Task 1 done'}},
            {'status': 'completed', 'output': {'summary': 'Task 2 done'}}
        ]
        
        summary = await agent.integrate(results, "test-conv-3")
        
        assert isinstance(summary, str)
        assert len(summary) > 0
    
    def test_parse_tasks_json(self):
        """Test JSON parsing from various formats"""
        agent = PrimaryAgent()
        
        # Test with markdown code block
        content1 = '```json\n[{"type": "code"}]\n```'
        result1 = agent._parse_tasks(content1)
        assert len(result1) == 1
        assert result1[0]['type'] == 'code'
        
        # Test with plain JSON
        content2 = '[{"type": "debug"}]'
        result2 = agent._parse_tasks(content2)
        assert len(result2) == 1
        assert result2[0]['type'] == 'debug'


class TestCodeAgent:
    """Test CodeAgent functionality"""
    
    @pytest.mark.asyncio
    async def test_execute_code_task(self, sample_task):
        """Test code agent execution"""
        agent = CodeAgent()
        
        # Mock client
        agent.client.chat_completion = AsyncMock(return_value=MagicMock(
            choices=[MagicMock(
                message=MagicMock(content='''
--- a/arch/x86/traps.c
+++ b/arch/arm64/traps.c
@@ -10,5 +10,5 @@
-    // x86 code
+    // ARM64 code
''')
            )]
        ))
        
        # Mock DB methods
        agent._get_rag_context = AsyncMock(return_value="No context")
        agent._store_artifact = AsyncMock()
        
        result = await agent.execute(sample_task)
        
        assert result['task_id'] == sample_task['id']
        assert result['status'] == 'completed'
        assert 'diff' in result['output']
    
    @pytest.mark.asyncio
    async def test_execute_handles_errors(self, sample_task):
        """Test error handling"""
        agent = CodeAgent()
        
        # Mock client to raise error
        agent.client.chat_completion = AsyncMock(side_effect=Exception("API timeout"))
        agent._get_rag_context = AsyncMock(return_value="")
        
        result = await agent.execute(sample_task)
        
        assert result['status'] == 'failed'
        assert 'error' in result['output']
    
    def test_extract_summary(self):
        """Test summary extraction from diff"""
        agent = CodeAgent()
        
        diff = """
Port x86 traps to ARM64
Key changes: Replace INT handlers with exception vectors
---
diff --git a/traps.c b/traps.c
"""
        summary = agent._extract_summary(diff)
        
        assert isinstance(summary, str)
        assert len(summary) > 0


class TestEternaPortAgent:
    """Test EternaPortAgent functionality"""
    
    @pytest.mark.asyncio
    async def test_execute_port_task(self, sample_eterna_task, tmp_path):
        """Test ETERNA port execution"""
        agent = EternaPortAgent()
        
        # Create temporary ARM source file
        arm_file = tmp_path / "vcpu.rs"
        arm_file.write_text("""
pub struct Vcpu {
    // ARM64 VCPU state
}
""")
        
        # Override path
        agent.eterna_path = str(tmp_path)
        
        # Mock client
        agent.client.chat_completion = AsyncMock(return_value=MagicMock(
            choices=[MagicMock(
                message=MagicMock(content='''
Architecture Analysis:
ARM64 EL2 maps to x86 VMX root mode.

```rust
pub struct Vcpu {
    // x86 VCPU state with VMCS
}
```
''')
            )]
        ))
        
        sample_eterna_task['file_path'] = 'vcpu.rs'
        result = await agent.execute(sample_eterna_task)
        
        assert result['status'] == 'completed'
        assert 'code' in result['output']
        assert 'analysis' in result['output']
    
    def test_needs_complex_planning(self):
        """Test planning detection"""
        agent = EternaPortAgent()
        
        # Small file
        small_code = "\n".join(["// line"] * 100)
        assert not agent._needs_complex_planning("Simple port", small_code)
        
        # Large file
        large_code = "\n".join(["// line"] * 1000)
        assert agent._needs_complex_planning("Port VCPU", large_code)
        
        # Complex keywords
        assert agent._needs_complex_planning("Port exception handling", small_code)
        assert agent._needs_complex_planning("Port GIC interrupts", small_code)
    
    def test_parse_output(self):
        """Test output parsing"""
        agent = EternaPortAgent()
        
        output = """
Analysis: ARM to x86 mapping

```rust
pub fn test() {}
```

Plan:
1. Port structures
2. Port functions
3. Test
"""
        code, analysis, plan = agent._parse_output(output, needs_planning=True)
        
        assert 'pub fn test()' in code
        assert 'Analysis' in analysis
        assert len(plan) > 0


class TestSwarmCoordination:
    """Test swarm coordination"""
    
    @pytest.mark.asyncio
    async def test_coordinator_registration(self):
        """Test agent registration"""
        from agents.swarm_coordinator import SwarmCoordinator
        
        coordinator = SwarmCoordinator()
        queue = coordinator.register_agent('test_agent')
        
        assert 'test_agent' in coordinator.queues
        assert 'test_agent' in coordinator.agent_health
        assert queue is not None
    
    @pytest.mark.asyncio
    async def test_message_passing(self):
        """Test message sending"""
        from agents.swarm_coordinator import SwarmCoordinator, AgentMessage
        
        coordinator = SwarmCoordinator()
        coordinator.register_agent('agent1')
        coordinator.register_agent('agent2')
        
        message = AgentMessage(
            from_agent='agent1',
            to_agent='agent2',
            message_type='task',
            payload={'data': 'test'}
        )
        
        await coordinator.send_message(message)
        
        # Check message in queue
        assert not coordinator.queues['agent2'].empty()
        received = await coordinator.queues['agent2'].get()
        assert received.from_agent == 'agent1'
        assert received.payload['data'] == 'test'
    
    @pytest.mark.asyncio
    async def test_handshake(self):
        """Test agent handshake"""
        from agents.swarm_coordinator import SwarmCoordinator
        
        coordinator = SwarmCoordinator()
        coordinator.register_agent('agent1')
        coordinator.register_agent('agent2')
        
        capabilities = {'model': 'grok-4-fast', 'specialization': 'code'}
        result = await coordinator.handshake('agent1', capabilities)
        
        assert result is True
        # Agent2 should have received handshake message
        assert not coordinator.queues['agent2'].empty()


@pytest.mark.asyncio
async def test_full_orchestration_flow(sample_task, x86_port_path):
    """Integration test for full orchestration"""
    from hypervisor_port_orchestrator import HypervisorPortOrchestrator
    
    orchestrator = HypervisorPortOrchestrator(str(x86_port_path))
    
    # Mock all agent methods
    orchestrator.primary.decompose = AsyncMock(return_value=[sample_task])
    orchestrator.primary.integrate = AsyncMock(return_value="All tasks completed")
    
    orchestrator.code_agent.execute = AsyncMock(return_value={
        'task_id': sample_task['id'],
        'status': 'completed',
        'file_path': 'src/test.rs',
        'output': {
            'code': 'pub fn test() {}',
            'summary': 'Generated test code'
        }
    })
    
    # Mock cargo check
    orchestrator._run_cargo_check = AsyncMock(return_value={
        'success': True,
        'returncode': 0,
        'stdout': 'Checking hypervisor...',
        'stderr': ''
    })
    
    result = await orchestrator.port_hypervisor(
        task_description="Test port",
        conversation_id="test-123",
        validate_rust=True,
        build=False
    )
    
    assert result['status'] == 'completed'
    assert len(result['subtasks']) > 0
    assert 'validation' in result


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
