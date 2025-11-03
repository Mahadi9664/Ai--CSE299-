import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import re
import os

def parse_and_split_acts(input_file, output_folder_name):
    """Parse the input file and split into individual act files"""
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split by the act separator pattern
        acts = re.split(r'={80}\nACT INDEX:', content)
        
        # Get the header (instructions part)
        header = acts[0]
        
        # Process each act (skip first element which is the header)
        output_dir = os.path.join(os.path.dirname(input_file), output_folder_name)
        os.makedirs(output_dir, exist_ok=True)
        
        act_count = 0
        
        for i, act in enumerate(acts[1:], start=0):
            # Re-add the separator that was removed during split
            act_content = f"ACT INDEX:{act}"
            
            # Extract act details for filename
            act_index_match = re.search(r'ACT INDEX:\s*(\d+)', act_content)
            act_title_match = re.search(r'ACT TITLE:\s*(.+?)(?:\n|$)', act_content)
            act_year_match = re.search(r'ACT YEAR:\s*(\d+)', act_content)
            
            if act_index_match and act_title_match and act_year_match:
                act_idx = act_index_match.group(1).zfill(3)
                act_title = act_title_match.group(1).strip()
                act_year = act_year_match.group(1)
                
                # Clean title for filename
                safe_title = re.sub(r'[^\w\s-]', '', act_title)
                safe_title = re.sub(r'\s+', '_', safe_title)[:50]
                
                filename = f"Act_{act_idx}_{act_year}_{safe_title}.txt"
                filepath = os.path.join(output_dir, filename)
                
                # Write act to file
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write('='*80 + '\n')
                    f.write(act_content)
                    f.write('='*80 + '\n')
                
                act_count += 1
        
        return act_count, output_dir
    
    except Exception as e:
        raise Exception(f"Error processing file: {str(e)}")

def select_file():
    """Open file dialog and process the selected file"""
    root = tk.Tk()
    root.withdraw()
    
    # First, select the input file
    file_path = filedialog.askopenfilename(
        title="Select the Acts Document",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )
    
    if file_path:
        # Ask for output folder name
        folder_name = simpledialog.askstring(
            "Output Folder Name",
            "Enter the name for the output folder:",
            initialvalue="split_acts"
        )
        
        if folder_name:
            # Remove invalid characters from folder name
            folder_name = re.sub(r'[<>:"/\\|?*]', '', folder_name)
            if not folder_name:
                folder_name = "split_acts"
            
            try:
                count, output_dir = parse_and_split_acts(file_path, folder_name)
                messagebox.showinfo(
                    "Success",
                    f"Successfully split {count} acts into separate files!\n\n"
                    f"Output directory:\n{output_dir}"
                )
            except Exception as e:
                messagebox.showerror("Error", str(e))
        else:
            messagebox.showinfo("Cancelled", "No folder name provided")
    else:
        messagebox.showinfo("Cancelled", "No file selected")

if __name__ == "__main__":
    print("Act Document Splitter")
    print("="*50)
    print("\nThis script will split a document containing multiple acts")
    print("into separate text files, one for each act.")
    print("\nClick OK to select your input file...")
    
    select_file()
    
    print("\nProcess completed!")