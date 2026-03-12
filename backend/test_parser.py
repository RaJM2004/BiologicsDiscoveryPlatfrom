from app.utils.file_parsers import parse_molecules
import sys

if __name__ == "__main__":
    file_path = "temp_uploads/JSON.json_1773221821.json"
    print(f"Parsing {file_path}")
    molecules = parse_molecules(file_path)
    print(f"Found {len(molecules)} molecules")
    if molecules:
        print("First 3 molecules:")
        for m in molecules[:3]:
            print(m)
