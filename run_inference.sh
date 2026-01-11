#!/bin/bash

SCRIPT_PATH="./image_recognition/inference/inference_control"
VENV_PATH="../../../venv"
PYTHON_SCRIPT="./inferenceWebInterface_test.py"
PYTHON_EXECUTABLE="${VENV_PATH}/bin/python"

# --- Script Execution ---

cd "$SCRIPT_PATH"

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to change directory to ${PATH}. Exiting."
    exit 1
fi

echo "Starting robot inference script..."
echo "Checking for virtual environment at: ${VENV_PATH}"

if [ ! -d "$VENV_PATH" ]; then
    echo "ERROR: Virtual environment directory not found at '$VENV_PATH'."
    echo "Please make sure the venv is created and the path is correct."
    exit 1
fi

echo "Activating virtual environment..."
source "${VENV_PATH}/bin/activate"

if [ $? -eq 0 ]; then
    echo "Virtual environment activated successfully."
    echo "Running Python script: ${PYTHON_SCRIPT}"

    if [ -f "$PYTHON_SCRIPT" ]; then
        "$PYTHON_EXECUTABLE" "$PYTHON_SCRIPT"
        
        # Check the exit status of the Python script
        if [ $? -eq 0 ]; then
            echo "Python script finished successfully."
        else
            echo "ERROR: Python script failed with exit code $?."
        fi
    else
        echo "ERROR: Python script not found at '$PYTHON_SCRIPT'."
    fi
else
    echo "ERROR: Failed to activate virtual environment."
fi

deactivate

echo "Script execution complete."