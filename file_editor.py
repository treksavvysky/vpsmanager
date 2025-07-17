class FileEditor:
    @staticmethod
    def append_text_to_file(file_path, text):
        """
        Appends given text to the end of the file specified by file_path.
        
        :param file_path: Path to the file to append the text to.
        :param text: Text to be appended.
        """
        with open(file_path, 'a') as file:
            file.write(text + '\n')

    @staticmethod
    def replace_phrase_in_file(file_path, target_phrase, replacement_phrase):
        """
        Replaces all instances of target_phrase with replacement_phrase in the file specified by file_path.
        
        :param file_path: Path to the file where the replacement should occur.
        :param target_phrase: The phrase to be replaced.
        :param replacement_phrase: The phrase to replace with.
        """
        with open(file_path, 'r') as file:
            file_contents = file.read()
        
        file_contents = file_contents.replace(target_phrase, replacement_phrase)
        
        with open(file_path, 'w') as file:
            file.write(file_contents)

    @staticmethod
    def replace_line_in_file(file_path, target_phrase, new_line):
        """
        Replaces an entire line containing the target_phrase with new_line in the file specified by file_path.
        
        :param file_path: Path to the file where the replacement should occur.
        :param target_phrase: The phrase that identifies the line to be replaced.
        :param new_line: The new line that will replace the old line.
        """
        with open(file_path, 'r') as file:
            lines = file.readlines()
        
        with open(file_path, 'w') as file:
            for line in lines:
                if target_phrase in line:
                    file.write(new_line + '\n')
                else:
                    file.write(line)

    @staticmethod
    def add_text_to_end_of_line(file_path, target_phrase, text_to_add):
        """
        Adds text to the end of lines containing the target_phrase in the file specified by file_path.
        
        :param file_path: Path to the file where the text should be added.
        :param target_phrase: The phrase that identifies the lines to be modified.
        :param text_to_add: The text to add to the end of the identified lines.
        """
        with open(file_path, 'r') as file:
            lines = file.readlines()
        
        with open(file_path, 'w') as file:
            for line in lines:
                if target_phrase in line:
                    file.write(line.strip() + ' ' + text_to_add + '\n')
                else:
                    file.write(line)

import sys

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python file_editor.py <operation> [arguments]...\n")
        print("Operations:\n")
        print("  append-text <file_path> <text> - Append text to a file")
        print("  replace-phrase <file_path> <target_phrase> <replacement_phrase> - Replace a phrase in a file")
        print("  replace-line <file_path> <target_phrase> <new_line> - Replace an entire line in a file")
        print("  add-text-to-end-of-line <file_path> <target_phrase> <text_to_add> - Add text to the end of a line in a file")
        sys.exit(1)

    operation = sys.argv[1]
    args = sys.argv[2:]

    operations = {
        'append-text': FileEditor.append_text_to_file,
        'replace-phrase': FileEditor.replace_phrase_in_file,
        'replace-line': FileEditor.replace_line_in_file,
        'add-text-to-end-of-line': FileEditor.add_text_to_end_of_line,
    }

    if operation in operations:
        operations[operation](*args)
    else:
        print(f"Unknown operation: {operation}")