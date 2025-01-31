import os
import glob
import subprocess
import sys

# Set PYTHONPATH
os.environ["PYTHONPATH"] = os.path.join(os.getcwd(), "src")
print(f"PYTHONPATH={os.environ['PYTHONPATH']}")

# Get all integration test scripts
test_scripts = glob.glob("tests/integration/test_*.py")

for script in test_scripts:
    print(f"Executing test: {script}")
    
    # Run the script
    result = subprocess.run([sys.executable, script], check=False)
    
    if result.returncode == 0:
        print(f"Test {script} passed.")
    else:
        print(f"Test {script} failed!")
        sys.exit(1)  # Exit with failure status
    
    print("---------------------------------")

print("All tests completed successfully.")
