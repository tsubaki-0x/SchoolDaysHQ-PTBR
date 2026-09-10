import os
import sys
import struct
import zlib
import tempfile
from pathlib import Path

STUB_SIZE = 0x1400

XOR_KEY = bytes.fromhex(
    "82 EE 1D B3 57 E9 2C C2 2F 54 7B 10 4C 9A 75 49"
)

PIDX = b"STKFile0PIDX"
PACK = b"STKFile0PACKFILE"


def xor_data(data):
    return bytes(
        b ^ XOR_KEY[i % len(XOR_KEY)]
        for i, b in enumerate(data)
    )


def load_original(path):
    with open(path, "rb") as f:
        data = f.read()

    if len(data) < STUB_SIZE + 32:
        raise ValueError("GPK original pequeno demais.")

    footer = len(data) - 32

    if data[footer:footer + 12] != PIDX:
        raise ValueError("STKFile0PIDX não encontrado no footer.")

    pidx_size = struct.unpack_from("<I", data, footer + 12)[0]

    if data[footer + 16:footer + 32] != PACK:
        raise ValueError("STKFile0PACKFILE não encontrado.")

    pidx_pos = footer - pidx_size

    if pidx_pos < STUB_SIZE:
        raise ValueError("Posição do PIDX inválida.")

    encrypted = data[pidx_pos:footer]
    decrypted = xor_data(encrypted)

    if len(decrypted) < 4:
        raise ValueError("PIDX inválido.")

    expected_plain_size = struct.unpack_from("<I", decrypted, 0)[0]

    try:
        index = zlib.decompress(decrypted[4:])
    except zlib.error as e:
        raise ValueError(f"Falha ao descomprimir PIDX original: {e}")

    if len(index) != expected_plain_size:
        raise ValueError(
            f"Tamanho do PIDX não confere: esperado "
            f"{expected_plain_size}, obtido {len(index)}."
        )

    return data, index


def parse_index(index):
    entries = []
    pos = 0

    while True:
        if pos + 2 > len(index):
            raise ValueError("Fim inesperado do PIDX.")

        name_len = struct.unpack_from("<H", index, pos)[0]

        if name_len == 0:
            return entries, index[pos:]

        entry_start = pos
        pos += 2

        name_bytes = index[pos:pos + name_len * 2]
        if len(name_bytes) != name_len * 2:
            raise ValueError("Nome truncado no PIDX.")

        name = name_bytes.decode("utf-16-le")
        pos += name_len * 2

        if pos + 6 + 8 + 4 + 4 + 1 > len(index):
            raise ValueError(f"Entrada truncada no PIDX: {name}")

        unknown6 = index[pos:pos + 6]
        pos += 6

        offset, size = struct.unpack_from("<II", index, pos)
        pos += 8

        flags = index[pos:pos + 4]
        pos += 4

        unc = struct.unpack_from("<I", index, pos)[0]
        pos += 4

        hlen = index[pos]
        pos += 1

        header = index[pos:pos + hlen]
        if len(header) != hlen:
            raise ValueError(f"Header truncado no PIDX: {name}")
        pos += hlen

        entries.append({
            "entry_start": entry_start,
            "name": name,
            "name_bytes": name_bytes,
            "unknown6": unknown6,
            "offset": offset,
            "size": size,
            "flags": flags,
            "unc": unc,
            "hlen": hlen,
            "header": header,
        })


def build_file_map(root):
    mapping = {}
    duplicates = []

    for base, dirs, files in os.walk(root):
        for fn in files:
            full = os.path.join(base, fn)
            rel = os.path.relpath(full, root).replace("\\", "/")
            key = rel.lower()

            if key in mapping:
                duplicates.append((rel, os.path.relpath(mapping[key], root).replace("\\", "/")))

            mapping[key] = full

    return mapping, duplicates


