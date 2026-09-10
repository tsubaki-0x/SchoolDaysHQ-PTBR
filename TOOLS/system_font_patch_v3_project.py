import os
import sys
import struct
import tempfile
import zlib
from pathlib import Path

# School Days HQ - System.GPK font patch
#
# Fluxo automático do projeto:
#
#   ORIGINAL/System_original.GPK
#   SYSTEM/FONTDATA_PTBR_SEM_ACENTOS.DAT
#               ↓
#   OUTPUT/System.GPK
#
# Este patcher NÃO recria o PIDX e NÃO aceita FONTDATA de tamanho diferente.
# Ele foi feito especificamente para o patch estável "sem acentos reais",
# no qual os caracteres PT-BR apenas reutilizam os glifos das letras-base.

XOR_KEY = bytes.fromhex(
    "82 EE 1D B3 57 E9 2C C2 2F 54 7B 10 4C 9A 75 49"
)

PIDX = b"STKFile0PIDX"
PACK = b"STKFile0PACKFILE"
TARGET = "SYSTEM/FONTDATA_ENG.DAT"


def project_root() -> Path:
    script_dir = Path(__file__).resolve().parent
    if script_dir.name.upper() == "TOOLS":
        return script_dir.parent
    return script_dir


def xor_data(data: bytes) -> bytes:
    return bytes(
        b ^ XOR_KEY[i % len(XOR_KEY)]
        for i, b in enumerate(data)
    )


def load_index(gpk: bytes) -> bytes:
    if len(gpk) < 32:
        raise ValueError("System.GPK inválido: arquivo pequeno demais.")

    footer = len(gpk) - 32

    if gpk[footer:footer + 12] != PIDX:
        raise ValueError("STKFile0PIDX não encontrado.")

    if gpk[footer + 16:footer + 32] != PACK:
        raise ValueError("STKFile0PACKFILE não encontrado.")

    pidx_size = struct.unpack_from("<I", gpk, footer + 12)[0]
    pidx_pos = footer - pidx_size

    if pidx_pos < 0:
        raise ValueError("Posição do PIDX inválida.")

    encrypted = gpk[pidx_pos:footer]
    decrypted = xor_data(encrypted)

    if len(decrypted) < 4:
        raise ValueError("PIDX inválido.")

    plain_size = struct.unpack_from("<I", decrypted, 0)[0]

    try:
        index = zlib.decompress(decrypted[4:])
    except zlib.error as e:
        raise ValueError(f"Falha ao descomprimir PIDX: {e}")

    if len(index) != plain_size:
        raise ValueError(
            "Tamanho do PIDX não confere.\n"
            f"Esperado: {plain_size:,}\n"
            f"Obtido:   {len(index):,}"
        )

    return index


def find_entry(index: bytes, wanted: str):
    pos = 0

    while True:
        if pos + 2 > len(index):
            raise ValueError("Fim inesperado do PIDX.")

        name_len = struct.unpack_from("<H", index, pos)[0]

        if name_len == 0:
            return None

        pos += 2

        name_bytes_len = name_len * 2
        if pos + name_bytes_len > len(index):
            raise ValueError("Nome truncado no PIDX.")

        name = index[pos:pos + name_bytes_len].decode("utf-16-le")
        pos += name_bytes_len

        if pos + 6 + 8 + 4 + 4 + 1 > len(index):
            raise ValueError(f"Entrada truncada no PIDX: {name}")

        pos += 6

        offset, size = struct.unpack_from("<II", index, pos)
        pos += 8

        flags = index[pos:pos + 4]
        pos += 4

        unc_size = struct.unpack_from("<I", index, pos)[0]
        pos += 4

        header_len = index[pos]
        pos += 1

        if pos + header_len > len(index):
            raise ValueError(f"Header truncado no PIDX: {name}")

        header = index[pos:pos + header_len]
        pos += header_len

        if name.upper() == wanted.upper():
            return {
                "name": name,
                "offset": offset,
                "size": size,
                "flags": flags,
                "unc_size": unc_size,
                "header_len": header_len,
                "header": header,
            }


