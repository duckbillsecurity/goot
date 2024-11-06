#!/usr/bin/env python

import argparse
import re
import sys

def get_arguments():
    parser = argparse.ArgumentParser(description='Decode recent GootLoader JavaScript files.')
    parser.add_argument('jsFilePath', help='Path to the GootLoader JavaScript file.')
    return parser.parse_args()

def read_file(file_path):
    try:
        with open(file_path, mode="r", encoding="utf-8") as file:
            return file.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

def detect_variant(file_content):
    # Check for GootLoader variant indicators
    if 'GOOT3' in file_content[:1000]:
        print("Detected GootLoader Variant 3")
        return 3
    elif re.search(r'jQuery JavaScript Library v\d+\.\d+\.\d+', file_content[:1000]):
        print("Detected GootLoader Variant 2")
        return 2
    else:
        print("Detected GootLoader Variant 2.1 or higher")
        return 2.1

def extract_variables(file_content):
    # Regex pattern to match variable assignments
    var_pattern = re.compile(r"^([a-zA-Z0-9_]+)\s*=\s*['\"](.*?)['\"]\s*;", re.MULTILINE)
    variables = dict(var_pattern.findall(file_content))
    print(f"Extracted {len(variables)} variables.")
    return variables

def extract_concatenations(file_content):
    # Regex pattern to match concatenation assignments
    concat_pattern = re.compile(r"^([a-zA-Z0-9_]+)\s*=\s*(.+);", re.MULTILINE)
    concatenations = concat_pattern.findall(file_content)
    return concatenations

def resolve_concatenations(concatenations, variables):
    resolved_vars = variables.copy()
    for var_name, expression in concatenations:
        # Skip if already resolved
        if var_name in resolved_vars:
            continue
        # Replace variable names with their values
        for key in variables.keys():
            expression = expression.replace(key, f"'{variables[key]}'")
        try:
            # Evaluate the expression safely
            resolved_value = eval(expression)
            resolved_vars[var_name] = resolved_value
        except Exception as e:
            print(f"Error resolving {var_name}: {e}")
            continue
    return resolved_vars

def decode_string(encoded_text):
    # GootLoader decoding algorithm
    decoded_result = ''
    for i, char in enumerate(encoded_text):
        if i % 2 == 0:
            decoded_result = char + decoded_result
        else:
            decoded_result = decoded_result + char
    return decoded_result

def main():
    args = get_arguments()
    file_content = read_file(args.jsFilePath)
    variant = detect_variant(file_content)
    
    # Extract variables and concatenations
    variables = extract_variables(file_content)
    concatenations = extract_concatenations(file_content)
    
    # Resolve concatenations
    resolved_vars = resolve_concatenations(concatenations, variables)
    
    # Find the main obfuscated code variable
    main_var_name = None
    max_length = 0
    for var in resolved_vars:
        if len(resolved_vars[var]) > max_length:
            main_var_name = var
            max_length = len(resolved_vars[var])
    if not main_var_name:
        print("Main obfuscated code variable not found.")
        sys.exit(1)
    
    obfuscated_code = resolved_vars[main_var_name]
    print(f"Decoding variable: {main_var_name}")
    
    # First round of decoding
    decoded_round1 = decode_string(obfuscated_code)
    
    # Extract the inner code from quotes
    inner_code_match = re.search(r"['\"](.*)['\"]", decoded_round1)
    if not inner_code_match:
        print("Failed to extract inner code from first decoding round.")
        sys.exit(1)
    inner_code = inner_code_match.group(1)
    
    # Second round of decoding
    decoded_round2 = decode_string(bytes(inner_code, "utf-8").decode("unicode_escape"))
    
    # Output the fully decoded script
    output_file = "DecodedGootLoader.js"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(decoded_round2)
    print(f"Decoding complete. Decoded script saved to {output_file}")

if __name__ == "__main__":
    main()
