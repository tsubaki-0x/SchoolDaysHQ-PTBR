from pathlib import Path
import shutil
import sys
import xml.etree.ElementTree as ET

FOLDERS = [f"{i:02d}" for i in range(6)]


def project_root() -> Path:
    script_dir = Path(__file__).resolve().parent
    if script_dir.name.upper() == "TOOLS":
        return script_dir.parent
    return script_dir


def _parse_command_line(line: str, marker: str, min_parts: int):
    marker_pos = line.find(marker)
    if marker_pos == -1:
        return None

    body = line.rstrip("\r\n")
    newline = line[len(body):]

    end = body.rfind(";")
    if end == -1 or end < marker_pos + len(marker):
        return None

    prefix = body[:marker_pos + len(marker)]
    payload = body[marker_pos + len(marker):end]
    suffix = body[end:]
    parts = payload.split("\t")

    if len(parts) < min_parts:
        return None

    return prefix, parts, suffix, newline


def count_valid_commands(contents: str, marker: str, min_parts: int) -> int:
    return sum(
        1
        for line in contents.splitlines(keepends=True)
        if _parse_command_line(line, marker, min_parts) is not None
    )


def expected_ids(prefix: str, count: int):
    return [f"{prefix}{i:04d}" for i in range(1, count + 1)]


def has_forbidden_control(text: str) -> bool:
    return "\t" in text or "\r" in text or "\n" in text


def validate_ids(elements, prefix: str, file_name: str, kind: str, errors, warnings):
    ids = [el.get("id") for el in elements]
    present = [x for x in ids if x is not None]

    if not present:
        if elements:
            warnings.append(
                f"{file_name}: {kind} sem IDs (XML legado). "
                "A contagem e a ordem serão verificadas, mas uma exclusão "
                "compensada por duplicação pode não ser detectada."
            )
        return

    if len(present) != len(elements):
        errors.append(
            f"{file_name}: {kind} usa IDs parcialmente. "
            "Todos os elementos devem ter id."
        )
        return

    seen = set()
    duplicates = []
    for x in ids:
        if x in seen and x not in duplicates:
            duplicates.append(x)
        seen.add(x)

    if duplicates:
        errors.append(
            f"{file_name}: IDs duplicados em {kind}: "
            + ", ".join(duplicates[:10])
        )
        return

    exp = expected_ids(prefix, len(elements))
    if ids != exp:
        missing = [x for x in exp if x not in ids]
        unexpected = [x for x in ids if x not in exp]
        detail = []

        if missing:
            detail.append("ausentes=" + ", ".join(missing[:10]))
        if unexpected:
            detail.append("inesperados=" + ", ".join(unexpected[:10]))

        if not missing and not unexpected:
            first_bad = next(
                (i for i, (a, b) in enumerate(zip(ids, exp), 1) if a != b),
                None,
            )
            detail.append(f"ordem alterada a partir da posição {first_bad}")

        errors.append(
            f"{file_name}: sequência de IDs inválida em {kind}"
            + (f" ({'; '.join(detail)})" if detail else "")
        )


def validate_printtext_elements(elements, file_name, errors):
    for i, el in enumerate(elements, 1):
        name = el.get("name")
        text = el.text if el.text is not None else ""

        if name is None:
            errors.append(f"{file_name}: PrintText #{i} sem atributo name")
            continue

        if has_forbidden_control(name):
            errors.append(
                f"{file_name}: PrintText #{i} possui TAB/quebra de linha no name"
            )

        if has_forbidden_control(text):
            errors.append(
                f"{file_name}: PrintText #{i} possui TAB/quebra de linha no texto"
            )


def validate_setselect_elements(elements, file_name, errors):
    for i, el in enumerate(elements, 1):
        sel1 = el.get("sel1")
        sel2 = el.get("sel2")

        if sel1 is None or sel2 is None:
            errors.append(
                f"{file_name}: SetSELECT #{i} precisa ter sel1 e sel2"
            )
            continue

        if has_forbidden_control(sel1) or has_forbidden_control(sel2):
            errors.append(
                f"{file_name}: SetSELECT #{i} possui TAB/quebra de linha"
            )


def replace_printtext(file_contents: str, elements):
    lines = file_contents.splitlines(keepends=True)
    index = 0
    out = []

    for line in lines:
        parsed = _parse_command_line(line, "[PrintText]=", 4)

        if parsed is None:
            out.append(line)
            continue

        prefix, parts, suffix, newline = parsed

        if index >= len(elements):
            raise ValueError(
                "Há mais comandos [PrintText] no ORS do que elementos "
                "<PrintText> no XML."
            )

        element = elements[index]
        new_name = element.get("name")
        new_text = element.text if element.text is not None else ""

        if new_name is None:
            new_name = parts[1]

        parts[1] = new_name
        parts[2] = new_text

        out.append(prefix + "\t".join(parts) + suffix + newline)
        index += 1

    return "".join(out), index


