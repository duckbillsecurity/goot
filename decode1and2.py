#!/usr/bin/env python

import argparse
import re

# Argument parsing
parser = argparse.ArgumentParser()
parser.add_argument('jsFilePath', help='Path to the GootLoader JS file.')
args = parser.parse_args()

def getVariableAndConcatPatterns():
    """
    Returns the regular expression patterns to find variables and concatenated lines.
    These patterns are tailored to GootLoader Variant 2.1 and higher.
    """
    # Pattern for extracting variable assignments (e.g., var_name = 'value';)
    var_pattern = re.compile(
        r"""^([a-zA-Z0-9_]+)\s*=\s*['"](.*?)['"]\s*;""",
        re.MULTILINE
    )

    # Pattern for detecting concatenations involving multiple variables (e.g., var_name = var1 + var2 + ...;)
    concat_pattern = re.compile(
        r"""^([a-zA-Z0-9_]+)\s*=\s*(?:[a-zA-Z0-9_]+\s*\+\s*)+[a-zA-Z0-9_]+\s*;""",
        re.MULTILINE
    )

    return var_pattern, concat_pattern

def ConvertVarsToDict(var_matches):
    """
    Converts matched variables into a dictionary where each key is a variable name
    and the value is the assigned string. Only valid matches are processed.
    """
    var_dict = {}
    for var_name, value in var_matches:
        # Ensure both var_name and value are present
        if var_name and value:
            var_dict[var_name] = value
            print(f"Variable added to dictionary: {var_name} = {value}")
    return var_dict

def convertConcatToString(concat_matches, var_dict):
    """
    Concatenates variables based on the obfuscated pattern. Joins multiple concatenated 
    strings by looking up variable values in `var_dict` and assembling them into one string.
    """
    concatenated_result = ''  # Initialize to avoid UnboundLocalError

    for match in concat_matches:
        # Attempt to split on '=' to separate variable name from its concatenated values
        if '=' not in match:
            print(f"Skipping unexpected match format: {match}")
            continue

        try:
            var_name, expression = match.split('=')
            var_name = var_name.strip()
            expression = expression.strip()

            # Resolve each variable in the expression using `var_dict`
            current_concat = ''
            for item in expression.split('+'):
                item = item.strip()
                # Look up each variable in `var_dict`, skip if not found
                if item in var_dict:
                    current_concat += var_dict[item]
                else:
                    print(f"Warning: {item} not found in variable dictionary")

            # Update `var_dict` with the resolved value if it's not empty
            if current_concat:
                var_dict[var_name] = current_concat
                concatenated_result = current_concat
                print(f"Concatenated variable: {var_name} = {current_concat}")
        except ValueError:
            print(f"Error processing match: {match}")
            continue

    return concatenated_result

def decodeString(encoded_text):
    """
    Decodes the text by rearranging characters in an alternating order, as per
    GootLoader's specific decoding technique.
    """
    decoded_result = ''
    for i, char in enumerate(encoded_text):
        # Odd-index characters are added to the end, even-index to the beginning
        decoded_result = char + decoded_result if i % 2 == 0 else decoded_result + char
    return decoded_result

def gootDecode(file_path):
    """
    Reads the input file, extracts variable patterns, performs concatenation, and
    decodes the obfuscated text in two rounds.
    """
    # Step 1: Open and read the malicious JavaScript file
    with open(file_path, 'r', encoding='utf-8') as file:
        file_content = file.read()

    # Step 2: Extract variables and concatenations
    var_pattern, concat_pattern = getVariableAndConcatPatterns()

    # Step 2a: Find all variable assignments and store them in a dictionary
    var_matches = var_pattern.findall(file_content)
    var_dict = ConvertVarsToDict(var_matches)

    # Step 2b: Find all concatenated lines that need to be resolved
    concat_matches = concat_pattern.findall(file_content)
    if not concat_matches:
        print("No concatenation patterns found.")
    
    # Step 3: Concatenate variables to form a partially decoded text
    concatenated_text = convertConcatToString(concat_matches, var_dict)
    if concatenated_text:
        print("Concatenation successful.")
    else:
        print("Concatenation resulted in empty output.")

    # Save concatenated output to a file
    with open('Round1Decoded.js_', 'w') as f:
        f.write(concatenated_text)

    # Step 4: First round of decoding
    round1_result = decodeString(concatenated_text)
    if round1_result:
        print("First round of decoding successful.")
    else:
        print("First round of decoding resulted in empty output.")

    # Save the first decoded output
    with open('Round2Decoded.js_', 'w') as f:
        f.write(round1_result)

    # Step 5: Second round of decoding on the result from the first round
    round2_result = decodeString(round1_result)
    if round2_result:
        print("Second round of decoding successful.")
    else:
        print("Second round of decoding resulted in empty output.")

    # Save the final decoded output
    with open('FinalDecoded.js_', 'w') as f:
        f.write(round2_result)

    print("Decoding complete. Outputs saved as 'Round1Decoded.js_', 'Round2Decoded.js_', and 'FinalDecoded.js_'.")

# Run the decoding process
gootDecode(args.jsFilePath)
