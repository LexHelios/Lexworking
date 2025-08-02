#!/usr/bin/env python3
"""
Test PDF processing to diagnose incomplete responses
"""
import asyncio
import sys
sys.path.append('.')

async def test_pdf_processing():
    # Test the multimodal processor
    from lex_multimodal_processor import multimodal_processor
    
    # Create a test PDF path
    test_pdf = "test.pdf"  # You'll need to provide a real PDF
    
    print("Testing PDF processing...")
    
    # Process the PDF
    result = await multimodal_processor.process_file(test_pdf)
    print(f"\nPDF Processing Result:")
    print(f"Success: {result.get('success')}")
    print(f"Content Type: {result.get('content_type')}")
    print(f"Requires Vision: {result.get('requires_vision_model')}")
    print(f"Text Length: {len(result.get('data', {}).get('text', ''))}")
    print(f"Total Pages: {result.get('data', {}).get('total_pages', 0)}")
    
    # Test prompt preparation
    test_prompt = "What is this document about?"
    prepared = multimodal_processor.prepare_multimodal_prompt(test_prompt, result)
    print(f"\nPrepared Prompt Length: {len(prepared)}")
    print(f"Prepared Prompt Preview:\n{prepared[:500]}...")
    
    # Test with orchestrator
    from lex_intelligent_orchestrator import orchestrator
    
    print("\nTesting orchestration...")
    orch_result = await orchestrator.orchestrate_request(
        user_input=test_prompt,
        file_contexts=[result] if result.get('success') else []
    )
    
    print(f"\nOrchestration Result:")
    print(f"Model Used: {orch_result.get('model_used')}")
    print(f"Response Length: {len(orch_result.get('response', ''))}")
    print(f"Response Preview:\n{orch_result.get('response', '')[:200]}...")

if __name__ == "__main__":
    print("PDF Response Testing")
    print("=" * 50)
    print("\nNote: This test requires a PDF file named 'test.pdf' in the current directory")
    print("You can also modify the script to use a different PDF path\n")
    
    # Run the test
    asyncio.run(test_pdf_processing())