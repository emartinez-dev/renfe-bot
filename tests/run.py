import os
import subprocess
import sys

# Set environment variable
os.environ["PYTHONPATH"] = "src/"

# Run coverage with pytest
subprocess.run(
    [sys.executable, "-m", "coverage", "run", "--branch", "--source=src", "-m", "pytest", "tests",
        "--ignore=tests/integration",],
    check=True
)

# Show coverage report
subprocess.run([sys.executable, "-m", "coverage", "report"], check=True)
subprocess.run([sys.executable, "-m", "coverage", "html"], check=True)
subprocess.run([sys.executable, "-m", "coverage", "xml"], check=True)