def normalize_replacement(replacement: bytes, expected_size: int):
    """
    Algumas extrações feitas pelo CRASSGUI adicionam o trailer:

        47 0D 0A  -> b'G\\r\\n'

    Esses 3 bytes não pertencem à entrada lógica dentro do GPK.
    Só removemos o trailer quando o tamanho é exatamente esperado + 3.
    """
    if len(replacement) == expected_size:
        return replacement, False

    if (
        len(replacement) == expected_size + 3
        and replacement.endswith(b"G\r\n")
    ):
        return replacement[:-3], True

    raise ValueError(
        "O tamanho do FONTDATA substituto não corresponde ao arquivo "
        "lógico armazenado no GPK.\n"
        f"Tamanho lógico esperado: {expected_size:,} bytes\n"
        f"Tamanho recebido:        {len(replacement):,} bytes\n\n"
        "Este patcher aceita somente o FONTDATA PT-BR de tamanho fixo."
    )


def validate_output(
    original_bytes: bytes,
    generated_bytes: bytes,
    entry: dict,
    replacement: bytes,
):
    if len(generated_bytes) != len(original_bytes):
        raise ValueError(
            "O tamanho final da System.GPK mudou inesperadamente."
        )

    # PIDX e footer precisam permanecer idênticos, pois este patcher não os toca.
    original_index = load_index(original_bytes)
    generated_index = load_index(generated_bytes)

    if generated_index != original_index:
        raise ValueError("PIDX foi alterado inesperadamente.")

    check_entry = find_entry(generated_index, TARGET)

    if check_entry is None:
        raise ValueError(
            f"{TARGET} não foi encontrado na System.GPK gerada."
        )

    if check_entry != entry:
        raise ValueError(
            "Metadados da entrada FONTDATA mudaram inesperadamente."
        )

    hlen = entry["header_len"]
    physical_start = entry["offset"]
    physical_len = entry["size"] - hlen
    physical_end = physical_start + physical_len

    logical_font = (
        entry["header"]
        + generated_bytes[physical_start:physical_end]
    )

    if logical_font != replacement:
        raise ValueError(
            "FONTDATA dentro da System.GPK gerada não corresponde "
            "byte-a-byte ao arquivo PT-BR."
        )


