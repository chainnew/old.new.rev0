"""
Test MCP Integration with Orchestrator and Swarm Pipeline
Simulates: User input → Orchestrator → Swarm with MCP tools → Planner updates
"""
import json
import time
import requests
from orchestrator_agent import OrchestratorAgent

def test_mcp_server_health():
    """Test 1: MCP server is running and accessible."""
    print("\n" + "="*70)
    print("🧪 TEST 1: MCP Server Health Check")
    print("="*70)
    
    try:
        response = requests.get("http://localhost:8001/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ MCP Server is running")
            print(f"   Service: {data['service']}")
            print(f"   Tools: {', '.join(data['tools'])}")
            return True
        else:
            print(f"❌ MCP Server returned {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ MCP Server not accessible: {e}")
        print("   Start it with: python mcp_servers.py")
        return False

def test_tool_schemas():
    """Test 2: Tool schemas are properly formatted."""
    print("\n" + "="*70)
    print("🧪 TEST 2: Tool Schemas")
    print("="*70)
    
    try:
        response = requests.get("http://localhost:8001/tools/schemas", timeout=5)
        if response.status_code == 200:
            schemas = response.json()
            tools = schemas['tools']
            print(f"✅ Found {len(tools)} tool schemas:")
            for tool in tools:
                func = tool['function']
                print(f"   - {func['name']}: {func['description'][:60]}...")
            return tools
        else:
            print(f"❌ Failed to get schemas: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def test_browser_tool():
    """Test 3: Browser tool for web research."""
    print("\n" + "="*70)
    print("🧪 TEST 3: Browser Tool (Web Research)")
    print("="*70)
    
    payload = {
        "tool_name": "browser",
        "args": {
            "query": "task tracking SaaS competitors like Trello",
            "num_results": 3
        },
        "swarm_id": "test-swarm-123",
        "agent_id": "test-agent-research"
    }
    
    try:
        response = requests.post(
            "http://localhost:8001/tools/browser",
            json=payload,
            headers={"Authorization": "Bearer mcp-secret-key"},
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print(f"✅ Browser tool executed successfully")
                output = result['output']
                print(f"   Query: {output.get('query')}")
                print(f"   Results found: {output.get('count', 0)}")
                for idx, res in enumerate(output.get('results', [])[:2], 1):
                    print(f"   {idx}. {res.get('text', '')[:80]}...")
                return result
            else:
                print(f"❌ Tool failed: {result.get('error')}")
                return None
        else:
            print(f"❌ HTTP {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_code_gen_tool():
    """Test 4: Code generation tool."""
    print("\n" + "="*70)
    print("🧪 TEST 4: Code Generation Tool")
    print("="*70)
    
    payload = {
        "tool_name": "code-gen",
        "args": {
            "framework": "Next.js",
            "component": "task card",
            "scope_data": {
                "features": ["drag and drop", "priority levels", "due dates"],
                "styling": "Tailwind CSS + Shadcn"
            }
        },
        "swarm_id": "test-swarm-123",
        "agent_id": "test-agent-implementation"
    }
    
    try:
        response = requests.post(
            "http://localhost:8001/tools/code-gen",
            json=payload,
            headers={"Authorization": "Bearer mcp-secret-key"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print(f"✅ Code generation successful")
                code = result['output'].get('code', '')
                print(f"   Generated {len(code)} characters of code")
                print(f"   Preview:")
                print("   " + "-"*66)
                for line in code.split('\n')[:10]:
                    print(f"   {line}")
                if len(code.split('\n')) > 10:
                    print(f"   ... and {len(code.split('\n')) - 10} more lines")
                print("   " + "-"*66)
                return result
            else:
                print(f"❌ Tool failed: {result.get('error')}")
                return None
        else:
            print(f"❌ HTTP {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_orchestrator_with_mcp():
    """Test 5: Full Orchestrator → MCP → Planner pipeline."""
    print("\n" + "="*70)
    print("🧪 TEST 5: Orchestrator with MCP Tools")
    print("="*70)
    
    try:
        orchestrator = OrchestratorAgent()
        
        # User input
        user_message = "Build a task tracking dashboard like Trello with Next.js and authentication"
        print(f"\n📝 User input: '{user_message}'")
        
        # Process with orchestrator
        result = orchestrator.handle_user_input(user_message, user_id="test_user")
        
        print(f"\n📊 Orchestrator result:")
        print(json.dumps(result, indent=2))
        
        if result['status'] == 'success' and result['swarm_id']:
            swarm_id = result['swarm_id']
            
            # Test MCP tool call through orchestrator
            print(f"\n🔧 Testing MCP tool call for swarm {swarm_id}...")
            
            # Call browser tool
            browser_result = orchestrator.call_mcp_tool(
                tool_name="browser",
                args={"query": "Trello alternatives task management", "num_results": 3},
                swarm_id=swarm_id,
                agent_id="agent-research-test"
            )
            
            if browser_result['success']:
                print(f"   ✅ Browser tool call successful")
                print(f"   Results: {browser_result['output'].get('count', 0)} items found")
            else:
                print(f"   ⚠️ Browser tool call failed: {browser_result.get('error')}")
            
            # Get planner data
            print(f"\n📋 Fetching planner data...")
            planner_data = orchestrator.get_planner_data(swarm_id)
            print(f"   Tasks: {len(planner_data)}")
            for task in planner_data:
                print(f"   - {task['title']}: {len(task['subtasks'])} subtasks")
            
            return True
        else:
            print(f"⚠️ Orchestrator returned: {result['status']}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_db_sync_tool():
    """Test 6: Database sync tool."""
    print("\n" + "="*70)
    print("🧪 TEST 6: Database Sync Tool")
    print("="*70)
    
    payload = {
        "tool_name": "db-sync",
        "args": {
            "operation": "get_progress",
            "data": {},
            "swarm_id": "test-swarm-123"
        },
        "swarm_id": "test-swarm-123",
        "agent_id": "test-agent"
    }
    
    try:
        response = requests.post(
            "http://localhost:8001/tools/db-sync",
            json=payload,
            headers={"Authorization": "Bearer mcp-secret-key"},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print(f"✅ DB sync successful")
                print(f"   Output: {result['output']}")
                return result
            else:
                print(f"❌ Tool failed: {result.get('error')}")
                return None
        else:
            print(f"❌ HTTP {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    """Run all MCP integration tests."""
    print("\n" + "="*70)
    print("🚀 MCP INTEGRATION TEST SUITE")
    print("="*70)
    print("\nTesting: Orchestrator → MCP Tools → Swarm → Planner Pipeline")
    print("="*70)
    
    results = {
        "mcp_health": False,
        "tool_schemas": False,
        "browser_tool": False,
        "code_gen_tool": False,
        "db_sync_tool": False,
        "full_pipeline": False
    }
    
    # Test 1: MCP server health
    results["mcp_health"] = test_mcp_server_health()
    if not results["mcp_health"]:
        print("\n⚠️ MCP server is not running. Start it with:")
        print("   python mcp_servers.py")
        print("\nSkipping remaining tests...")
        return
    
    time.sleep(1)
    
    # Test 2: Tool schemas
    schemas = test_tool_schemas()
    results["tool_schemas"] = len(schemas) > 0
    
    time.sleep(1)
    
    # Test 3: Browser tool
    results["browser_tool"] = test_browser_tool() is not None
    
    time.sleep(1)
    
    # Test 4: Code generation (requires OpenRouter API key)
    print("\n⚠️ Note: Code generation requires OPENROUTER_API_KEY in .env")
    try:
        results["code_gen_tool"] = test_code_gen_tool() is not None
    except:
        print("   Skipping code-gen test (API key not configured)")
        results["code_gen_tool"] = None
    
    time.sleep(1)
    
    # Test 5: DB sync
    results["db_sync_tool"] = test_db_sync_tool() is not None
    
    time.sleep(1)
    
    # Test 6: Full pipeline
    print("\n⚠️ Note: Full pipeline requires both Swarm API and MCP servers")
    try:
        results["full_pipeline"] = test_orchestrator_with_mcp()
    except:
        print("   Skipping full pipeline test")
        results["full_pipeline"] = None
    
    # Summary
    print("\n\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    
    total = 0
    passed = 0
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL" if result is False else "⏭️  SKIP"
        print(f"{status:12} {test_name.replace('_', ' ').title()}")
        if result is not None:
            total += 1
            if result:
                passed += 1
    
    print("="*70)
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("\n📌 Next Steps:")
        print("  1. MCP servers are ready for production")
        print("  2. Use in swarm agents with tool calls")
        print("  3. Frontend can trigger tools via /api/mcp/* endpoints")
        print("  4. Agent planner will show tool badges and results")
    else:
        print("\n⚠️ Some tests failed. Check the errors above.")
    
    print("\n")

if __name__ == "__main__":
    main()
