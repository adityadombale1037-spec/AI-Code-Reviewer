import ast
import builtins
import difflib


def analyze_python_code(code):
    errors = []

    # Step 1: Check syntax
    try:
        tree = ast.parse(code)

    except SyntaxError as error:
        error_type = type(error).__name__
        line_number = error.lineno or 1

        errors.append({
            "error_name": error_type,
            "line": line_number,
            "problem": error.msg,
            "explanation": (
                f"Python found a {error_type} on line "
                f"{line_number}. It could not understand "
                "the code's syntax."
            ),
            "solution": (
                "Check the syntax near this line. Look for "
                "missing colons, unmatched brackets, quotation "
                "marks, commas, or incorrect indentation."
            )
        })

        # Return a report for the syntax error
        return make_report(errors)

    # Step 2: Find variables that have been assigned
    defined_names = set(dir(builtins))
    user_defined_names = set()
    used_names = []
    variable_values = {}

    class CodeAnalyzer(ast.NodeVisitor):

        def visit_FunctionDef(self, node):
            defined_names.add(node.name)
            user_defined_names.add(node.name)

            arguments = (
                node.args.posonlyargs
                + node.args.args
                + node.args.kwonlyargs
            )

            for argument in arguments:
                defined_names.add(argument.arg)
                user_defined_names.add(argument.arg)

            if node.args.vararg:
                defined_names.add(node.args.vararg.arg)
                user_defined_names.add(node.args.vararg.arg)

            if node.args.kwarg:
                defined_names.add(node.args.kwarg.arg)
                user_defined_names.add(node.args.kwarg.arg)

            for statement in node.body:
                self.visit(statement)

        def visit_AsyncFunctionDef(self, node):
            self.visit_FunctionDef(node)

        def visit_ClassDef(self, node):
            defined_names.add(node.name)
            user_defined_names.add(node.name)

            for statement in node.body:
                self.visit(statement)

        def visit_Name(self, node):
            if isinstance(node.ctx, ast.Store):
                defined_names.add(node.id)
                user_defined_names.add(node.id)

            elif isinstance(node.ctx, ast.Load):
                used_names.append((node.id, node.lineno))

        def visit_Import(self, node):
            for alias in node.names:
                name = alias.asname or alias.name.split(".")[0]
                defined_names.add(name)
                user_defined_names.add(name)

        def visit_ImportFrom(self, node):
            for alias in node.names:
                if alias.name != "*":
                    name = alias.asname or alias.name
                    defined_names.add(name)
                    user_defined_names.add(name)

    analyzer = CodeAnalyzer()
    analyzer.visit(tree)

    # Step 3: Find simple variable assignments.
    # Example: b = 0
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue

        if len(node.targets) != 1:
            continue

        target = node.targets[0]
        value = node.value

        if not isinstance(target, ast.Name):
            continue

        # Record literal values such as 0, 10, "hello".
        if isinstance(value, ast.Constant):
            variable_values[target.id] = value.value
        else:
            # Avoid using an old value if the variable changes.
            variable_values.pop(target.id, None)

    # Step 4: Detect possible undefined names
    reported_names = set()

    for name, line_number in used_names:
        if name not in defined_names and name not in reported_names:
            reported_names.add(name)

            similar_names = difflib.get_close_matches(
                name,
                sorted(user_defined_names),
                n=1,
                cutoff=0.6
            )

            if similar_names:
                suggested_name = similar_names[0]

                solution = (
                    f"You used '{name}', but it is not defined. "
                    f"You defined '{suggested_name}' in your code. "
                    f"If you meant to use that variable, check "
                    f"whether '{suggested_name}' is the correct name."
                )
            else:
                solution = (
                    f"You used '{name}', but its definition "
                    "was not found. Check the spelling and "
                    "define the variable before using it."
                )

            errors.append({
                "error_name": "Possible NameError",
                "line": line_number,
                "problem": f"'{name}' may not be defined.",
                "explanation": (
                    f"Python needs '{name}' to refer to a "
                    "defined variable or function. Otherwise, "
                    "it may raise NameError when this line runs."
                ),
                "solution": solution
            })

    # Step 5: Detect division by zero, while recognizing simple guards
    parent_map = {
        child: parent
        for parent in ast.walk(tree)
        for child in ast.iter_child_nodes(parent)
    }

    def compares_variable_with_zero(test, variable_name):
        """Return the comparison operator when test compares var with 0."""
        if not isinstance(test, ast.Compare) or len(test.ops) != 1 or len(test.comparators) != 1:
            return None

        left = test.left
        right = test.comparators[0]

        def is_zero(value):
            return (
                isinstance(value, ast.Constant)
                and isinstance(value.value, (int, float))
                and not isinstance(value.value, bool)
                and value.value == 0
            )

        if isinstance(left, ast.Name) and left.id == variable_name and is_zero(right):
            return test.ops[0]
        if is_zero(left) and isinstance(right, ast.Name) and right.id == variable_name:
            return test.ops[0]
        return None

    def is_inside(statements, target):
        return any(
            descendant is target
            for statement in statements
            for descendant in ast.walk(statement)
        )

    def is_protected_by_zero_check(node, variable_name):
        """Recognize common guards such as if b == 0: ... else: a / b."""
        current = node
        while current in parent_map:
            child = current
            parent = parent_map[current]

            if isinstance(parent, ast.If):
                operator = compares_variable_with_zero(parent.test, variable_name)
                if operator is not None:
                    in_body = is_inside(parent.body, node)
                    in_else = is_inside(parent.orelse, node)

                    # if b == 0: ... else: a / b
                    if isinstance(operator, ast.Eq) and in_else:
                        return True
                    # if b != 0: a / b
                    if isinstance(operator, ast.NotEq) and in_body:
                        return True

            current = parent
        return False

    for node in ast.walk(tree):
        if not (
            isinstance(node, ast.BinOp)
            and isinstance(node.op, (ast.Div, ast.FloorDiv, ast.Mod))
        ):
            continue

        denominator = node.right
        zero_found = False
        denominator_description = ast.unparse(denominator)
        variable_name = denominator.id if isinstance(denominator, ast.Name) else None

        # Case A: 10 / 0
        if (
            isinstance(denominator, ast.Constant)
            and isinstance(denominator.value, (int, float))
            and not isinstance(denominator.value, bool)
            and denominator.value == 0
        ):
            zero_found = True

        # Case B: b = 0, then a / b
        elif variable_name is not None:
            if (
                variable_name in variable_values
                and isinstance(variable_values[variable_name], (int, float))
                and not isinstance(variable_values[variable_name], bool)
                and variable_values[variable_name] == 0
                and not is_protected_by_zero_check(node, variable_name)
            ):
                zero_found = True
                denominator_description = (
                    f"'{variable_name}', whose assigned value is 0"
                )

        if zero_found:
            errors.append({
                "error_name": "ZeroDivisionError",
                "line": node.lineno,
                "problem": (
                    f"The expression '{ast.unparse(node)}' "
                    "divides by zero."
                ),
                "explanation": (
                    f"The denominator is {denominator_description}. "
                    "Python cannot divide a number by zero."
                ),
                "solution": (
                    f"You are trying to divide by '{ast.unparse(denominator)}', "
                    "but its value is zero. Python cannot divide a number by zero. "
                    "Before dividing, check whether the denominator is zero. "
                    "If it is zero, display 'Cannot divide by zero.' "
                    "instead of performing the calculation."
                )
            })

    # Step 6: Detect simple string + number expressions
    for node in ast.walk(tree):
        if not (
            isinstance(node, ast.BinOp)
            and isinstance(node.op, ast.Add)
        ):
            continue

        left = node.left
        right = node.right

        left_string = (
            isinstance(left, ast.Constant)
            and isinstance(left.value, str)
        )

        right_string = (
            isinstance(right, ast.Constant)
            and isinstance(right.value, str)
        )

        left_number = (
            isinstance(left, ast.Constant)
            and isinstance(left.value, (int, float))
            and not isinstance(left.value, bool)
        )

        right_number = (
            isinstance(right, ast.Constant)
            and isinstance(right.value, (int, float))
            and not isinstance(right.value, bool)
        )

        if left_string and right_number:
            original = (
                f"{ast.unparse(left)} + {ast.unparse(right)}"
            )
            suggestion = (
                f"{ast.unparse(left)} + str({ast.unparse(right)})"
            )

        elif left_number and right_string:
            original = (
                f"{ast.unparse(left)} + {ast.unparse(right)}"
            )
            suggestion = (
                f"str({ast.unparse(left)}) + {ast.unparse(right)}"
            )

        else:
            continue

        errors.append({
            "error_name": "Possible TypeError",
            "line": node.lineno,
            "problem": (
                f"A string and a number are added directly: "
                f"{original}"
            ),
            "explanation": (
                "Python cannot directly add a string and a number. "
                "If you want to join them as text, convert the "
                "number to a string."
            ),
            "solution": (
                f"Consider changing '{original}' to "
                f"'{suggestion}'. This converts the number "
                "to a string before joining the values."
            )
        })

    return make_report(errors)


def make_report(errors):
    # Remove duplicate findings
    unique_errors = []
    seen = set()

    for error in errors:
        key = (
            error["error_name"],
            error["line"],
            error["problem"]
        )

        if key not in seen:
            seen.add(key)
            unique_errors.append(error)

    has_error = any(
        error["error_name"] in (
            "SyntaxError",
            "IndentationError",
            "ZeroDivisionError"
        )
        for error in unique_errors
    )

    has_warning = any(
        error["error_name"].startswith("Possible")
        for error in unique_errors
    )

    if has_error:
        status = "error"
    elif has_warning:
        status = "warning"
    else:
        status = "success"

    return {
        "status": status,
        "total_errors": len(unique_errors),
        "errors": unique_errors
    }


if __name__ == "__main__":
    sample_code = """
a = 10
b = 0
print(a / b)
"""

    report = analyze_python_code(sample_code)

    print("Status:", report["status"])
    print("Total findings:", report["total_errors"])

    for error in report["errors"]:
        print("\\n------------------------------")
        print("Error Name:", error["error_name"])
        print("Line:", error["line"])
        print("Problem:", error["problem"])
        print("Explanation:", error["explanation"])
        print("Suggestion:", error["solution"])