def patch_system(
    original_path: str | Path,
    replacement_path: str | Path,
    output_path: str | Path,
):
    original_path = Path(original_path)
    replacement_path = Path(replacement_path)
    output_path = Path(output_path)

    if not original_path.is_file():
        raise FileNotFoundError(
            f"System original não encontrada:\n{original_path}"
        )

    if not replacement_path.is_file():
        raise FileNotFoundError(
            f"FONTDATA PT-BR não encontrado:\n{replacement_path}"
        )

    if (
        os.path.normcase(str(original_path.resolve()))
        == os.path.normcase(str(output_path.resolve()))
    ):
        raise ValueError(
            "A saída não pode ser o próprio System_original.GPK."
        )

    print("========================================")
    print("SYSTEM.GPK PT-BR FONT PATCH")
    print("========================================")
    print(f"System original: {original_path}")
    print(f"FONTDATA PT-BR:  {replacement_path}")
    print(f"Saída:           {output_path}")
    print()

    print("Lendo System.GPK...")
    original = bytearray(original_path.read_bytes())

    print("Lendo PIDX...")
    index = load_index(original)

    entry = find_entry(index, TARGET)

    if entry is None:
        raise ValueError(f"{TARGET} não encontrado.")

    if entry["flags"] == b"DFLT":
        raise ValueError(
            "FONTDATA_ENG.DAT apareceu comprimido como DFLT. "
            "Este patcher espera a entrada raw original."
        )

    print()
    print("Target found:")
    print(f"  Name:       {entry['name']}")
    print(f"  Offset:     0x{entry['offset']:08X}")
    print(f"  Size:       {entry['size']:,} bytes")
    print(f"  Flags:      {entry['flags']!r}")
    print(f"  Header len: {entry['header_len']}")
    print(f"  Header:     {entry['header'].hex(' ').upper()}")

    replacement_raw = replacement_path.read_bytes()

    replacement, stripped = normalize_replacement(
        replacement_raw,
        entry["size"],
    )

    if stripped:
        print()
        print(
            "Trailer CRASSGUI 47 0D 0A (G\\r\\n) detectado "
            "e removido para o patch."
        )

    hlen = entry["header_len"]

    if replacement[:hlen] != entry["header"]:
        raise ValueError(
            "Os bytes de header do FONTDATA substituto mudaram.\n"
            f"Esperado: {entry['header'].hex(' ').upper()}\n"
            f"Recebido: {replacement[:hlen].hex(' ').upper()}\n"
            "Este patcher seguro não altera o PIDX."
        )

    physical_start = entry["offset"]
    physical_len = entry["size"] - hlen
    physical_end = physical_start + physical_len

    if physical_len < 0:
        raise ValueError(
            "Tamanho físico interno do FONTDATA é inválido."
        )

    if physical_end > len(original):
        raise ValueError(
            "Payload físico do FONTDATA ultrapassa o tamanho do GPK."
        )

    new_payload = replacement[hlen:]

    if len(new_payload) != physical_len:
        raise ValueError(
            "Tamanho físico interno não confere.\n"
            f"Esperado: {physical_len:,}\n"
            f"Recebido: {len(new_payload):,}"
        )

    old_payload = bytes(
        original[physical_start:physical_end]
    )

    diff_count = sum(
        a != b
        for a, b in zip(old_payload, new_payload)
    )

    print()
    print("========================================")
    print("PRÉ-VALIDAÇÃO")
    print("========================================")
    print(f"Tamanho lógico:          {entry['size']:,} bytes")
    print(f"Tamanho físico:          {physical_len:,} bytes")
    print(f"Bytes físicos alterados: {diff_count:,}")
    print("PIDX:                     será preservado")
    print("Demais recursos:          serão preservados")

    original[physical_start:physical_end] = new_payload

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Grava primeiro em um temporário. OUTPUT/System.GPK anterior
    # só é substituído depois da pós-validação.
    fd, temp_name = tempfile.mkstemp(
        prefix="_System_font_patch_",
        suffix=".GPK",
        dir=str(output_path.parent),
    )
    os.close(fd)

    try:
        Path(temp_name).write_bytes(original)

        generated = Path(temp_name).read_bytes()

        validate_output(
            original_path.read_bytes(),
            generated,
            entry,
            replacement,
        )

        os.replace(temp_name, output_path)

    except Exception:
        if os.path.exists(temp_name):
            os.remove(temp_name)
        raise

    print()
    print("========================================")
    print("PÓS-VALIDAÇÃO")
    print("========================================")
    print("FONTDATA dentro do GPK:  OK")
    print("PIDX:                    INTACTO")
    print("Tamanho da System.GPK:   INTACTO")
    print("Demais recursos:         INTACTOS")
    print("RESULTADO: SYSTEM.GPK VÁLIDA")

    print()
    print("========================================")
    print("SYSTEM.GPK PT-BR GERADA COM SUCESSO")
    print("========================================")
    print(f"Output: {output_path.resolve()}")
    print(f"Size:   {output_path.stat().st_size:,} bytes")
    print()
    print(
        "Este é o patch estável sem glifos acentuados reais: "
        "os caracteres PT-BR reutilizam os glifos das letras-base."
    )


def main():
    root = project_root()

    if len(sys.argv) == 1:
        original_gpk = (
            root
            / "ORIGINAL"
            / "System_original.GPK"
        )

        replacement_font = (
            root
            / "SYSTEM"
            / "FONTDATA_PTBR_SEM_ACENTOS.DAT"
        )

        output_gpk = (
            root
            / "OUTPUT"
            / "System.GPK"
        )

    elif len(sys.argv) == 4:
        original_gpk = Path(sys.argv[1])
        replacement_font = Path(sys.argv[2])
        output_gpk = Path(sys.argv[3])

    else:
        print(
            "Uso:\n"
            "  python system_font_patch_v3_project.py\n\n"
            "Modo automático:\n"
            "  ORIGINAL\\System_original.GPK\n"
            "  + SYSTEM\\FONTDATA_PTBR_SEM_ACENTOS.DAT\n"
            "  -> OUTPUT\\System.GPK\n\n"
            "Ou manualmente:\n"
            "  python system_font_patch_v3_project.py "
            "<System.GPK> <FONTDATA.DAT> <Output.GPK>"
        )
        sys.exit(1)

    try:
        patch_system(
            original_gpk,
            replacement_font,
            output_gpk,
        )

    except Exception as e:
        print()
        print("ERRO:")
        print(e)
        print()
        print(
            "A saída anterior, se existia, foi preservada."
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
