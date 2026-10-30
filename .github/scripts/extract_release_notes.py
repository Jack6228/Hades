import os
import re
import sys
from pathlib import Path

def main():
    if len(sys.argv) < 2:
        print("Error: Tag name required as an argument.", file=sys.stderr)
        sys.exit(1)
        
    tag = sys.argv[1] # e.g., v0.8.4
    
    # 1. Anchor the path to the repository root
    repo_root = Path(os.environ.get("GITHUB_WORKSPACE", Path.cwd()))
    changelog_path = repo_root / "docs" / "reference" / "CHANGELOG.rst"
    
    # 2. Fallback check for case-sensitivity mismatches
    if not changelog_path.exists():
        alt_path = repo_root / "changelog.rst"
        if alt_path.exists():
            changelog_path = alt_path

    # 3. Read and parse the changelog
    if not changelog_path.exists():
        print(f"Warning: CHANGELOG.rst not found at {changelog_path}. Using fallback notes.", file=sys.stderr)
        notes = f"Release {tag}"
    else:
        content = changelog_path.read_text(encoding='utf-8')
        
        # Robust pattern matching:
        # - Matches the tag (e.g., v0.8.4)
        # - Allows optional spacing/dates on the same line
        # - Matches the RST underline (hyphens or equals signs)
        # - Captures everything until the next version header or end of file
        pattern = rf'{re.escape(tag)}.*?\n[-=]+\n(.*?)(?=\n(?:v?\d+\.\d+\.\d+).*?\n[-=]+\n|\Z)'
        match = re.search(pattern, content, re.DOTALL)
        
        notes = match.group(1).strip() if match else f"Release {tag}"

    # 4. Write out the markdown file for GitHub Releases
    output_path = repo_root / "RELEASE_NOTES.md"
    output_path.write_text(
        f"## What's Changed in {tag}\n\n"
        "Click here for full [Installation instructions](https://hades-obol.readthedocs.io/en/latest/overview/installation.html)\n\n"
        f"{notes}",
        encoding='utf-8',
    )
    print(f"Successfully generated release notes for {tag} at {output_path}")

if __name__ == "__main__":
    main()