def replace_setselect(file_contents: str, elements):
    lines = file_contents.splitlines(keepends=True)
    index = 0
    out = []

    for line in lines:
        parsed = _parse_command_line(line, "[SetSELECT]=", 3)

        if parsed is None:
            out.append(line)
            continue

        prefix, parts, suffix, newline = parsed

        if index >= len(elements):
            raise ValueError(
                "Há mais comandos [SetSELECT] no ORS do que elementos "
                "<SetSELECT> no XML."
            )

        element = elements[index]
        new_sel1 = element.get("sel1")
        new_sel2 = element.get("sel2")

        if new_sel1 is not None:
            parts[1] = new_sel1
        if new_sel2 is not None:
            parts[2] = new_sel2

        out.append(prefix + "\t".join(parts) + suffix + newline)
        index += 1

    return "".join(out), index


def collect_original_ors(folder: Path):
    return {
        p.name: p
        for p in sorted(folder.iterdir())
        if p.is_file() and p.name.upper().endswith(".ORS")
    }


def preflight(root: Path):
    original_script = root / "ORIGINAL" / "Script"
    original_english = original_script / "ENGLISH"
    xml_root = root / "XML" / "PT_BR"

    errors = []
    warnings = []
    plan = []

    if not original_script.is_dir():
        errors.append(f"ORIGINAL\\Script não encontrado: {original_script}")
        return errors, warnings, plan

    if not original_english.is_dir():
        errors.append(
            f"ORIGINAL\\Script\\ENGLISH não encontrado: {original_english}"
        )
        return errors, warnings, plan

    missing_xml = [
        xml_root / f"{n}.xml"
        for n in FOLDERS
        if not (xml_root / f"{n}.xml").is_file()
    ]
    for p in missing_xml:
        errors.append(f"XML PT-BR ausente: {p}")

    missing_dirs = [
        original_english / n
        for n in FOLDERS
        if not (original_english / n).is_dir()
    ]
    for p in missing_dirs:
        errors.append(f"Pasta original ausente: {p}")

    if errors:
        return errors, warnings, plan

    for folder in FOLDERS:
        xml_path = xml_root / f"{folder}.xml"
        src_folder = original_english / folder

        try:
            tree = ET.parse(xml_path)
            xml_root_node = tree.getroot()
        except ET.ParseError as e:
            errors.append(f"{xml_path}: XML inválido: {e}")
            continue
        except OSError as e:
            errors.append(f"{xml_path}: {e}")
            continue

        if xml_root_node.tag != "ORSData":
            errors.append(
                f"{xml_path}: raiz deve ser <ORSData>, "
                f"encontrado <{xml_root_node.tag}>"
            )
            continue

        file_elements = xml_root_node.findall("./File")
        nested_files = xml_root_node.findall(".//File")
        if len(nested_files) != len(file_elements):
            errors.append(
                f"{xml_path}: há <File> aninhado/fora do nível esperado"
            )

        original_files = collect_original_ors(src_folder)
        xml_names = []

        for fe in file_elements:
            name = fe.get("name")
            if not name:
                errors.append(f"{xml_path}: <File> sem atributo name")
            else:
                xml_names.append(name)

        seen = set()
        dup_files = []
        for name in xml_names:
            if name in seen and name not in dup_files:
                dup_files.append(name)
            seen.add(name)

        for name in dup_files:
            errors.append(f"{xml_path}: <File> duplicado: {name}")

        original_names = set(original_files)
        xml_name_set = set(xml_names)

        for name in sorted(original_names - xml_name_set):
            errors.append(f"{xml_path}: <File> ausente: {name}")
        for name in sorted(xml_name_set - original_names):
            errors.append(f"{xml_path}: <File> inesperado: {name}")

        by_name = {
            fe.get("name"): fe
            for fe in file_elements
            if fe.get("name")
        }

        for file_name, src_file in original_files.items():
            file_element = by_name.get(file_name)
            if file_element is None:
                continue

            for child in list(file_element):
                if child.tag not in {"PrintText", "SetSELECT"}:
                    errors.append(
                        f"{file_name}: tag inesperada dentro de <File>: <{child.tag}>"
                    )

            try:
                contents = src_file.read_text(encoding="utf-8")
            except UnicodeDecodeError as e:
                errors.append(
                    f"{src_file}: erro UTF-8 no byte {e.start}: {e.reason}"
                )
                continue
            except OSError as e:
                errors.append(f"{src_file}: {e}")
                continue

            print_elements = file_element.findall("./PrintText")
            select_elements = file_element.findall("./SetSELECT")

            source_print_count = count_valid_commands(
                contents, "[PrintText]=", 4
            )
            source_select_count = count_valid_commands(
                contents, "[SetSELECT]=", 3
            )

            if source_print_count != len(print_elements):
                errors.append(
                    f"{file_name}: PrintText diferente "
                    f"(ORS={source_print_count}, XML={len(print_elements)})"
                )

            if source_select_count != len(select_elements):
                errors.append(
                    f"{file_name}: SetSELECT diferente "
                    f"(ORS={source_select_count}, XML={len(select_elements)})"
                )

            validate_printtext_elements(print_elements, file_name, errors)
            validate_setselect_elements(select_elements, file_name, errors)

            validate_ids(
                print_elements, "PT", file_name, "PrintText", errors, warnings
            )
            validate_ids(
                select_elements, "SEL", file_name, "SetSELECT", errors, warnings
            )

            plan.append(
                {
                    "folder": folder,
                    "file_name": file_name,
                    "src_file": src_file,
                    "print_elements": print_elements,
                    "select_elements": select_elements,
                    "source_print_count": source_print_count,
                    "source_select_count": source_select_count,
                }
            )

    return errors, warnings, plan


