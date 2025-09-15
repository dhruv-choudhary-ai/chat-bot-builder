#!/usr/bin/env python3
"""
Master test runner for AILifeBotAssist
Runs all tests in the correct sequence
"""
import subprocess
import sys
import os
import time
import signal
from typing import Optional

class TestRunner:
    def __init__(self):
        self.server_process: Optional[subprocess.Popen] = None
        
    def print_section(self, title: str):
        """Print a formatted section header"""
        print(f"\n{'='*70}")
        print(f"  {title}")
        print(f"{'='*70}")

    def run_setup_tests(self) -> bool:
        """Run setup and environment tests"""
        self.print_section("SETUP & ENVIRONMENT TESTS")
        try:
            result = subprocess.run([sys.executable, "test_setup.py"], 
                                  capture_output=False, text=True)
            return result.returncode == 0
        except Exception as e:
            print(f"❌ Setup tests failed: {e}")
            return False

    def run_database_tests(self) -> bool:
        """Run database tests"""
        self.print_section("DATABASE TESTS")
        try:
            result = subprocess.run([sys.executable, "test_database.py"], 
                                  capture_output=False, text=True)
            return result.returncode == 0
        except Exception as e:
            print(f"❌ Database tests failed: {e}")
            return False

    def start_server(self) -> bool:
        """Start the FastAPI server"""
        self.print_section("STARTING TEST SERVER")
        try:
            # Start server in background
            self.server_process = subprocess.Popen([
                sys.executable, "-m", "uvicorn", "main:app", 
                "--host", "127.0.0.1", "--port", "8000", "--reload"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait for server to start
            print("Starting server...")
            time.sleep(5)
            
            # Check if server is still running
            if self.server_process.poll() is None:
                print("✅ Server started successfully on http://127.0.0.1:8000")
                return True
            else:
                print("❌ Server failed to start")
                return False
                
        except Exception as e:
            print(f"❌ Failed to start server: {e}")
            return False

    def stop_server(self):
        """Stop the FastAPI server"""
        if self.server_process:
            print("\nStopping server...")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.server_process.kill()
            print("✅ Server stopped")

    def run_api_tests(self) -> bool:
        """Run API tests"""
        self.print_section("API TESTS")
        try:
            result = subprocess.run([sys.executable, "test_api.py"], 
                                  capture_output=False, text=True)
            return result.returncode == 0
        except Exception as e:
            print(f"❌ API tests failed: {e}")
            return False

    def run_all_tests(self) -> bool:
        """Run all tests in sequence"""
        print("AILifeBotAssist - Master Test Runner")
        print("=" * 70)
        print("This will run all tests for the AILifeBotAssist project")
        print("Make sure you have:")
        print("1. Set up your .env file (copy from .env.example)")
        print("2. Installed all requirements: pip install -r requirements.txt")
        print("3. Set up your database and run migrations")
        
        input("\nPress Enter to continue or Ctrl+C to cancel...")
        
        try:
            # Run tests in sequence
            tests = [
                ("Setup & Environment", self.run_setup_tests),
                ("Database", self.run_database_tests),
            ]
            
            # Run offline tests first
            offline_results = []
            for test_name, test_func in tests:
                try:
                    result = test_func()
                    offline_results.append((test_name, result))
                    if not result:
                        print(f"\n⚠️  {test_name} tests failed. Continuing with remaining tests...")
                except KeyboardInterrupt:
                    print("\n\n❌ Tests interrupted by user")
                    return False
                except Exception as e:
                    print(f"\n❌ Critical error in {test_name}: {e}")
                    offline_results.append((test_name, False))
            
            # Start server and run API tests
            server_started = self.start_server()
            api_result = False
            
            if server_started:
                try:
                    api_result = self.run_api_tests()
                finally:
                    self.stop_server()
            else:
                print("⚠️  Skipping API tests due to server startup failure")
            
            # Compile all results
            all_results = offline_results + [("API Tests", api_result)]
            
            # Final summary
            self.print_section("FINAL TEST SUMMARY")
            passed = sum(1 for _, result in all_results if result)
            total = len(all_results)
            
            for test_name, result in all_results:
                status = "✅ PASS" if result else "❌ FAIL"
                print(f"{status} | {test_name}")
            
            print(f"\nOverall Results: {passed}/{total} test suites passed")
            success_rate = (passed / total) * 100
            print(f"Success Rate: {success_rate:.1f}%")
            
            if success_rate >= 75:
                print("\n🎉 Testing completed successfully!")
                print("\nYour AILifeBotAssist application is ready for use!")
                print("\nTo start the server manually:")
                print("  uvicorn main:app --reload")
                print("\nTo access the application:")
                print("  http://localhost:8000")
            else:
                print("\n⚠️  Some critical tests failed.")
                print("Please review the issues above before deploying to production.")
            
            return success_rate >= 75
            
        except KeyboardInterrupt:
            print("\n\n❌ Tests interrupted by user")
            self.stop_server()
            return False
        except Exception as e:
            print(f"\n❌ Critical error during testing: {e}")
            self.stop_server()
            return False

    def __del__(self):
        """Cleanup when object is destroyed"""
        self.stop_server()

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\n\nReceived interrupt signal. Cleaning up...")
    sys.exit(1)

def main():
    """Main test execution"""
    signal.signal(signal.SIGINT, signal_handler)
    
    # Change to the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    runner = TestRunner()
    success = runner.run_all_tests()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
