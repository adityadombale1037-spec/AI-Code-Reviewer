# AI Code Reviewer & Bug Explainer

A beginner-friendly Python web application that checks submitted Python
code for common errors, explains possible problems in simple language,
and suggests ways to fix them.

## Features

-   **Code editor:** Paste Python code into the web interface.
-   **Static code analysis:** Uses Python's Abstract Syntax Tree (AST)
    to look for selected common coding problems.
-   **Beginner-friendly explanations:** Findings include the problem, an
    explanation, and a suggested solution.
-   **Line references:** Shows the line number associated with a finding
    when available.
-   **Combined report:** Combines findings from the basic and advanced
    analyzers and removes duplicate findings.
-   **Run code:** The app can attempt to run submitted code when the
    analyzer finds no issues.
-   **Web interface:** Built with Flask, HTML, and CSS.

> **Important limitation:** This is an educational project. Static
> analysis uses rules and heuristics, so it can miss bugs or report a
> possible issue that is not actually a bug. It does not understand
> every Python program.

## Technologies Used

-   Python
-   Flask
-   Python `ast` module for static analysis
-   HTML
-   CSS
-   Git and GitHub

Check `requirements.txt` for the Python packages used by this project.

## Project Structure

``` text
AI_Code_Reviewer/
├── app.py
├── analyzer.py
├── analyzer_2.py
├── requirements.txt
├── .gitignore
├── templates/
│   └── index.html
└── static/
    └── style.css
```

## Run the Project Locally

### 1. Install Python

Install a recent version of Python and make sure Python is available
from your terminal.

### 2. Open the project folder

Open this folder in VS Code, then open **Terminal → New Terminal**.

### 3. Create and activate a virtual environment (if you do not already have one)

On Windows PowerShell:

``` powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

If the virtual environment already exists, activate it with the second
command only.

### 4. Install dependencies

``` powershell
python -m pip install -r requirements.txt
```

### 5. Start the Flask application

``` powershell
python app.py
```

Open the local address printed in the terminal. If the app uses Flask's
default local address, it is usually:

``` text
http://127.0.0.1:5000
```

To stop the server, press **Ctrl + C** in the terminal.

## How to Use It

1.  Open the application in your browser.
2.  Paste Python code into the editor.
3.  Submit the code for analysis.
4.  Review each finding's problem, explanation, line number, and
    suggested solution.
5.  If the app runs the submitted code, review the output shown on the
    page.

## Security Warning

**Do not deploy this application publicly with unrestricted code
execution enabled.** Running code submitted by another person can be
dangerous. A timeout alone does not make execution safe.

Before public deployment, disable submitted-code execution or implement
a properly isolated sandbox with strict CPU, memory, filesystem,
network, and time limits. Do not run untrusted code with access to
secrets or important files.

## Current Limitations

-   The analyzer checks selected patterns; it is not a complete Python
    compiler or proof that code is bug-free.
-   Type and runtime-error predictions are heuristic and may not be
    correct for every program.
-   The suggested solution is guidance; the app does not automatically
    rewrite the entire program.
-   Code execution should be restricted to a trusted local development
    environment until proper sandboxing is implemented.

## Future Improvements

-   Add more static-analysis rules and tests.
-   Improve the explanations and suggested fixes.
-   Add automated unit tests.
-   Add a safer isolated execution environment before considering public
    deployment.
-   Improve accessibility and mobile layout.

## Author

**Aditya Dombale**

## License

No license has been added yet. Unless you add a license, others should
not assume they have permission to reuse, modify, or distribute this
project.
