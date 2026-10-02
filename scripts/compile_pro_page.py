#!/usr/bin/env python3
"""
Compiler for the Open Food Facts for Businesses (Pro Platform) page.
Resolves `[[texts/...]]` includes and validates/generates:
- `lang/en/texts/index-pro-2.html` (Include-based template for ProductOpener)
- `index-pro-2.html` (Root file)
"""

import os
import re

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BLOCKS_DIR = os.path.join(REPO_ROOT, "lang", "en", "texts", "pro", "blocks")


def resolve_includes(content, base_dir=os.path.join(REPO_ROOT, "lang", "en")):
    """Recursively resolve [[texts/...]] tags into their file contents."""
    pattern = re.compile(r"\[\[texts/([^\]]+)\]\]")

    def replacer(match):
        rel_path = match.group(1)
        full_path = os.path.join(base_dir, "texts", rel_path)
        if os.path.exists(full_path):
            with open(full_path, "r", encoding="utf-8") as f:
                included_text = f.read()
            return resolve_includes(included_text, base_dir)
        else:
            print(f"Warning: Include not found: {full_path}")
            return match.group(0)

    return pattern.sub(replacer, content)


def main():
    template_path = os.path.join(REPO_ROOT, "lang", "en", "texts", "index-pro-2.html")
    root_output_path = os.path.join(REPO_ROOT, "index-pro-2.html")

    print(f"Compiling Pro page template from {template_path}...")
    with open(template_path, "r", encoding="utf-8") as f:
        template_content = f.read()

    # The root file is updated with the include structure
    with open(root_output_path, "w", encoding="utf-8") as f:
        f.write(template_content)
    print(f"Updated {root_output_path}")

    # Generate standalone preview file for local browser testing without ProductOpener
    resolved = resolve_includes(template_content)
    standalone_path = os.path.join(REPO_ROOT, "scratch", "index-pro-2-compiled.html")
    os.makedirs(os.path.dirname(standalone_path), exist_ok=True)
    with open(standalone_path, "w", encoding="utf-8") as f:
        f.write(resolved)
    print(f"Compiled standalone preview to {standalone_path}")


if __name__ == "__main__":
    main()