def original_stream(original_gpk, entry):
    physical_len = entry["size"] - entry["hlen"]

    if physical_len < 0:
        raise ValueError(f"size < header_len em {entry['name']}")

    payload = original_gpk[
        entry["offset"]:entry["offset"] + physical_len
    ]

    if len(payload) != physical_len:
        raise ValueError(f"Payload truncado em {entry['name']}")

    return entry["header"] + payload


def original_logical_data(original_gpk, entry):
    stream = original_stream(original_gpk, entry)

    if entry["flags"] == b"DFLT":
        try:
            logical = zlib.decompress(stream)
        except zlib.error as e:
            raise ValueError(
                f"Falha ao descomprimir {entry['name']}: {e}"
            )

        if len(logical) != entry["unc"]:
            raise ValueError(
                f"Tamanho descompactado inválido em {entry['name']}: "
                f"PIDX={entry['unc']}, real={len(logical)}"
            )

        return logical

    return stream


def preflight(input_folder, original_gpk_path, output_gpk):
    print("======================================")
    print("PRÉ-VALIDAÇÃO GPK")
    print("======================================")

    input_abs = os.path.abspath(input_folder)
    original_abs = os.path.abspath(original_gpk_path)
    output_abs = os.path.abspath(output_gpk)

    if os.path.normcase(original_abs) == os.path.normcase(output_abs):
        raise ValueError(
            "O arquivo de saída não pode ser o próprio Script_original.GPK."
        )

    if not os.path.isdir(input_folder):
        raise FileNotFoundError(f"BUILD Script não encontrado: {input_folder}")

    if not os.path.isfile(original_gpk_path):
        raise FileNotFoundError(
            f"Script_original.GPK não encontrado: {original_gpk_path}"
        )

    original_gpk, original_index = load_original(original_gpk_path)
    entries, terminator = parse_index(original_index)

    if not entries:
        raise ValueError("PIDX não contém entradas.")

    names_lower = [e["name"].lower() for e in entries]
    if len(names_lower) != len(set(names_lower)):
        raise ValueError("PIDX original contém nomes duplicados (case-insensitive).")

    fmap, duplicates = build_file_map(input_folder)

    if duplicates:
        a, b = duplicates[0]
        raise ValueError(
            f"BUILD contém caminhos duplicados por diferença de maiúsculas/minúsculas: "
            f"{a} / {b}"
        )

    expected = set(names_lower)
    found = set(fmap)

    missing = sorted(expected - found)
    extras = sorted(found - expected)

    dflt_count = sum(1 for e in entries if e["flags"] == b"DFLT")
    raw_count = len(entries) - dflt_count

    print(f"Entradas no GPK original: {len(entries)}")
    print(f"DFLT esperados:           {dflt_count}")
    print(f"Raw esperados:            {raw_count}")
    print(f"Arquivos na BUILD:        {len(fmap)}")
    print(f"Ausentes:                 {len(missing)}")
    print(f"Extras:                   {len(extras)}")

    if missing:
        raise FileNotFoundError(
            f"{len(missing)} arquivo(s) ausente(s) na BUILD. Primeiro: {missing[0]}"
        )

    if extras:
        raise ValueError(
            f"{len(extras)} arquivo(s) extra(s) na BUILD. Primeiro: {extras[0]}"
        )

    # Valida que cada entrada original é legível antes de iniciar o repack.
    for e in entries:
        original_logical_data(original_gpk, e)

    print("RESULTADO: OK")
    print()

    return original_gpk, original_index, entries, terminator, fmap


