import streamlit as st
import numpy as np
import random
import pandas as pd

def split_into_hamming_blocks(input_string):
    """Split 128-bit string into 16 blocks of 8-bit Hamming codes"""
    return [input_string[i:i+8] for i in range(0, 128, 8)]

def calculate_parity_bits(data):
    # Calculate parity bits for positions 1, 2, and 4
    p1 = (data[2] + data[4] + data[6]) % 2
    p2 = (data[2] + data[5] + data[6]) % 2
    p4 = (data[4] + data[5] + data[6]) % 2
    return p1, p2, p4

def find_error_position(received_code):
    # Calculate syndrome bits
    s1 = (received_code[0] + received_code[2] + received_code[4] + received_code[6]) % 2
    s2 = (received_code[1] + received_code[2] + received_code[5] + received_code[6]) % 2
    s3 = (received_code[3] + received_code[4] + received_code[5] + received_code[6]) % 2
    
    # Convert syndrome to decimal to get error position
    error_pos = s1 + (s2 * 2) + (s3 * 4)
    return error_pos

def correct_error(received_code, error_pos):
    if error_pos == 0:
        return received_code
    
    # Flip the bit at error position
    corrected_code = received_code.copy()
    corrected_code[error_pos - 1] = 1 - corrected_code[error_pos - 1]
    return corrected_code

def process_hamming_block(block, error_position):
    """Process a single 8-bit Hamming code block"""
    original_block = np.array([int(bit) for bit in block])
    
    # Introduce error
    received_block = original_block.copy()
    received_block[error_position - 1] = 1 - received_block[error_position - 1]
    
    # Find and correct error
    error_pos = find_error_position(received_block[:7])  # Only check the first 7 bits for Hamming (7,4)
    
    # Correct the error if it's in the first 7 bits
    corrected_block = correct_error(received_block[:7], error_pos)
    
    # Handle the 8th bit separately
    if error_position == 8:
        # Flip the 8th bit if it was errored
        corrected_block = np.append(corrected_block, 1 - received_block[7])
    else:
        corrected_block = np.append(corrected_block, received_block[7])
    
    return original_block, received_block, corrected_block

st.title("128-bit Hamming Code Error Detection and Correction")

# Input the 128-bit code
st.subheader("Enter 128-bit Code")
code_input = st.text_input("Enter 128 bits (0s and 1s):","")

if st.button("Process Code"):
    if not code_input:
        st.error("Please enter the 128-bit code")
    elif len(code_input) != 128 or not all(bit in '01' for bit in code_input):
        st.error("Please enter exactly 128 bits (0s and 1s)")
    else:
        # Split into blocks
        blocks = split_into_hamming_blocks(code_input)
        
        # Generate random error positions for each block
        error_positions = [random.randint(1, 8) for _ in range(16)]
        
        # Process each block and store results
        results = []
        all_original = []
        all_received = []
        all_corrected = []
        
        for i, (block, error_pos) in enumerate(zip(blocks, error_positions)):
            original, received, corrected = process_hamming_block(block, error_pos)
            
            all_original.extend(original)
            all_received.extend(received)
            all_corrected.extend(corrected)
            
            # Append results for the table
            results.append({
                "Block No": i + 1,
                "Original": ''.join(map(str, original)),
                "Error Bit Position": error_pos,
                "Corrected": ''.join(map(str, corrected))
            })
        
        # Display results in a table
        st.subheader("Block-wise Results")
        results_df = pd.DataFrame(results)
        st.table(results_df)
        
        # Compare final results
        original_string = ''.join(map(str, all_original))
        corrected_string = ''.join(map(str, all_corrected))
        
        st.subheader("Final Results")
        st.write("Original 128-bit code:", original_string)
        st.write("Corrected 128-bit code:", corrected_string)
        
        if original_string == corrected_string:
            st.success("All errors successfully corrected! Final code matches original.")
        else:
            st.error("Error correction failed! Final code does not match original.")
            
        # Display error statistics
        successful_corrections = sum(1 for orig, corr in zip(all_original, all_corrected) if orig == corr)
        st.write(f"Successfully corrected {successful_corrections} out of 128 bits")