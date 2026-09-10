from pathlib import Path
import sys
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom

# School Days HQ ORS -> XML
# ORS esperado: UTF-8 sem BOM
# Separador de campos: TAB
#
# Estrutura esperada do projeto:
#   SchoolDays_PTBR/
#   ├─ ORIGINAL/Script/ENGLISH/00..05
#   ├─ XML/
#   │  ├─ ORIGINAL_EN/   -> XMLs ingleses gerados automaticamente
#   │  └─ PT_BR/         -> XMLs traduzidos manualmente
#   ├─ BUILD/
#   ├─ OUTPUT/
#   └─ TOOLS/ors2xml_fixed.py
#
# Esta versão gera IDs estáveis por arquivo:
#   PrintText: PT0001, PT0002, ...
#   SetSELECT: SEL0001, SEL0002, ...
#
# Esses IDs são usados pelo xml2ors_fixed_v3_robust.py para detectar:
# - falas apagadas
# - falas duplicadas
# - falas adicionadas
# - ordem alterada

FOLDERS = [f"{i:02d}" for i in range(6)]


def project_root() -> Path:
    script_dir = Path(__file__).resolve().parent
    if script_dir.name.upper() == "TOOLS":
        return script_dir.parent
    return script_dir


def _parse_command_line(line: str, marker: str, min_parts: int):
    """
    Interpreta um comando ORS por linha.

    O texto pode conter ';', então o terminador do comando é o ÚLTIMO ';'
    da linha, não o primeiro.
    """
    marker_pos = line.find(marker)
    if marker_pos == -1:
        return None

    body = line.rstrip("\r\n")
    end = body.rfind(";")

    if end == -1 or end < marker_pos + len(marker):
        return None

    payload = body[marker_pos + len(marker):end]
    parts = payload.split("\t")

    if len(parts) < min_parts:
        return None

    return parts


def add_translation_header(root):
    root.append(
        ET.Comment(
            "\n"
            " SCHOOL DAYS HQ TRANSLATION XML\n"
            "\n"
            " TRADUZA SOMENTE:\n"
            " - o texto entre <PrintText>...</PrintText>\n"
            " - os valores sel1 e sel2 de <SetSELECT>\n"
            " - o atributo name de <PrintText> apenas se realmente quiser traduzir\n"
            "   nomes genéricos de personagens (ex.: Passenger -> Passageira)\n"
            "\n"
            " NÃO ALTERE:\n"
            " - id de PrintText\n"
            " - id de SetSELECT\n"
            " - name de <File>\n"
            " - quantidade de elementos\n"
            " - ordem dos elementos\n"
            "\n"
            " Os IDs são usados para validar a tradução antes da BUILD.\n"
        )
    )


def convert_folder(ors_directory: Path, output_file: Path):
    root = ET.Element("ORSData")
    add_translation_header(root)

    total_files = 0
    read_files = 0
    printtext_count = 0
    setselect_count = 0
    errors = []

    for ors_file_path in sorted(
        ors_directory.iterdir(),
        key=lambda p: p.name.lower()
    ):
        if not ors_file_path.is_file() or ors_file_path.suffix.upper() != ".ORS":
            continue

        total_files += 1
        file_element = ET.SubElement(root, "File")
        file_element.set("name", ors_file_path.name)

        pt_index = 0
        sel_index = 0

        try:
            with ors_file_path.open("r", encoding="utf-8") as file:
                read_files += 1

                for line_number, line in enumerate(file, 1):
                    parsed = _parse_command_line(line, "[PrintText]=", 4)

                    if parsed is not None:
                        parts = parsed
                        pt_index += 1

                        name = parts[1].strip()
                        text = parts[2]

                        element = ET.SubElement(file_element, "PrintText")
                        element.set("id", f"PT{pt_index:04d}")
                        element.set("name", name)
                        element.text = text
                        printtext_count += 1
                        continue

                    parsed = _parse_command_line(line, "[SetSELECT]=", 3)

                    if parsed is not None:
                        parts = parsed
                        sel_index += 1

                        sel1 = parts[1]
                        sel2 = parts[2]

                        element = ET.SubElement(file_element, "SetSELECT")
                        element.set("id", f"SEL{sel_index:04d}")
                        element.set("sel1", sel1)
                        element.set("sel2", sel2)
                        setselect_count += 1

        except UnicodeDecodeError as e:
            errors.append(
                f"{ors_file_path}: erro UTF-8 no byte {e.start}: {e.reason}"
            )
            root.remove(file_element)

        except OSError as e:
            errors.append(f"{ors_file_path}: {e}")
            root.remove(file_element)

    xml_string = ET.tostring(root, encoding="utf-8")
    dom = minidom.parseString(xml_string)

    output_file.parent.mkdir(parents=True, exist_ok=True)
    with output_file.open("wb") as f:
        f.write(dom.toprettyxml(indent="    ", encoding="utf-8"))

    return {
        "total_files": total_files,
        "read_files": read_files,
        "printtext": printtext_count,
        "setselect": setselect_count,
        "errors": errors,
    }


