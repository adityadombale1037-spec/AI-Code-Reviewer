from flask import Flask, render_template, request
from analyzer import analyze_python_code
from analyzer_2 import analyze_python_code_advanced

import os
import sys
import tempfile
import subprocess


app = Flask(__name__)


 
def combine_reports(*reports):
    """Combine reports and remove duplicate findings."""

    combined_errors = []
    seen = set()

    for report in reports:
        for error in report.get("errors", []):

            error_name = error.get("error_name", "")
            line = error.get("line", 0)
            problem = error.get("problem", "")

            # Normalize error types so equivalent findings
            # from different analyzers can be recognized.
            normalized_type = error_name.replace(
                "Possible ", ""
            )

            if normalized_type == "TypeError":
                normalized_type = "TypeError"

            elif normalized_type == "ZeroDivisionError":
                normalized_type = "ZeroDivisionError"

            # Group findings by type and line number.
            # This avoids showing the same type of error twice
            # on the same line just because wording differs.
            key = (normalized_type, line)

            if key not in seen:
                seen.add(key)
                combined_errors.append(error)

    combined_errors.sort(key=lambda item: item.get("line", 0))

    has_error = any(
        error["error_name"] in (
            "SyntaxError",
            "IndentationError",
            "ZeroDivisionError",
            "Possible ZeroDivisionError"
        )
        for error in combined_errors
    )

    has_warning = any(
        error["error_name"].startswith("Possible")
        for error in combined_errors
    )

    if has_error:
        status = "error"
    elif has_warning:
        status = "warning"
    else:
        status = "success"

    return {
        "status": status,
        "total_errors": len(combined_errors),
        "errors": combined_errors
    }
 

def execute_python_code(code):
    """
    Run code for a local student prototype.

    WARNING:
    subprocess with a timeout is NOT a secure sandbox.
    Do not use this function to execute untrusted public
    submissions on a production server.
    """

    temporary_path = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            encoding="utf-8",
            delete=False
        ) as temporary_file:

            temporary_file.write(code)
            temporary_path = temporary_file.name

        completed = subprocess.run(
            [sys.executable, "-I", temporary_path],
            capture_output=True,
            text=True,
            timeout=3,
            cwd=tempfile.gettempdir()
        )

        if completed.returncode == 0:
            return {
                "success": True,
                "output": completed.stdout,
                "error": ""
            }

        return {
            "success": False,
            "output": completed.stdout,
            "error": completed.stderr
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "output": "",
            "error": (
                "Execution timed out after 3 seconds. "
                "The program may contain an infinite loop "
                "or a long-running operation."
            )
        }

    except Exception as error:
        return {
            "success": False,
            "output": "",
            "error": str(error)
        }

    finally:
        if temporary_path and os.path.exists(temporary_path):
            try:
                os.remove(temporary_path)
            except OSError:
                pass


@app.route("/", methods=["GET", "POST"])
def home():

    code = ""
    result = None
    execution_result = None

    if request.method == "POST":

        code = request.form.get("code", "")

        if not code.strip():

            result = {
                "status": "error",
                "total_errors": 1,
                "errors": [
                    {
                        "error_name": "EmptyCodeError",
                        "line": 1,
                        "problem": "No Python code was entered.",
                        "explanation": (
                            "The analyzer needs Python code "
                            "to check for possible problems."
                        ),
                        "solution": (
                            "Enter some Python code in the editor "
                            "and click Analyze Code again."
                        )
                    }
                ]
            }

        else:

            try:
                # Run the existing analyzer.
                basic_report = analyze_python_code(code)

                # Run the new advanced analyzer.
                advanced_report = analyze_python_code_advanced(code)

                # Combine the findings from both analyzers.
                result = combine_reports(
                    basic_report,
                    advanced_report
                )

                # Execute only when no findings were reported.
                # This is suitable only for a trusted local prototype.
                if result["total_errors"] == 0:
                    execution_result = execute_python_code(code)

            except Exception as error:

                result = {
                    "status": "error",
                    "total_errors": 1,
                    "errors": [
                        {
                            "error_name": "AnalyzerInternalError",
                            "line": 1,
                            "problem": str(error),
                            "explanation": (
                                "An unexpected error occurred "
                                "inside the analysis system."
                            ),
                            "solution": (
                                "Check the terminal for the "
                                "Python traceback and verify "
                                "that both analyzer files are "
                                "saved correctly."
                            )
                        }
                    ]
                }

    return render_template(
    "index.html",
    code=code,
    result=result,
    execution_result=execution_result
)


if __name__ == "__main__":
    app.run(debug=True)
 
