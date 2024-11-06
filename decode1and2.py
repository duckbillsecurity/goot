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
    # Pattern for extracting variable assignments
    var_pattern = re.compile(
        r"""(?:^([a-zA-Z0-9_]+)\s*=\s*['"](.*?)['"]\s*;)""",
        re.MULTILINE
    )

    # Pattern for detecting concatenations involving multiple variables
    concat_pattern = re.compile(
        r"""(?:^([a-zA-Z0-9_]+)\s*=\s*(?:[a-zA-Z0-9_]+\s*\+\s*)+[a-zA-Z0-9_]+;)""",
        re.MULTILINE
    )

    return var_pattern, concat_pattern

def convertConcatToString(concat_matches, var_dict):
    """
    Concatenates variables based on the obfuscated pattern. Joins multiple concatenated 
    strings by looking up variable values in `var_dict` and assembling them into one string.
    """
    decoded_text = ''

    for match in concat_matches:
        # Split on '=' to separate variable name from its concatenated values
        var_name, expression = match.split('=')
        var_name = var_name.strip()
        expression = expression.strip()
        
        # Resolve each variable in the expression using `var_dict`
        concatenated_value = ''
        for item in expression.split('+'):
            item = item.strip()
            concatenated_value += var_dict.get(item, '')

        # Update `var_dict` with the resolved value
        var_dict[var_name] = concatenated_value

    # The last resolved variable should contain the final decoded concatenated string
    return concatenated_value

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
    var_dict = {name: value for name, value in var_matches}

    # Step 2b: Find all concatenated lines that need to be resolved
    concat_matches = concat_pattern.findall(file_content)

    # Step 3: Concatenate variables to form a partially decoded text
    concatenated_text = convertConcatToString(concat_matches, var_dict)

    # Save concatenated output to a file
    with open('Round1Decoded.js_', 'w') as f:
        f.write(concatenated_text)

    # Step 4: First round of decoding
    round1_result = decodeString(concatenated_text)

    # Save the first decoded output
    with open('Round2Decoded.js_', 'w') as f:
        f.write(round1_result)

    # Step 5: Second round of decoding
    round2_result = decodeString(round1_result)

    # Save the final decoded output
    with open('FinalDecoded.js_', 'w') as f:
        f.write(round2_result)

    print("Decoding complete. Outputs saved as 'Round1Decoded.js_', 'Round2Decoded.js_', and 'FinalDecoded.js_'.")

# Run the decoding process
gootDecode(args.jsFilePath)