def validate_generated_gpk(gpk_path, input_folder, original_gpk_path):
    print()
    print("======================================")
    print("PÓS-VALIDAÇÃO GPK")
    print("======================================")

    generated_gpk, generated_index = load_original(gpk_path)
    generated_entries, _ = parse_index(generated_index)

    original_gpk, original_index = load_original(original_gpk_path)
    original_entries, _ = parse_index(original_index)

    if len(generated_entries) != len(original_entries):
        raise ValueError(
            f"Quantidade de entradas mudou: original={len(original_entries)}, "
            f"gerado={len(generated_entries)}"
        )

    original_names = [e["name"].lower() for e in original_entries]
    generated_names = [e["name"].lower() for e in generated_entries]

    if generated_names != original_names:
        raise ValueError("A ordem ou os nomes das entradas do PIDX mudaram.")

    fmap, duplicates = build_file_map(input_folder)
    if duplicates:
        raise ValueError("BUILD passou a conter caminhos duplicados.")

    verified_dflt = 0
    verified_raw = 0

    original_by_name = {e["name"].lower(): e for e in original_entries}

    for e in generated_entries:
        key = e["name"].lower()
        logical = original_logical_data(generated_gpk, e)

        if e["flags"] == b"DFLT":
            with open(fmap[key], "rb") as f:
                expected = f.read()

            if logical != expected:
                raise ValueError(
                    f"Conteúdo lógico do GPK gerado não bate com a BUILD: {e['name']}"
                )

            verified_dflt += 1

        else:
            # Raw entries são intencionalmente preservadas do GPK original.
            original_raw = original_logical_data(
                original_gpk, original_by_name[key]
            )
            if logical != original_raw:
                raise ValueError(
                    f"Raw entry não foi preservada: {e['name']}"
                )
            verified_raw += 1

    if not generated_gpk.startswith(original_gpk[:STUB_SIZE]):
        raise ValueError("Stub/prefixo inicial não foi preservado.")

    print(f"GPK criado:              OK")
    print(f"PIDX/footer:             OK")
    print(f"Entradas verificadas:    {len(generated_entries)}/{len(original_entries)}")
    print(f"DFLT verificados:        {verified_dflt}")
    print(f"Raw preservados:         {verified_raw}")
    print("RESULTADO: GPK VÁLIDO")


