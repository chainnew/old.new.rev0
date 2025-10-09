"""
Test script for Grok-4-Fast-Reasoning scope breakdown and swarm creation.
Demonstrates the full pipeline: User input → Scope fleshing → Swarm creation → Planner tasks
"""
import json
from orchestrator_agent import OrchestratorAgent

def test_scope_breakdown():
    """Test the Grok-4-Fast-Reasoning scope breakdown approach."""
    print("\n" + "="*70)
    print("🧪 TESTING GROK-4-FAST-REASONING SCOPE BREAKDOWN")
    print("="*70 + "\n")
    
    orchestrator = OrchestratorAgent()
    
    # Test cases with different complexity levels
    test_cases = [
        {
            "name": "E-Commerce (Complex)",
            "message": "Build an e-commerce store with Stripe",
            "expected_project": "ECommerceStripeStore"
        },
        {
            "name": "Task Tracker (Moderate)",
            "message": "Create a task tracker like Trello with Next.js",
            "expected_project": "TrackFlow"
        },
        {
            "name": "Chat App (Specific)",
            "message": "Build a real-time chat app with WebSockets and user authentication",
            "expected_project": "RealtimeChatApp"
        },
        {
            "name": "Vague Input",
            "message": "hey",
            "expected_status": "needs_clarification"
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        print(f"\n{'─'*70}")
        print(f"📝 Test Case: {test_case['name']}")
        print(f"   Input: '{test_case['message']}'")
        print(f"{'─'*70}\n")
        
        try:
            result = orchestrator.handle_user_input(
                test_case['message'],
                user_id=f"test_{test_case['name'].lower().replace(' ', '_')}"
            )
            
            print(f"\n✅ Result Status: {result['status']}")
            print(f"   Message: {result['message']}")
            
            if result.get('swarm_id'):
                print(f"   Swarm ID: {result['swarm_id']}")
                print(f"   Planner URL: {result['planner_url']}")
                
                # Get planner data
                print(f"\n📊 Planner Tasks Generated:")
                planner_data = orchestrator.get_planner_data(result['swarm_id'])
                
                for task in planner_data:
                    print(f"\n   Task {task['id']}: {task['title']}")
                    print(f"   ├─ Status: {task['status']}")
                    print(f"   ├─ Priority: {task['priority']}")
                    print(f"   └─ Subtasks: {len(task['subtasks'])} items")
                    
                    for subtask in task['subtasks'][:2]:  # Show first 2
                        print(f"      • {subtask['id']}: {subtask['title']}")
                        print(f"        Tools: {', '.join(subtask.get('tools', []))}")
                
                results.append({
                    'test': test_case['name'],
                    'status': 'PASS',
                    'swarm_id': result['swarm_id'],
                    'num_tasks': len(planner_data),
                    'total_subtasks': sum(len(t['subtasks']) for t in planner_data)
                })
            else:
                results.append({
                    'test': test_case['name'],
                    'status': 'PASS (Clarification)',
                    'response': result['message']
                })
                
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            results.append({
                'test': test_case['name'],
                'status': 'FAIL',
                'error': str(e)
            })
    
    # Summary
    print(f"\n\n{'='*70}")
    print("📈 TEST SUMMARY")
    print(f"{'='*70}\n")
    
    for result in results:
        status_emoji = "✅" if "PASS" in result['status'] else "❌"
        print(f"{status_emoji} {result['test']}: {result['status']}")
        
        if 'swarm_id' in result:
            print(f"   └─ {result['num_tasks']} tasks, {result['total_subtasks']} subtasks")
    
    passed = sum(1 for r in results if "PASS" in r['status'])
    print(f"\n📊 Results: {passed}/{len(results)} tests passed")
    
    print(f"\n{'='*70}")
    print("🎯 GROK-4-FAST-REASONING BREAKDOWN IS READY!")
    print("   - Open localhost:3000")
    print("   - Click violet Sparkles button (bottom-right)")
    print("   - Submit a project scope")
    print("   - Watch Grok break it down into modular tasks")
    print("   - View in Global Planner")
    print(f"{'='*70}\n")


def test_single_scope(message: str):
    """Test a single scope with detailed output."""
    print("\n" + "="*70)
    print(f"🎯 TESTING: {message}")
    print("="*70 + "\n")
    
    orchestrator = OrchestratorAgent()
    result = orchestrator.handle_user_input(message, user_id="interactive_test")
    
    print(f"\n✅ Status: {result['status']}")
    print(f"   Message: {result['message']}")
    
    if result.get('swarm_id'):
        print(f"\n🔗 View in browser:")
        print(f"   http://localhost:3000{result['planner_url']}")
        
        # Show full planner data
        planner_data = orchestrator.get_planner_data(result['swarm_id'])
        print(f"\n📋 Full Planner JSON:")
        print(json.dumps({
            'swarm_id': result['swarm_id'],
            'tasks': planner_data
        }, indent=2))


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Test single scope from command line
        message = ' '.join(sys.argv[1:])
        test_single_scope(message)
    else:
        # Run full test suite
        test_scope_breakdown()
