#!/usr/bin/env python3
import os
import re
import shutil

def is_svg_animated(path):
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as fp:
            content = fp.read()
            return ('@keyframes' in content or '<animate' in content or 'animation:' in content or 'animation-name' in content)
    except:
        return False

def get_normalized_name(f, full_path):
    name, ext = os.path.splitext(f)
    if ext.lower() != '.svg':
        return f
    
    if 'copie' in name.lower():
        return '__DELETE__'
        
    animated = is_svg_animated(full_path)
    s = name
    
    # Special case: animated-puzzle (1).svg -> puzzle-animated.svg
    if 'animated-puzzle' in s.lower() and '1' in s:
        return 'puzzle-animated.svg'

    # Remove Illustrations - or Illustration - or Illustrations or Illustration
    s = re.sub(r'(?i)\billustrations?\s*-\s*', '', s)
    s = re.sub(r'(?i)\billustrations?\b', '', s)
    
    # Strip any existing animated prefix or suffix
    s = re.sub(r'(?i)^animated-', '', s)
    s = re.sub(r'(?i)-animated$', '', s)
    
    # Replace (1), (2) etc. with -1, -2
    s = re.sub(r'\s*\(([0-9]+)\)\s*', r'-\1', s)
    
    # Replace + with -plus
    s = s.replace('+', '-plus')
    
    # Replace spaces and underscores with hyphens
    s = re.sub(r'[\s_]+', '-', s)
    
    # Remove any other non-alphanumeric except hyphen
    s = re.sub(r'[^a-zA-Z0-9-]', '', s)
    
    # Clean multiple hyphens
    s = re.sub(r'-+', '-', s).strip('-').lower()
    
    if animated:
        s = s + '-animated'
        
    return s + '.svg'

def normalize_repository(base_dir):
    print(f"\n==========================================")
    print(f"Normalizing SVGs in: {base_dir}")
    print(f"==========================================")
    
    mapping = {}
    deletes = []
    
    # First pass: identify changes
    for root, dirs, files in os.walk(base_dir):
        for f in sorted(files):
            if f.endswith('.svg'):
                old_p = os.path.join(root, f)
                norm_name = get_normalized_name(f, old_p)
                if norm_name == '__DELETE__':
                    deletes.append(old_p)
                elif norm_name != f:
                    new_p = os.path.join(root, norm_name)
                    mapping[old_p] = new_p

    # Perform deletes
    for p in deletes:
        print(f"DELETING DUPLICATE: {p}")
        if os.path.exists(p):
            os.remove(p)

    # Perform renames safely for case-insensitive filesystems (macOS APFS)
    for old_p, new_p in mapping.items():
        if not os.path.exists(old_p):
            continue
            
        old_dir, old_file = os.path.split(old_p)
        new_dir, new_file = os.path.split(new_p)
        
        # If destination file already exists and is a distinct file (not just a case-variant of old_file)
        if os.path.exists(new_p) and old_file.lower() != new_file.lower():
            print(f"Target already exists, replacing: {old_file} -> {new_file}")
            os.remove(new_p)
            
        print(f"RENAMING: {old_file} -> {new_file}")
        
        if old_file.lower() == new_file.lower():
            # Two-step rename for case-only changes
            tmp_p = os.path.join(old_dir, f"__tmp_{new_file}")
            os.rename(old_p, tmp_p)
            os.rename(tmp_p, new_p)
        else:
            os.rename(old_p, new_p)
        
    print(f"Done: {len(mapping)} renamed, {len(deletes)} deleted.")
    return mapping

if __name__ == '__main__':
    design_dir = '/Users/pierre/development/openfoodfacts-design/images'
    web_dir = '/Users/pierre/development/openfoodfacts-web/html/images/illustrations'
    
    m1 = normalize_repository(design_dir)
    m2 = normalize_repository(web_dir)
