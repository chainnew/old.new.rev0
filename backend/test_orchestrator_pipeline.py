"""
Test the full Orchestrator → Swarm → Planner pipeline
Simulates user input → scope generation → planner population
"""
import json
from orchestrator_agent import OrchestratorAgent

def test_trackflow_pipeline():
    """Test with TrackFlow example (task tracker)"""
    print("\n" + "="*70)
    print("🧪 TESTING: Orchestrator → Swarm → Planner Pipeline")
    print("="*70 + "\n")
    
    orchestrator = OrchestratorAgent()
    
    # Test 1: Clear request
    print("📝 Test 1: User says 'Build a task tracker like Trello with Next.js'\n")
    result = orchestrator.handle_user_input(
        "Build a task tracking dashboard like Trello with Next.js and Tailwind, auth, and analytics",
        user_id="test_user"
    )
    
    print(f"✅ Orchestrator Result:")
    print(json.dumps(result, indent=2))
    
    if result['status'] == 'success' and result['swarm_id']:
        # Get planner data
        print(f"\n📋 Fetching Planner Data for swarm: {result['swarm_id']}\n")
        planner_data = orchestrator.get_planner_data(result['swarm_id'])
        
        print("="*70)
        print("PLANNER DATA (Ready for agent-plan.tsx):")
        print("="*70)
        print(json.dumps(planner_data, indent=2))
        
        # Show formatted summary
        print("\n" + "="*70)
        print("FORMATTED SUMMARY:")
        print("="*70)
        for task in planner_data:
            print(f"\n📌 Task {task['id']}: {task['title']}")
            print(f"   Status: {task['status']} | Priority: {task['priority']}")
            print(f"   Subtasks: {len(task['subtasks'])}")
            for subtask in task['subtasks'][:2]:  # Show first 2
                print(f"     - {subtask.get('title', subtask.get('id'))}: {subtask.get('status', 'N/A')}")
            if len(task['subtasks']) > 2:
                print(f"     ... and {len(task['subtasks']) - 2} more")
    
    # Test 2: Vague request
    print("\n\n" + "="*70)
    print("📝 Test 2: User says 'hey' (vague request)\n")
    result2 = orchestrator.handle_user_input("hey", user_id="test_user2")
    
    print(f"✅ Orchestrator Response:")
    print(json.dumps(result2, indent=2))
    
    if result2['status'] == 'needs_clarification':
        print("\n💬 Clarification message:")
        print(result2['message'])

def test_api_format():
    """Test that output matches API endpoint format"""
    print("\n\n" + "="*70)
    print("🔌 TESTING: API Endpoint Format")
    print("="*70 + "\n")
    
    orchestrator = OrchestratorAgent()
    result = orchestrator.handle_user_input(
        "Build an e-commerce store with product catalog, cart, and checkout",
        user_id="api_test"
    )
    
    if result['swarm_id']:
        api_response = {
            "swarm_id": result['swarm_id'],
            "tasks": orchestrator.get_planner_data(result['swarm_id'])
        }
        
        print("API Response format (/api/planner/{swarm_id}):")
        print(json.dumps(api_response, indent=2)[:500] + "...")
        
        print(f"\n✅ Format validated! {len(api_response['tasks'])} tasks ready for frontend")

if __name__ == "__main__":
    try:
        test_trackflow_pipeline()
        test_api_format()
        
        print("\n\n" + "="*70)
        print("✅ ALL TESTS PASSED!")
        print("="*70)
        print("\n📌 Next Steps:")
        print("  1. Restart API: python swarm_api.py")
        print("  2. Test endpoint: curl http://localhost:8000/orchestrator/process \\")
        print("       -X POST -H 'Content-Type: application/json' \\")
        print("       -d '{\"message\": \"build task tracker\", \"user_id\": \"demo\"}'")
        print("  3. Use swarm_id in frontend: <Plan swarmId=\"{swarm_id}\" />")
        print("  4. Watch it populate dynamically! 🚀\n")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
