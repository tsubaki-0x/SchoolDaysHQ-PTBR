import os
import xml.etree.ElementTree as ET
from difflib import SequenceMatcher

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ORIGINAL = os.path.join(BASE, "ORIGINAL", "Script", "ENGLISH")
XML_DIR = os.path.join(BASE, "XML")

TARGETS = [
    ("02", "02-2K-R00.ENG.ORS"),
    ("05", "05-KC-F00.ENG.ORS"),
]

def read_ors(path):
    items = []
    with open(path, "r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            if "[PrintText]=" not in line:
                continue
            payload = line.split("[PrintText]=", 1)[1].rstrip("\r\n")
            if payload.endswith(";"):
                payload = payload[:-1]
            parts = payload.split("\t")
            if len(parts) >= 4:
                items.append({
                    "line": lineno,
                    "name": parts[1].strip(),
                    "text": parts[2].strip(),
                })
    return items

def read_xml(xml_path, filename):
    root = ET.parse(xml_path).getroot()
    for fe in root.findall(".//File"):
        if fe.get("name") == filename:
            return [
                {"name": el.get("name") or "", "text": el.text or ""}
                for el in fe.findall("./PrintText")
            ]
    raise RuntimeError(f"Arquivo {filename} nao encontrado em {xml_path}")

def show_window(title, seq, start, end, is_ors=False):
    print(title)
    lo = max(0, start - 3)
    hi = min(len(seq), end + 3)
    for i in range(lo, hi):
        mark = ">>" if start <= i < end else "  "
        extra = f" [linha ORS {seq[i]['line']}]" if is_ors else ""
        print(f"{mark} #{i+1:03d} {seq[i]['name']}: {seq[i]['text']}{extra}")

for folder, filename in TARGETS:
    ors_path = os.path.join(ORIGINAL, folder, filename)
    xml_path = os.path.join(XML_DIR, folder + ".xml")

    ors = read_ors(ors_path)
    xml = read_xml(xml_path, filename)

    print("\n" + "=" * 80)
    print(filename)
    print(f"ORS={len(ors)}  XML={len(xml)}")
    print("=" * 80)

    # Speaker sequence is useful because translated text differs from source text.
    a = [x["name"] for x in ors]
    b = [x["name"] for x in xml]
    sm = SequenceMatcher(a=a, b=b, autojunk=False)

    diffs = [op for op in sm.get_opcodes() if op[0] != "equal"]

    if not diffs:
        print("A sequencia de personagens e igual; o erro pode envolver duas falas")
        print("consecutivas do mesmo personagem. Compare manualmente as janelas abaixo.")
        continue

    for tag, i1, i2, j1, j2 in diffs:
        print(f"\nDIFERENCA: {tag.upper()} | ORS #{i1+1}..{i2} | XML #{j1+1}..{j2}")
        show_window("ORS ORIGINAL:", ors, i1, i2, True)
        print()
        show_window("XML ATUAL:", xml, j1, j2, False)

print("\nDiagnostico concluido.")
