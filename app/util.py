import json

def format_duns(duns) -> tuple[bool, str]:
    """Format DUNS number to XX-XXX-XXXX format if possible."""
    if isinstance(duns, int):                   # Duns was entered as an integer without hyphens
        if duns < 0:
            return (False, duns)
        as_str = str(duns)
    elif isinstance(duns, str):                 # Duns was entered as a string with hyphens
        as_str = duns.replace("-", "")

    return (True, f"{as_str[:2]}-{as_str[2:5]}-{as_str[5:]}")


def validate_duns_format(duns: str) -> bool:    # Validate DUNS number format, pass formatted DUNS
    """Validate the format of a DUNS number."""
    if len(duns) != 11:                         # DUNS is improperly formatted
        return False
    if not duns.replace("-", "").isdigit():     # DUNS contains non-digit characters
        return False
    return True

def load_key(file_path: str) -> str:
    """Load a key from a file."""
    try:
        with open(file_path, 'r') as file:
            data = file.read().strip()
        if file_path.endswith('.json'):
            return (True, json.loads(data))  # Return JSON data as a dictionary
        else:
            return (True, data)
    except FileNotFoundError:
        with open(file_path, 'w') as file:
            file.write("#Replace with your key")
        return (False, f"File not found: {file_path}")
    except Exception as e:
        return (False, f"Error reading file: {file_path}, Error: {str(e)}")