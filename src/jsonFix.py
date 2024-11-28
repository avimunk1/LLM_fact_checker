import json
import re

def fix_json(json_content):
    """
    Attempt to fix common JSON formatting issues in a given string.
    """
    try:
        # Remove all single quotes
        json_content = json_content.replace("'", "")
        
        # Handle triple quotes - normalize whitespace while preserving single spaces between words
        json_content = re.sub(r'"""[\s\S]*?"""', 
            lambda m: '"' + ' '.join(
                filter(None, m.group(0)
                    .replace('"""', '')
                    .replace('"', '')
                    .replace('\n', ' ')
                    .split(' ')
                )
            ) + '"', 
            json_content)
        
        # Fix double quotes at the end of lines
        json_content = json_content.replace('."",', '.",')
        
        # Parse and dump the JSON to validate and clean up
        data = json.loads(json_content)
        return json.dumps(data, indent=2)
    except json.JSONDecodeError as e:
        # Print debugging information
        print(f"\nError position: {e.pos}")
        print(f"Line number: {e.lineno}")
        print(f"Column: {e.colno}")
        
        # Show the problematic section
        start = max(0, e.pos - 100)
        end = min(len(json_content), e.pos + 100)
        print("\nProblematic section:")
        print(json_content[start:end])
        print("\n" + " " * (100) + "^")  # Point to the error position
        
        return f"JSON fixing error: {e}"

# Read the file content
input_path = "/Users/avimunk/Curserprojects/Mapp_utils/files/queryResults.json"
try:
    with open(input_path, "r", encoding="utf-8") as file:
        content = file.read()
        print(f"File size: {len(content)} characters")
except Exception as e:
    print(f"Error reading file: {e}")
    exit(1)

# Apply the fix
fixed_content = fix_json(content)

# Save the corrected content to a new file if fixed successfully
output_path = "/Users/avimunk/Curserprojects/Mapp_utils/files/fixed.json"
if "JSON fixing error" not in fixed_content:
    with open(output_path, "w", encoding="utf-8") as corrected_file:
        corrected_file.write(fixed_content)
    print(f"Successfully created: {output_path}")
else:
    print(fixed_content)