def repack(input_folder, original_gpk_path, output_gpk):
    original_gpk, original_index, entries, terminator, fmap = preflight(
        input_folder, original_gpk_path, output_gpk
    )

    print("======================================")
    print("REPACK")
    print("======================================")

    archive = bytearray(original_gpk[:STUB_SIZE])
    new_index = bytearray()

    changed = []
    unchanged = 0
    dflt_count = 0
    raw_count = 0

    for i, e in enumerate(entries, 1):
        src_path = fmap[e["name"].lower()]

        with open(src_path, "rb") as f:
            extracted_data = f.read()

        original_logical = original_logical_data(original_gpk, e)
        changed_entry = extracted_data != original_logical

        if e["flags"] == b"DFLT":
            dflt_count += 1

            if changed_entry:
                full_stream = zlib.compress(extracted_data, 9)
                unc = len(extracted_data)
                changed.append(e["name"])
            else:
                # Preserve original compressed bytes exactly.
                full_stream = original_stream(original_gpk, e)
                unc = e["unc"]
                unchanged += 1

        else:
            raw_count += 1

            # Raw entries (.DS_STORE) são preservadas 100% do original.
            full_stream = original_stream(original_gpk, e)
            unc = e["unc"]

            if changed_entry:
                print(
                    f"WARNING: ignorando diferença externa em raw entry: "
                    f"{e['name']}"
                )

            unchanged += 1

        hlen = e["hlen"]

        if hlen > len(full_stream):
            raise ValueError(
                f"header_len inválido em {e['name']}: "
                f"{hlen} > {len(full_stream)}"
            )

        header = full_stream[:hlen]
        payload = full_stream[hlen:]

        new_offset = len(archive)
        new_size = len(full_stream)

        archive.extend(payload)

        new_index.extend(
            struct.pack("<H", len(e["name_bytes"]) // 2)
        )
        new_index.extend(e["name_bytes"])
        new_index.extend(e["unknown6"])
        new_index.extend(
            struct.pack("<II", new_offset, new_size)
        )
        new_index.extend(e["flags"])
        new_index.extend(struct.pack("<I", unc))
        new_index.extend(struct.pack("<B", hlen))
        new_index.extend(header)

        if i % 200 == 0 or i == len(entries):
            print(f"Processing {i}/{len(entries)}...")

    new_index.extend(
        terminator if terminator else b"\x00\x00\x00\x00"
    )

    print()
    print(f"Arquivos idênticos/preservados: {unchanged}")
    print(f"Arquivos realmente modificados: {len(changed)}")
    print(f"DFLT entries: {dflt_count}")
    print(f"Raw entries:  {raw_count}")

    if changed:
        print("\nModificados:")
        for name in changed[:50]:
            print("  " + name)

        if len(changed) > 50:
            print(f"  ... e mais {len(changed) - 50}")

    output_path = Path(output_gpk).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Cria em arquivo temporário. A saída anterior só é substituída
    # depois que a pós-validação for aprovada.
    fd, temp_name = tempfile.mkstemp(
        prefix="_Script_repack_",
        suffix=".GPK",
        dir=str(output_path.parent)
    )
    os.close(fd)

    try:
        if not changed:
            with open(temp_name, "wb") as f:
                f.write(original_gpk)

            print()
            print("*** PERFECT MATCH ***")
            print(
                "Nenhum ORS lógico foi alterado. "
                "O GPK temporário é byte-a-byte idêntico ao original."
            )
        else:
            compressed_index = zlib.compress(bytes(new_index), 9)
            pidx_plain = (
                struct.pack("<I", len(new_index))
                + compressed_index
            )

            encrypted_pidx = xor_data(pidx_plain)

            archive.extend(encrypted_pidx)
            archive.extend(PIDX)
            archive.extend(
                struct.pack("<I", len(encrypted_pidx))
            )
            archive.extend(PACK)

            with open(temp_name, "wb") as f:
                f.write(archive)

        validate_generated_gpk(
            temp_name,
            input_folder,
            original_gpk_path
        )

        # os.replace é atômico no mesmo filesystem e preserva a saída anterior
        # até o exato momento em que a nova já foi validada.
        os.replace(temp_name, output_path)

    except Exception:
        try:
            if os.path.exists(temp_name):
                os.remove(temp_name)
        finally:
            raise

    final_size = output_path.stat().st_size

    print()
    print("======================================")
    print("GPK PATCH GERADO COM SUCESSO")
    print("======================================")
    print(f"Entries:    {len(entries)}")
    print(f"Modified:   {len(changed)}")
    print(f"Size:       {final_size:,} bytes")
    print(f"Output:     {output_path}")


if __name__ == "__main__":
    script_dir = Path(__file__).resolve().parent
    project_root = (
        script_dir.parent
        if script_dir.name.upper() == "TOOLS"
        else script_dir
    )

    if len(sys.argv) == 1:
        input_folder = str(project_root / "BUILD" / "Script")
        original_gpk = str(
            project_root / "ORIGINAL" / "Script_original.GPK"
        )
        output_dir = project_root / "OUTPUT"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_gpk = str(output_dir / "Script.GPK")

    elif len(sys.argv) == 4:
        input_folder = sys.argv[1]
        original_gpk = sys.argv[2]
        output_gpk = sys.argv[3]
        Path(output_gpk).resolve().parent.mkdir(
            parents=True,
            exist_ok=True
        )

    else:
        print(
            "Uso:\n"
            "  python gpk_repack_v5_robust.py\n\n"
            "Modo automático:\n"
            "  BUILD\\Script + ORIGINAL\\Script_original.GPK\n"
            "  -> OUTPUT\\Script.GPK\n\n"
            "Ou manualmente:\n"
            "  python gpk_repack_v5_robust.py "
            "<ScriptFolder> <OriginalGPK> <OutputGPK>"
        )
        sys.exit(1)

    try:
        repack(
            input_folder,
            original_gpk,
            output_gpk
        )

    except Exception as e:
        print()
        print("ERRO:")
        print(e)
        print()
        print(
            "A saída anterior, se existia, foi preservada. "
            "Nenhum Script.GPK validado foi substituído."
        )
        sys.exit(1)