def main():
    root = project_root()
    source_root = root / "ORIGINAL" / "Script" / "ENGLISH"
    xml_root = root / "XML" / "ORIGINAL_EN"

    force = "--force" in sys.argv[1:]
    requested = [a for a in sys.argv[1:] if not a.startswith("--")]

    if requested:
        invalid = [x for x in requested if x not in FOLDERS]
        if invalid:
            print("ERRO: pasta inválida:", ", ".join(invalid))
            print("Use 00, 01, 02, 03, 04 ou 05.")
            sys.exit(1)
        folders = requested
    else:
        folders = FOLDERS

    if not source_root.is_dir():
        print("ERRO: pasta original não encontrada:")
        print(source_root)
        sys.exit(1)

    missing_dirs = [
        n for n in folders
        if not (source_root / n).is_dir()
    ]
    if missing_dirs:
        print("ERRO: faltam pastas ORS em ORIGINAL\\Script\\ENGLISH:")
        for n in missing_dirs:
            print("  -", n)
        sys.exit(1)

    existing = [
        xml_root / f"{n}.xml"
        for n in folders
        if (xml_root / f"{n}.xml").exists()
    ]

    if existing and not force:
        print("ERRO: já existem XMLs que seriam sobrescritos:")
        for p in existing:
            print("  -", p)
        print()
        print("Isso protege traduções manuais já feitas.")
        print(
            "Se realmente quiser regenerar a partir dos ORS originais, "
            "use --force."
        )
        sys.exit(1)

    print("======================================")
    print("ORS -> XML")
    print("======================================")
    print(f"Origem: {source_root}")
    print(f"Saída:  {xml_root}")
    print()

    total_errors = 0
    total_files = 0
    total_pt = 0
    total_ss = 0

    for n in folders:
        src = source_root / n
        dst = xml_root / f"{n}.xml"
        result = convert_folder(src, dst)

        total_files += result["read_files"]
        total_pt += result["printtext"]
        total_ss += result["setselect"]

        print(
            f"[{n}] {result['read_files']}/{result['total_files']} ORS | "
            f"PrintText: {result['printtext']} | "
            f"SetSELECT: {result['setselect']}"
        )
        print(f"     -> {dst}")

        if result["errors"]:
            total_errors += len(result["errors"])
            for err in result["errors"]:
                print("     ERRO:", err)

    print()

    if total_errors:
        print(f"Concluído com {total_errors} erro(s).")
        sys.exit(1)

    print("Conversão concluída sem erros.")
    print(f"ORS convertidos:       {total_files}")
    print(f"PrintText exportados:  {total_pt}")
    print(f"SetSELECT exportados:  {total_ss}")
    print()
    print("Os XMLs contêm o texto ORIGINAL em inglês.")
    print("Cada PrintText e SetSELECT recebeu um ID de validação.")
    print("Os XMLs ingleses foram salvos em XML\\ORIGINAL_EN.")
    print("Copie-os para XML\\PT_BR antes de traduzir, ou mantenha suas traduções antigas lá.")


if __name__ == "__main__":
    main()
