# Project Setup
This guide will help you set up a virtual environment for the project and install all necessary dependencies listed in the requirements.txt file.

## Prerequisites
Ensure that you have the following installed on your machine:

- Python 3.x
- pip (Python package manager)

If you don’t have Python installed, download and install it from [here](https://www.python.org/downloads/).

## Step 1: Install venv (if not already installed)
First, check if you have the venv package installed. If not, follow the instructions below based on your operating system.

### Ubuntu/Debian
```bash
sudo apt-get install python3-venv
```

### MacOS

**venv** comes pre-installed with Python 3.x on macOS. If you encounter issues, ensure you're using the correct Python version installed via Homebrew or similar.

### Windows
**venv** is included with Python 3.x on Windows. No additional installation should be required.

## Step 2: Create a Virtual Environment

In the root directory of the project, run the following command to create a virtual environment named venv:

```bash
python3 -m venv venv
```

### For Windows:

```bash
python -m venv venv
```

## Step 3: Activate the Virtual Environment

### On macOS/Linux:

```bash
source venv/bin/activate
```

### On Windows:
```bash
venv\Scripts\activate
```

After activation, your terminal should reflect that you're inside the virtual environment.

## Step 4: Install Dependencies

Once the virtual environment is activated, install the required dependencies from requirements.txt by running:

```bash
pip install -r requirements.txt
```

## Step 5: Deactivate the Virtual Environment

After working on the project, you can deactivate the virtual environment by running:

```bash
deactivate
```

## Additional Notes
Ensure you have the latest version of pip by running:

```bash
pip install --upgrade pip
```