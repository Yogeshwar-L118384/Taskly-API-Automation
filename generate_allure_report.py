#!/usr/bin/env python3
"""
Generate Allure Report with Screenshots and Test Details
"""
import os
import subprocess
import sys
from pathlib import Path

def generate_allure_report():
    """Generate and open allure HTML report"""
    
    allure_bin = r"tools\allure\allure-2.35.1\bin\allure.bat"
    
    # Check if allure binary exists
    if not Path(allure_bin).exists():
        print(f"❌ Allure not found at {allure_bin}")
        print("Please ensure allure is installed in tools/allure/")
        return False
    
    try:
        print("📊 Generating Allure Report...")
        
        # Clean and generate report
        cmd = [allure_bin, "generate", "allure-results", "-o", "allure-report", "--clean"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Error generating report:\n{result.stderr}")
            return False
        
        print("✅ Report generated successfully!")
        print(f"📁 Location: {Path('allure-report').absolute()}")
        
        # Open report
        print("\n🌐 Opening report in browser...")
        cmd_open = [allure_bin, "open", "allure-report"]
        subprocess.Popen(cmd_open)
        
        print("✅ Report opened in default browser!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main entry point"""
    if not generate_allure_report():
        sys.exit(1)

if __name__ == "__main__":
    main()
