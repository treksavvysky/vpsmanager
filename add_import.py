import re
import sys

def add_import_to_file(filename, module_name, item_to_import):
    """
    Adds an item to import from a specified module in a Python file, if the module is already imported and the item is not.
    
    Parameters:
    - filename: The name of the file to modify.
    - module_name: The name of the module from which to import.
    - item_to_import: The item to import from the module.
    """
    try:
        with open(filename, 'r+') as file:
            lines = file.readlines()
            file.seek(0)  # Go back to the start of the file
            import_added = False
            
            for line in lines:
                if re.match(f'from {module_name} import', line):
                    # Check if the item is already imported
                    if item_to_import in line:
                        print(f"{item_to_import} is already imported from {module_name}.")
                    else:
                        # Add the item to the import statement
                        line = line.rstrip('\n') + f', {item_to_import}\n'
                        import_added = True
                    file.write(line)
                else:
                    file.write(line)
            
            if not import_added:
                print(f"No import statement for {module_name} found or {item_to_import} is already included.")
    
    except FileNotFoundError:
        print(f"The file {filename} does not exist.")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 add_import.py <filename> <module_name> <item_to_import>")
    else:
        filename = sys.argv[1]
        module_name = sys.argv[2]
        item_to_import = sys.argv[3]
        add_import_to_file(filename, module_name, item_to_import)
