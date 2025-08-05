#!/usr/bin/env python3
"""
LEX AI Fixed System Startup
🔱 JAI MAHAKAAL! Start the enhanced LEX system with all fixes applied
"""

import os
import sys
import subprocess
from pathlib import Path

def check_environment():
    """Check if environment is set up correctly"""
    print("🔱 LEX AI System Startup - Checking Environment 🔱")
    print("=" * 60)
    
    # Check Python version
    python_version = sys.version_info
    print(f"🐍 Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version < (3, 8):
        print("❌ Python 3.8+ required")
        return False
    
    # Check required files
    required_files = [
        "simple_lex_server.py",
        "lex_ai_with_memory.py", 
        "lex_memory_system.py",
        "server/orchestrator/multi_model_engine.py"
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    
    print("✅ All required files present")
    
    # Check environment variables
    env_vars = ["GROQ_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY"]
    available_keys = []
    
    for var in env_vars:
        if os.getenv(var):
            available_keys.append(var)
    
    if available_keys:
        print(f"✅ Available API keys: {', '.join(available_keys)}")
    else:
        print("⚠️ No API keys found - LEX will run with fallback responses")
        print("💡 Set GROQ_API_KEY, OPENAI_API_KEY, or ANTHROPIC_API_KEY for full functionality")
    
    return True

def show_startup_options():
    """Show available startup options"""
    print("\n🚀 LEX System Startup Options:")
    print("1. Full LEX System (simple_lex_server.py) - Recommended")
    print("2. Memory-focused LEX (lex_ai_with_memory.py) - For testing memory")
    print("3. Run tests (test_lex_fixes.py)")
    print("4. Exit")
    
    choice = input("\nSelect option (1-4): ").strip()
    return choice

def start_server(script_name):
    """Start the selected server"""
    print(f"\n🔱 Starting {script_name}...")
    print("=" * 60)
    print("🌟 LEX AI System Features:")
    print("✅ Persistent memory across conversations")
    print("✅ User name and context retention")
    print("✅ Proper response generation")
    print("✅ Thinking tags completely hidden")
    print("✅ Comprehensive capabilities listing")
    print("✅ Multi-model AI orchestration")
    print("=" * 60)
    print("🌐 Server will be available at: http://localhost:8000")
    print("📱 Simple interface: http://localhost:8000/simple")
    print("🔧 IDE interface: http://localhost:8000/ide")
    print("📚 API docs: http://localhost:8000/docs")
    print("=" * 60)
    print("Press Ctrl+C to stop the server")
    print()
    
    try:
        subprocess.run([sys.executable, script_name], check=True)
    except KeyboardInterrupt:
        print("\n🔱 LEX AI System stopped gracefully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Server error: {e}")

def run_tests():
    """Run the test suite"""
    print("\n🧪 Running LEX AI System Tests...")
    print("=" * 60)
    print("⚠️ Make sure a LEX server is running on port 8000 first!")
    print("   You can start it in another terminal with option 1 or 2")
    print()
    
    proceed = input("Continue with tests? (y/N): ").strip().lower()
    if proceed in ['y', 'yes']:
        try:
            subprocess.run([sys.executable, "test_lex_fixes.py"], check=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ Test error: {e}")
    else:
        print("Tests cancelled")

def main():
    """Main startup function"""
    if not check_environment():
        print("❌ Environment check failed. Please fix the issues above.")
        sys.exit(1)
    
    while True:
        choice = show_startup_options()
        
        if choice == "1":
            start_server("simple_lex_server.py")
            break
        elif choice == "2":
            start_server("lex_ai_with_memory.py")
            break
        elif choice == "3":
            run_tests()
            continue  # Return to menu after tests
        elif choice == "4":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please select 1-4.")

if __name__ == "__main__":
    main()