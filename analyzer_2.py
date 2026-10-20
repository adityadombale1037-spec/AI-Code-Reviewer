import ast
import builtins
import keyword


def analyze_python_code_advanced(code):

    errors = []

    # --------------------------------------------------
    # Helper function to add a finding
    # --------------------------------------------------

    def add_finding(
        error_name,
        line,
        problem,
        explanation,
        solution
    ):
        errors.append({
            "error_name": error_name,
            "line": line,
            "problem": problem,
            "explanation": explanation,
            "solution": solution
        })

    # --------------------------------------------------
    # 1. Parse Python code
    # --------------------------------------------------

    try:
        tree = ast.parse(code)

    except SyntaxError as error:
        add_finding(
            "SyntaxError",
            error.lineno or 1,
            error.msg,
            "The Python code contains invalid syntax.",
            "Check the syntax near the reported line and correct it."
        )

        return make_report(errors)

    # --------------------------------------------------
    # Collect names defined in the code
    # --------------------------------------------------

    defined_names = set(dir(builtins))
    defined_names.update(keyword.kwlist)

    for node in ast.walk(tree):

        if isinstance(node, ast.Name):
            if isinstance(node.ctx, (ast.Store, ast.Param)):
                defined_names.add(node.id)

        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            defined_names.add(node.name)

            for argument in node.args.posonlyargs:
                defined_names.add(argument.arg)

            for argument in node.args.args:
                defined_names.add(argument.arg)

            for argument in node.args.kwonlyargs:
                defined_names.add(argument.arg)

            if node.args.vararg:
                defined_names.add(node.args.vararg.arg)

            if node.args.kwarg:
                defined_names.add(node.args.kwarg.arg)

        elif isinstance(node, ast.ClassDef):
            defined_names.add(node.name)

        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias in node.names:
                if alias.name != "*":
                    defined_names.add(
                        alias.asname or alias.name.split(".")[0]
                    )

    # --------------------------------------------------
    # 2. Detect possible NameError
    # --------------------------------------------------

    reported_names = set()

    for node in ast.walk(tree):

        if not isinstance(node, ast.Name):
            continue

        if not isinstance(node.ctx, ast.Load):
            continue

        if node.id not in defined_names:

            if node.id in reported_names:
                continue

            reported_names.add(node.id)

            add_finding(
                "Possible NameError",
                node.lineno,
                f"Name '{node.id}' may not be defined.",
                (
                    "Python cannot use a variable or name "
                    "that has not been defined."
                ),
                (
                    f"Check the spelling of '{node.id}' "
                    "and make sure it is defined before use."
                )
            )

    # --------------------------------------------------
    # 3. Detect possible TypeError
    # --------------------------------------------------

    def get_simple_type(node):

        if isinstance(node, ast.Constant):
            return type(node.value)

        if isinstance(node, ast.List):
            return list

        if isinstance(node, ast.Tuple):
            return tuple

        if isinstance(node, ast.Set):
            return set

        if isinstance(node, ast.Dict):
            return dict

        if isinstance(node, ast.JoinedStr):
            return str

        return None

    def report_type_error(node, message):

        add_finding(
            "Possible TypeError",
            node.lineno,
            message,
            (
                "This operation may use incompatible data types. "
                "Python does not allow every operation between "
                "different types."
            ),
            (
                "Check the data types before performing the operation. "
                "Convert a value when necessary, for example with "
                "str(), int(), or float()."
            )
        )

    for node in ast.walk(tree):

        # Check arithmetic and addition operations.
        if isinstance(node, ast.BinOp):

            left_type = get_simple_type(node.left)
            right_type = get_simple_type(node.right)

            # String + number and number + string.
            if isinstance(node.op, ast.Add):

                if (
                    left_type is str
                    and right_type in (int, float, complex)
                ) or (
                    right_type is str
                    and left_type in (int, float, complex)
                ):
                    report_type_error(
                        node,
                        "A string and a number are being added directly."
                    )

            # Number - string, number * string, etc.
            if isinstance(node.op, (ast.Sub, ast.Div, ast.FloorDiv,
                                     ast.Mod, ast.Pow)):

                numeric_types = (int, float, complex)

                if (
                    left_type is str
                    and right_type in numeric_types
                ) or (
                    right_type is str
                    and left_type in numeric_types
                ):
                    report_type_error(
                        node,
                        "This arithmetic operation uses a string "
                        "and a number in an incompatible way."
                    )

            # List + string or tuple + list.
            if isinstance(node.op, ast.Add):

                incompatible = (
                    (left_type is list and right_type is str)
                    or (left_type is str and right_type is list)
                    or (left_type is tuple and right_type is list)
                    or (left_type is list and right_type is tuple)
                )

                if incompatible:
                    report_type_error(
                        node,
                        "The two values have incompatible types "
                        "for this addition operation."
                    )

        # Check calls such as len(10) and int("hello").
        if isinstance(node, ast.Call):

            if not isinstance(node.func, ast.Name):
                continue

            function_name = node.func.id

            if not node.args:
                continue

            first_type = get_simple_type(node.args[0])

            if function_name == "len":
                if first_type in (int, float, complex, bool):
                    report_type_error(
                        node,
                        "len() cannot be used with a number."
                    )

            elif function_name == "int":
                argument = node.args[0]

                if (
                    isinstance(argument, ast.Constant)
                    and isinstance(argument.value, str)
                ):
                    try:
                        int(argument.value)
                    except ValueError:
                        report_type_error(
                            node,
                            "This string cannot be converted to an integer."
                        )

            elif function_name == "float":
                argument = node.args[0]

                if (
                    isinstance(argument, ast.Constant)
                    and isinstance(argument.value, str)
                ):
                    try:
                        float(argument.value)
                    except ValueError:
                        report_type_error(
                            node,
                            "This string cannot be converted to a float."
                        )

    # --------------------------------------------------
    # 4. Detect possible ZeroDivisionError
    # --------------------------------------------------

    for node in ast.walk(tree):

        if not isinstance(node, ast.BinOp):
            continue

        if not isinstance(node.op, (ast.Div, ast.FloorDiv, ast.Mod)):
            continue

        right = node.right

        if (
            isinstance(right, ast.Constant)
            and isinstance(right.value, (int, float, complex))
            and not isinstance(right.value, bool)
            and right.value == 0
        ):
            add_finding(
                "Possible ZeroDivisionError",
                node.lineno,
                "The operation divides by zero.",
                "Python cannot divide a number by zero.",
                "Check the denominator and make sure it is not zero."
            )

    # --------------------------------------------------
    # 5. Collect simple collection information
    # --------------------------------------------------

    known_collections = {}
    known_dictionaries = {}
    known_types = {}

    for node in ast.walk(tree):

        if not isinstance(node, ast.Assign):
            continue

        value = node.value

        if isinstance(value, (ast.List, ast.Tuple)):
            collection_length = len(value.elts)

            for target in node.targets:
                if isinstance(target, ast.Name):
                    known_collections[target.id] = collection_length

        elif isinstance(value, ast.Dict):

            keys = {
                key.value
                for key in value.keys
                if isinstance(key, ast.Constant)
            }

            for target in node.targets:
                if isinstance(target, ast.Name):
                    known_dictionaries[target.id] = set(keys)

        value_type = get_simple_type(value)

        if value_type is not None:
            for target in node.targets:
                if isinstance(target, ast.Name):
                    known_types[target.id] = value_type

    # --------------------------------------------------
    # 6. Detect more IndexError cases
    # --------------------------------------------------

    for node in ast.walk(tree):

        if not isinstance(node, ast.Subscript):
            continue

        container = node.value
        index_node = node.slice

        length = None

        # Direct indexing: [10, 20][5]
        if isinstance(container, (ast.List, ast.Tuple)):
            length = len(container.elts)

        # Variable indexing: numbers[5]
        elif (
            isinstance(container, ast.Name)
            and container.id in known_collections
        ):
            length = known_collections[container.id]

        # Skip slices and non-integer indexes.
        if not (
            isinstance(index_node, ast.Constant)
            and isinstance(index_node.value, int)
            and not isinstance(index_node.value, bool)
        ):
            continue

        if length is None:
            continue

        index = index_node.value

        if index >= length or index < -length:

            add_finding(
                "Possible IndexError",
                node.lineno,
                (
                    f"Index {index} is invalid for a collection "
                    f"containing {length} items."
                ),
                (
                    "Python uses zero-based indexing. "
                    "The requested index does not refer to an item "
                    "in this collection."
                ),
                (
                    f"Use an index between {-length} and {length - 1}, "
                    "or check the collection length before accessing it."
                )
            )

    # --------------------------------------------------
    # 7. Detect more KeyError cases
    # --------------------------------------------------

    for node in ast.walk(tree):

        if not isinstance(node, ast.Subscript):
            continue

        container = node.value
        key_node = node.slice

        # Direct dictionary access: {"a": 1}["b"]
        if isinstance(container, ast.Dict):

            existing_keys = {
                key.value
                for key in container.keys
                if isinstance(key, ast.Constant)
            }

        # Variable dictionary access: student["marks"]
        elif (
            isinstance(container, ast.Name)
            and container.id in known_dictionaries
        ):
            existing_keys = known_dictionaries[container.id]

        else:
            continue

        if not isinstance(key_node, ast.Constant):
            continue

        requested_key = key_node.value

        if requested_key not in existing_keys:

            add_finding(
                "Possible KeyError",
                node.lineno,
                f"Key {requested_key!r} may not exist in this dictionary.",
                (
                    "Python raises a KeyError when a dictionary "
                    "is accessed using a missing key."
                ),
                (
                    "Check whether the key exists before accessing it, "
                    "or use dictionary.get(key) when appropriate."
                )
            )
 
    # --------------------------------------------------
    # 8. Improved AttributeError detection
    # --------------------------------------------------

    valid_attributes = {
        str: set(dir(str)),
        list: set(dir(list)),
        tuple: set(dir(tuple)),
        dict: set(dir(dict)),
        set: set(dir(set)),
        int: set(dir(int)),
        float: set(dir(float)),
        bool: set(dir(bool)),
    }

    # Remember types of simple variables.
    known_types = {}

    # Remember types of values inside simple dictionaries.
    known_dictionary_value_types = {}

    for statement in ast.walk(tree):

        if not isinstance(statement, ast.Assign):
            continue

        value = statement.value

        # Example: name = "Aditya"
        value_type = get_simple_type(value)

        for target in statement.targets:

            if not isinstance(target, ast.Name):
                continue

            variable_name = target.id

            if value_type is not None:
                known_types[variable_name] = value_type

            # Example:
            # student = {"name": "Aditya", "age": 19}
            if isinstance(value, ast.Dict):

                dictionary_value_types = {}

                for key, dictionary_value in zip(
                    value.keys,
                    value.values
                ):

                    if not isinstance(key, ast.Constant):
                        continue

                    item_type = get_simple_type(dictionary_value)

                    if item_type is not None:
                        dictionary_value_types[key.value] = item_type

                known_dictionary_value_types[variable_name] = (
                    dictionary_value_types
                )

    # Check attributes and method calls.
    for node in ast.walk(tree):

        if not isinstance(node, ast.Attribute):
            continue

        object_type = None
        object_description = "object"

        # Case 1: name.append()
        # Example: name = "Aditya"; name.append("!")
        if isinstance(node.value, ast.Name):

            variable_name = node.value.id

            object_type = known_types.get(variable_name)
            object_description = f"'{variable_name}'"

        # Case 2: student["name"].append()
        # Example: student = {"name": "Aditya"}
        elif isinstance(node.value, ast.Subscript):

            container = node.value.value
            key_node = node.value.slice

            if (
                isinstance(container, ast.Name)
                and isinstance(key_node, ast.Constant)
            ):

                dictionary_name = container.id
                dictionary_key = key_node.value

                dictionary_types = known_dictionary_value_types.get(
                    dictionary_name,
                    {}
                )

                object_type = dictionary_types.get(dictionary_key)

                object_description = (
                    f"value at key {dictionary_key!r} "
                    f"in dictionary '{dictionary_name}'"
                )

        # Ignore expressions whose types are unknown.
        if object_type not in valid_attributes:
            continue

        # Report only attributes unavailable on this type.
        if node.attr not in valid_attributes[object_type]:

            add_finding(
                "Possible AttributeError",
                node.lineno,
                (
                    f"The {object_description} is a "
                    f"{object_type.__name__}, which does not have "
                    f"the attribute '{node.attr}'."
                ),
                (
                    f"The '{node.attr}' attribute or method is not "
                    f"available for objects of type "
                    f"{object_type.__name__}."
                ),
                (
                    "Check the object's data type and use a method "
                    "supported by that type. For example, use "
                    "list.append() to add an item to a list."
                )
            )
 

    # --------------------------------------------------
    # 9. Detect suspicious use of 'is' with literals
    # --------------------------------------------------

    for node in ast.walk(tree):

        if not isinstance(node, ast.Compare):
            continue

        for operator, comparator in zip(
            node.ops,
            node.comparators
        ):

            if not isinstance(operator, (ast.Is, ast.IsNot)):
                continue

            if isinstance(comparator, ast.Constant):

                add_finding(
                    "Possible ComparisonWarning",
                    node.lineno,
                    "The 'is' operator is being used with a literal.",
                    (
                        "'is' checks whether two references point "
                        "to the same object. It is not meant for "
                        "ordinary value comparisons."
                    ),
                    (
                        "Use '==' or '!=' when comparing values."
                    )
                )

    # --------------------------------------------------
    # 10. Create the final report
    # --------------------------------------------------

    return make_report(errors)


# ------------------------------------------------------
# Create report and remove duplicate findings
# ------------------------------------------------------

def make_report(errors):

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

    unique_errors.sort(key=lambda item: item["line"])

    error_names = {
        "SyntaxError",
        "IndentationError",
        "ZeroDivisionError",
        "Possible ZeroDivisionError",
        "Possible IndexError",
        "Possible KeyError",
        "Possible TypeError"
    }

    has_error = any(
        item["error_name"] in error_names
        for item in unique_errors
    )

    has_warning = any(
        item["error_name"].startswith("Possible")
        for item in unique_errors
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