def main():
    root = project_root()
    original_script = root / "ORIGINAL" / "Script"
    build_root = root / "BUILD"
    final_script = build_root / "Script"
    temp_script = build_root / "_Script_build_tmp"

    print("======================================")
    print("XML -> ORS / BUILD")
    print("======================================")
    print("Executando validação completa antes da BUILD...")
    print()

    errors, warnings, plan = preflight(root)

    total_expected_files = len(plan)
    total_expected_pt = sum(x["source_print_count"] for x in plan)
    total_expected_ss = sum(x["source_select_count"] for x in plan)

    print("======================================")
    print("PRÉ-VALIDAÇÃO")
    print("======================================")
    print(f"ORS validados:        {total_expected_files}")
    print(f"PrintText validados:  {total_expected_pt}")
    print(f"SetSELECT validados:  {total_expected_ss}")
    print(f"Avisos:               {len(warnings)}")
    print(f"Erros:                {len(errors)}")

    if warnings:
        print()
        print("AVISOS:")
        for warning in warnings[:20]:
            print("  -", warning)
        if len(warnings) > 20:
            print(f"  ... e mais {len(warnings) - 20}")
        print()
        print(
            "XMLs legados sem IDs continuam compatíveis. "
            "Quando forem regenerados pelo novo ors2xml_fixed, "
            "a validação ficará ainda mais rígida."
        )

    if errors:
        print()
        print("ERROS ENCONTRADOS. A BUILD atual NÃO foi alterada.")
        for err in errors[:100]:
            print("  -", err)
        if len(errors) > 100:
            print(f"  ... e mais {len(errors) - 100}")
        sys.exit(1)

    print()
    print("Pré-validação aprovada.")
    print("Copiando ORIGINAL\\Script para área temporária...")

    build_root.mkdir(parents=True, exist_ok=True)
    if temp_script.exists():
        shutil.rmtree(temp_script)

    shutil.copytree(original_script, temp_script)

    total_files = 0
    total_printtext = 0
    total_setselect = 0
    folder_stats = {n: [0, 0, 0] for n in FOLDERS}

    try:
        for item in plan:
            folder = item["folder"]
            file_name = item["file_name"]
            src_file = item["src_file"]
            print_elements = item["print_elements"]
            select_elements = item["select_elements"]

            contents = src_file.read_text(encoding="utf-8")

            contents, replaced_pt = replace_printtext(
                contents, print_elements
            )
            contents, replaced_ss = replace_setselect(
                contents, select_elements
            )

            final_pt = count_valid_commands(contents, "[PrintText]=", 4)
            final_ss = count_valid_commands(contents, "[SetSELECT]=", 3)

            if final_pt != item["source_print_count"]:
                raise RuntimeError(
                    f"{file_name}: PrintText mudou após conversão "
                    f"({item['source_print_count']} -> {final_pt})"
                )
            if final_ss != item["source_select_count"]:
                raise RuntimeError(
                    f"{file_name}: SetSELECT mudou após conversão "
                    f"({item['source_select_count']} -> {final_ss})"
                )

            dst_file = temp_script / "ENGLISH" / folder / file_name
            dst_file.parent.mkdir(parents=True, exist_ok=True)
            with dst_file.open("w", encoding="utf-8", newline="") as f:
                f.write(contents)

            total_files += 1
            total_printtext += replaced_pt
            total_setselect += replaced_ss

            folder_stats[folder][0] += 1
            folder_stats[folder][1] += replaced_pt
            folder_stats[folder][2] += replaced_ss

        for folder in FOLDERS:
            expected = len(
                collect_original_ors(original_script / "ENGLISH" / folder)
            )
            converted, pt, ss = folder_stats[folder]
            print(
                f"[{folder}] ORS: {converted}/{expected} | "
                f"PrintText: {pt} | SetSELECT: {ss}"
            )

        if final_script.exists():
            shutil.rmtree(final_script)
        temp_script.rename(final_script)

    except Exception:
        shutil.rmtree(temp_script, ignore_errors=True)
        raise

    print()
    print("BUILD criado com sucesso.")
    print(f"ORS convertidos:       {total_files}")
    print(f"PrintText substituídos:{total_printtext:>8}")
    print(f"SetSELECT substituídos:{total_setselect:>8}")
    print(f"Saída: {final_script}")
    print()
    print("A estrutura original e os .DS_STORE foram copiados automaticamente.")
    print("As pastas ENGLISH\\00..05 agora contêm os ORS gerados a partir dos XMLs.")


if __name__ == "__main__":
    main()
