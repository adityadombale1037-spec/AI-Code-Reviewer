# 🐍 AI Code Reviewer & Bug Explainer

An AI-powered Python web application that helps developers identify common coding errors, understand bugs in simple English, and get suggestions to improve their code.

The application combines **Python static code analysis with Gemini AI** to provide useful error reports and beginner-friendly explanations.

## 🚀 Features

* **💻 Code Editor:** Enter or paste Python code into the web interface.
* **🔍 Static Code Analysis:** Uses Python's Abstract Syntax Tree (AST) and custom rules to identify selected coding problems.
* **🤖 Gemini AI Integration:** Uses Google's Gemini AI to explain code problems in simple, beginner-friendly language.
* **🐛 Bug Detection:** Identifies selected common errors, such as syntax errors, possible name errors, type errors, and division-by-zero problems.
* **💡 AI-Powered Explanations:** Helps users understand why a problem may occur and how to fix it.
* **🛠️ Fix Suggestions:** Provides suggested corrections for detected problems.
* **📍 Line References:** Displays line numbers for findings when available.
* **📋 Combined Error Report:** Combines findings from multiple analyzers and removes duplicate results.
* **▶️ Code Execution:** Can run submitted Python code and display its output when execution is enabled and the application's checks allow it.
* **🎨 User-Friendly Interface:** Built with HTML and CSS, including a Times New Roman font style.
* **🌐 Web-Based Application:** Access the tool through a browser using a Flask web server.

> **Note:** Gemini AI explanations depend on a valid API configuration and network availability. AI-generated suggestions may not always be correct.

## 🧰 Technologies Used

| Technology        | Purpose                                 |
| ----------------- | --------------------------------------- |
| Python            | Main programming language               |
| Flask             | Web application backend                 |
| Python AST        | Static code analysis                    |
| Google Gemini AI  | AI-powered explanations and suggestions |
| Google Gen AI SDK | Communication with the Gemini API       |
| HTML              | Web page structure                      |
| CSS               | Website styling                         |
| Git               | Version control                         |
| GitHub            | Source code hosting                     |

See `requirements.txt` for the Python packages required by the project.

## 📁 Project Structure

```text
AI_Code_Reviewer_my/
├── app.py
├── analyzer.py
├── analyzer_2.py
├── ai_helper.py
├── requirements.txt
├── .gitignore
├── templates/
│   └── index.html
└── static/
    └── style.css
```

The structure above shows the main application files. Other files may exist in your local project folder.

## ⚙️ Installation and Setup

### 1. Install Python

Install Python and make sure it is available from your terminal.

### 2. Clone the repository

```bash
git clone https://github.com/adityadombale1037-spec/AI-Code-Reviewer.git
```

### 3. Open the project folder

```bash
cd AI-Code-Reviewer
```

Open the folder in VS Code.

### 4. Create a virtual environment

On Windows PowerShell:

```powershell
python -m venv venv
```

Activate it:

```powershell
.\venv\Scripts\Activate.ps1
```

If your virtual environment already exists, activate it instead of creating another one.

### 5. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 6. Configure the Gemini API key

The application uses a Gemini API key to request AI-generated explanations.

Create or obtain your API key through Google's official AI developer platform.

Set the `GEMINI_API_KEY` environment variable in PowerShell:

```powershell
$env:GEMINI_API_KEY="YOUR_API_KEY_HERE"
```

Replace `YOUR_API_KEY_HERE` with your own API key.

**Security warning:**

* Never publish your real API key on GitHub.
* Do not hardcode the key in `app.py`, `ai_helper.py`, or other source files.
* Do not commit `.env` files containing secrets.
* Configure environment variables separately for each deployment platform.

The PowerShell command above sets the key for the current terminal session. You may need to set it again when opening a new terminal.

### 7. Run the application

```powershell
python app.py
```

Open the local address displayed in your terminal. If Flask uses its default address, it is usually:

```text
http://127.0.0.1:5000
```

To stop the application, press `Ctrl + C` in the terminal.

## 📝 How to Use

1. Start the Flask application.
2. Open the website in your browser.
3. Enter or paste Python code into the code editor.
4. Submit the code for analysis.
5. Review the detected problems and their line numbers.
6. Read the explanations and suggested fixes.
7. If code execution is enabled and permitted, review the program output or runtime error.

## 🔐 Security Considerations

**Do not deploy this application publicly with unrestricted execution of user-submitted code.**

Executing untrusted Python code can expose files, secrets, and system resources. A timeout alone does not make code execution safe.

Before allowing public users to submit and execute code, disable execution or implement a properly isolated sandbox with strict CPU, memory, filesystem, network, and time restrictions.

Also:

* Keep API keys and other secrets out of source control.
* Configure API keys securely on the deployment platform.
* Handle API errors, rate limits, and unavailable services.
* Avoid exposing sensitive error messages or environment variables to users.

## ⚠️ Limitations

* Static analysis checks selected patterns and cannot identify every possible bug.
* Some findings may be false positives or may miss problems.
* Gemini AI may generate inaccurate explanations or suggestions.
* AI explanations require a working API configuration and network access.
* Code execution must be properly restricted before public deployment.
* Suggested fixes should be reviewed and tested before use.

## 🔮 Future Improvements

* Add more static-analysis rules and automated tests.
* Improve the accuracy of bug detection and explanations.
* Add more detailed AI-generated code suggestions.
* Implement secure, isolated code execution.
* Improve the user interface and mobile responsiveness.
* Add support for additional programming languages.
* Improve error handling and API usage management.

## 👨‍💻 Author

**Aditya Dombale**

Computer Engineering Student

## 📄 License

No license has been added yet. Unless a license is added, others should not assume they have permission to reuse, modify, or distribute this project.
