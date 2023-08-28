from bs4 import BeautifulSoup
import glob
import os
import sys

def extract_includes(file_path):
    includes = set()
    with open(file_path, 'r') as f:
        soup = BeautifulSoup(f, 'html.parser')
        includes_elements = soup.find_all(string=lambda text: '[[texts/' in text)
        for include in includes_elements:
            includes.add(include.strip())
    return includes

def main():
    # Get list of English HTML files
    en_files = glob.glob('lang/en/texts/**/*.html', recursive=True)
    
    all_good = True

    # Get list of all language directories
    lang_dirs = glob.glob('lang/*/')

    for en_file_path in en_files:
        # Extract the original includes from the English version
        original_includes = extract_includes(en_file_path)

        for lang_dir in lang_dirs:
            lang = os.path.basename(os.path.normpath(lang_dir))

            # Skip the English directory
            if lang == 'en':
                continue
            
            # Generate the corresponding path for the translated version
            translated_file_path = en_file_path.replace('lang/en/', f'lang/{lang}/')
            
            # Skip if the translated file does not exist
            if not os.path.exists(translated_file_path):
                print(f"Warning: Translated file does not exist for language '{lang}' - {translated_file_path}")
                continue

            # Extract includes from the translated version
            translated_includes = extract_includes(translated_file_path)
            
            # Check if original includes are preserved in the translated version
            for original_include in original_includes:
                if original_include not in translated_includes:
                    print(f"Error: Missing include in language '{lang}', file {translated_file_path}: {original_include}")
                    all_good = False

    if not all_good:
        print("Error: Missing includes found in one or more files across languages.")
        sys.exit(1)

if __name__ == "__main__":
    main()
