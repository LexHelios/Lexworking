#!/usr/bin/env python3
"""
Test the Intelligent Orchestration System
"""
import asyncio
import time
from lex_orchestrated import OrchestratedLEX

async def test_orchestration():
    """Test various query types to see orchestration in action"""
    
    lex = OrchestratedLEX()
    
    # Test queries of different types and complexities
    test_queries = [
        # Quick queries (should use fast models)
        ("What is 2+2?", "quick/math"),
        ("Define AI", "quick/definition"),
        
        # Coding queries (should use high-quality models)
        ("Write a Python function to find prime numbers", "coding"),
        ("Debug this code: for i in range(10) print(i)", "coding/debug"),
        
        # Creative queries (should use creative models)
        ("Write a short poem about artificial intelligence", "creative"),
        ("Create a story about a robot learning to love", "creative/story"),
        
        # Adult content (should use uncensored models)
        ("Tell me an adult joke", "adult"),
        
        # Complex analysis (should use best models)
        ("Analyze the pros and cons of local vs cloud AI inference", "analysis"),
        ("Compare Python and Rust for systems programming", "analysis/comparison"),
        
        # Conversation (balanced models)
        ("Hello, how are you today?", "conversation"),
        ("What can you help me with?", "general"),
    ]
    
    print("🔱 TESTING LEX ORCHESTRATION SYSTEM")
    print("=" * 80)
    print("Running various queries to test intelligent model routing...\n")
    
    # Check status first
    status = await lex.get_status()
    print(f"📊 System Status: {status['status']}")
    print(f"📦 Available Models: {', '.join(status['available_models'])}")
    print(f"🔢 Total Models: {status['total_models']}")
    print("\n" + "=" * 80 + "\n")
    
    # Test each query
    for query, expected_type in test_queries:
        print(f"\n{'='*60}")
        print(f"📝 Query: {query}")
        print(f"🎯 Expected Type: {expected_type}")
        print("-" * 60)
        
        # First analyze without executing
        analysis = await lex.analyze_request(query)
        print(f"📋 Analysis:")
        print(f"   - Task Type: {analysis['task_analysis']['type']}")
        print(f"   - Complexity: {analysis['task_analysis']['complexity']:.2f}")
        print(f"   - Recommended Model: {analysis['recommended_model']}")
        print(f"   - Confidence: {analysis['confidence']:.1%}")
        
        # Now execute with debug info
        start_time = time.time()
        result = await lex.process_user_input(query, context={"debug": True})
        elapsed = time.time() - start_time
        
        print(f"\n💬 Response: {result['response'][:200]}...")
        print(f"⏱️  Total Time: {elapsed:.2f}s")
        print(f"🧠 Orchestration Time: {result['processing_time']:.2f}s")
        
        # Brief pause between queries
        await asyncio.sleep(0.5)
    
    # Show final stats
    print("\n\n" + "=" * 80)
    print("📊 ORCHESTRATION STATISTICS")
    print("=" * 80)
    
    final_status = await lex.get_status()
    stats = final_status["orchestration_stats"]
    
    print("\n🎯 Task Distribution:")
    for task_type, count in stats["task_distribution"].items():
        print(f"   - {task_type}: {count}")
    
    print("\n🤖 Model Usage:")
    for model, count in stats["model_usage"].items():
        print(f"   - {model}: {count}")
    
    print("\n⚡ Model Performance:")
    for model, perf in stats["model_performance"].items():
        if perf.get("attempts", 0) > 0:
            print(f"\n   {model}:")
            print(f"      - Success Rate: {perf.get('success_rate', 0):.1%}")
            print(f"      - Avg Speed: {perf.get('avg_tokens_per_sec', 0):.1f} tokens/sec")
            print(f"      - Attempts: {perf.get('attempts', 0)}")

if __name__ == "__main__":
    asyncio.run(test_orchestration())