import tkinter as tk
from tkinter import filedialog, messagebox
import json
import re
import os

def parse_document_to_json(file_path):
    """
    Parse the structured document and convert to JSON format for ML fine-tuning.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split into acts
    acts = re.split(r'ACT INDEX:\s*(\d+)', content)
    
    all_data = []
    
    for i in range(1, len(acts), 2):
        if i + 1 >= len(acts):
            break
            
        act_index = acts[i].strip()
        act_content = acts[i + 1]
        
        # Extract act metadata
        act_title = ""
        act_no = ""
        act_year = ""
        
        title_match = re.search(r'ACT TITLE:\s*(.+?)(?:\n|$)', act_content)
        no_match = re.search(r'ACT NO:\s*(.+?)(?:\n|$)', act_content)
        year_match = re.search(r'ACT YEAR:\s*(.+?)(?:\n|$)', act_content)
        
        if title_match:
            act_title = title_match.group(1).strip()
        if no_match:
            act_no = no_match.group(1).strip()
        if year_match:
            act_year = year_match.group(1).strip()
        
        # Extract sections and Q&A pairs
        section_pattern = r'Section\s+(\d+[A-Za-z]*)'
        sections = re.split(section_pattern, act_content)
        
        for j in range(1, len(sections), 2):
            if j + 1 >= len(sections):
                break
                
            section_num = sections[j].strip()
            section_content = sections[j + 1]
            
            # Extract Q&A pairs
            qa_pattern = r'Q(\d+):\s*(.*?)\nA:\s*(.*?)\s*Type:\s*(.+?)(?=\nQ\d+:|$)'
            qa_matches = re.findall(qa_pattern, section_content, re.DOTALL)
            
            for q_num, question, answer, qa_type in qa_matches:
                data_entry = {
                    "act_index": act_index,
                    "act_title": act_title,
                    "act_no": act_no,
                    "act_year": act_year,
                    "section": section_num,
                    "question_number": q_num.strip(),
                    "question": question.strip(),
                    "answer": answer.strip(),
                    "type": qa_type.strip()
                }
                all_data.append(data_entry)
    
    return all_data


def create_jsonl_format(data):
    """
    Convert data to JSONL format for fine-tuning (OpenAI/Anthropic style).
    """
    jsonl_lines = []
    for entry in data:
        jsonl_entry = {
            "messages": [
                {
                    "role": "user",
                    "content": entry["question"]
                },
                {
                    "role": "assistant",
                    "content": entry["answer"]
                }
            ],
            "metadata": {
                "act_title": entry["act_title"],
                "section": entry["section"],
                "type": entry["type"]
            }
        }
        jsonl_lines.append(json.dumps(jsonl_entry, ensure_ascii=False))
    
    return '\n'.join(jsonl_lines)


def convert_txt_to_json():
    """
    Main function with GUI file selection for converting TXT to JSON.
    """
    # Create root window (hidden)
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    
    # Ask user to select input .txt file
    print("Please select a .txt file to convert to JSON...")
    input_file = filedialog.askopenfilename(
        title="Select TXT file to convert",
        filetypes=[
            ("Text Files", "*.txt"),
            ("All Files", "*.*")
        ]
    )
    
    if not input_file:
        print("No file selected. Exiting...")
        root.destroy()
        return
    
    print(f"Selected file: {input_file}")
    
    try:
        # Parse the document
        print("Parsing document...")
        data = parse_document_to_json(input_file)
        
        if not data:
            raise ValueError("No Q&A pairs found in the document.")
        
        print(f"Found {len(data)} Q&A pairs")
        
        # Ask user for output format
        format_choice = messagebox.askyesnocancel(
            "Choose Format",
            "Select output format:\n\n"
            "YES = JSONL (for fine-tuning)\n"
            "NO = Standard JSON\n"
            "CANCEL = Exit"
        )
        
        if format_choice is None:
            print("Conversion cancelled.")
            root.destroy()
            return
        
        # Prepare default filename
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        
        if format_choice:  # JSONL format
            default_name = base_name + ".jsonl"
            file_types = [("JSONL Files", "*.jsonl"), ("All Files", "*.*")]
            output_content = create_jsonl_format(data)
        else:  # Standard JSON format
            default_name = base_name + ".json"
            file_types = [("JSON Files", "*.json"), ("All Files", "*.*")]
            output_content = json.dumps(data, indent=2, ensure_ascii=False)
        
        # Ask user where to save the file
        print("Please choose where to save the output file...")
        output_file = filedialog.asksaveasfilename(
            title="Save JSON file as",
            defaultextension=".jsonl" if format_choice else ".json",
            initialfile=default_name,
            filetypes=file_types
        )
        
        if not output_file:
            print("No output file selected. Exiting...")
            root.destroy()
            return
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output_content)
        
        print(f"\n✓ Conversion successful!")
        print(f"  Input:  {input_file}")
        print(f"  Output: {output_file}")
        print(f"  Format: {'JSONL' if format_choice else 'JSON'}")
        print(f"  Entries: {len(data)}")
        
        # Show success message
        messagebox.showinfo(
            "Success",
            f"Conversion successful!\n\n"
            f"Format: {'JSONL' if format_choice else 'JSON'}\n"
            f"Entries: {len(data)}\n\n"
            f"Saved to:\n{output_file}"
        )
        
    except Exception as e:
        error_msg = f"Error converting file: {str(e)}"
        print(f"\n✗ {error_msg}")
        messagebox.showerror("Error", error_msg)
    
    finally:
        root.destroy()


if __name__ == "__main__":
    print("=" * 60)
    print("TXT to JSON/JSONL Converter for ML Fine-tuning")
    print("=" * 60)
    convert_txt_to_json()