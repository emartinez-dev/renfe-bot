#!/bin/sh

export PYTHONPATH="${PWD}/src"
echo PYTHONPATH=$PYTHONPATH

for script in tests/integration/test_*.py; do
    echo "Executing test: $script"
    if python "$script"; then
        echo "Test $script passed."
    else
        echo "Test $script failed!"
        exit 1
    fi
    echo "---------------------------------"
done

echo "All tests completed successfully."
