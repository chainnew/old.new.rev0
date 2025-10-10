"""
Test script for Phase 2A: Stack Inference Integration

Verifies that orchestrator_agent.py correctly integrates with stack_inferencer.py
and enriches scopes with inferred technology stacks.

Run: python test_stack_integration.py
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from orchestrator_agent import OrchestratorAgent

def test_stack_inference_integration():
    """Test that stack inference is called and enriches scopes."""
    print("🧪 Testing Phase 2A: Stack Inference Integration\n")
    print("="*60)

    # Initialize orchestrator
    orchestrator = OrchestratorAgent()

    # Test scopes with expected stack inferences
    test_cases = [
        {
            "message": "Build a task management app with Python backend and modern UI",
            "expected_backend": "Python/FastAPI",
            "expected_confidence_min": 0.7
        },
        {
            "message": "Create an e-commerce store with Next.js and Stripe integration",
            "expected_backend": "Next.js",  # or Node
            "expected_confidence_min": 0.6
        },
        {
            "message": "Build a real-time chat application with authentication",
            "expected_backend": "Node",  # or FastAPI
            "expected_confidence_min": 0.5
        }
    ]

    results = []

    for i, test in enumerate(test_cases, 1):
        print(f"\n[Test {i}/{len(test_cases)}]")
        print(f"Message: \"{test['message']}\"")
        print("-" * 60)

        try:
            # Extract scope (triggers stack inference)
            scope = orchestrator._extract_scope(test['message'])

            # Verify stack_inference field exists
            has_inference = 'stack_inference' in scope
            confidence = scope.get('stack_inference', {}).get('confidence', 0)
            backend = scope.get('tech_stack', {}).get('backend', 'unknown')
            template = scope.get('stack_inference', {}).get('template_title', 'None')

            print(f"✅ Scope extracted successfully")
            print(f"   Has stack_inference: {has_inference}")
            if has_inference:
                print(f"   Backend: {backend}")
                print(f"   Confidence: {confidence:.2f}")
                print(f"   Template: {template}")
                print(f"   Rationale: {scope['stack_inference'].get('rationale', 'N/A')[:80]}...")

            # Validate
            passed = (
                has_inference and
                confidence >= test['expected_confidence_min'] and
                backend != 'unknown'
            )

            results.append({
                'test': test['message'][:50],
                'passed': passed,
                'confidence': confidence,
                'backend': backend
            })

            if passed:
                print(f"✅ Test PASSED")
            else:
                print(f"❌ Test FAILED (confidence {confidence:.2f} < {test['expected_confidence_min']})")

        except Exception as e:
            print(f"❌ Test FAILED with error: {e}")
            results.append({
                'test': test['message'][:50],
                'passed': False,
                'confidence': 0,
                'backend': 'error'
            })

    # Summary
    print("\n" + "="*60)
    print("📊 Test Summary")
    print("="*60)

    passed_count = sum(1 for r in results if r['passed'])
    total_count = len(results)

    for i, result in enumerate(results, 1):
        status = "✅ PASS" if result['passed'] else "❌ FAIL"
        print(f"{i}. {status} | Conf: {result['confidence']:.2f} | {result['test']}...")

    print(f"\nTotal: {passed_count}/{total_count} tests passed")

    if passed_count == total_count:
        print("\n🎉 All tests passed! Stack inference integration working correctly.")
        return True
    else:
        print(f"\n⚠️ {total_count - passed_count} tests failed. Check pgvector setup and embeddings.")
        return False


if __name__ == "__main__":
    try:
        success = test_stack_inference_integration()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test suite crashed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
