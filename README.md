# Virtual Environment Setup Guide for macOS

This guide explains how to create, activate, and manage a Python virtual environment on macOS.

---

## **Prerequisites**

1. **Python 3.x Installed**  
   Make sure Python 3.x is installed on your Mac. Check by running:
   ```bash
   python3 --version
   ```
   If not installed, use [Homebrew](https://brew.sh/) to install Python:
   ```bash
   brew install python
   ```

2. **Ensure `pip` is Installed**  
   Python 3.x should come with `pip`. Verify by running:
   ```bash
   pip3 --version
   ```

---

## **Steps to Create and Activate a Virtual Environment**

### **Step 1: Navigate to Your Project Directory**
Use the terminal to navigate to the folder where you want to set up your project:
```bash
cd /path/to/your/project
```

---

### **Step 2: Create a Virtual Environment**
Run the following command to create a virtual environment named `venv`:
```bash
python3 -m venv venv
```
- A directory named `venv` will be created, containing the virtual environment files.

---

### **Step 3: Activate the Virtual Environment**
To activate the virtual environment, use:
```bash
source venv/bin/activate
```
- After activation, the terminal prompt will display `(venv)` to indicate the virtual environment is active:
  ```plaintext
  (venv) your-mac:project user$
  ```

---

### **Step 4: Install Dependencies**
With the virtual environment active, you can install project dependencies using `pip`.  
For example:
```bash
pip install -r requirements.txt
```
- This will install all packages listed in the `requirements.txt` file.

---

### **Step 5: Deactivate the Virtual Environment**
When you're done working, deactivate the virtual environment by running:
```bash
deactivate
```
- The terminal prompt will return to its normal state.

---

## **Common Commands**

| Command                                   | Description                          |
|-------------------------------------------|--------------------------------------|
| `python3 -m venv venv`                    | Create a virtual environment.        |
| `source venv/bin/activate`                | Activate the virtual environment.    |
| `pip install <package>`                   | Install a package.                   |
| `pip install -r requirements.txt`         | Install packages from a file.        |
| `deactivate`                              | Deactivate the virtual environment.  |

---

## **Troubleshooting**

### Problem: `zsh: command not found: python3`
If Python 3 is not found, install it using Homebrew:
```bash
brew install python
```

### Problem: `Requirement already satisfied` or `pip command not found`
Ensure you’re using the correct `pip` inside the virtual environment:
```bash
which pip
```
The output should point to the `venv/bin/pip` directory.

---

Save this file as `README.md` or `virtual_env_guide.md`. Let me know if you need further assistance!

