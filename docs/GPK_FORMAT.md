# Notas técnicas sobre o formato GPK

Estas notas registram apenas o que foi necessário para a pipeline deste projeto.

## Estrutura geral observada

Os GPKs analisados possuem um prefixo/stub inicial seguido pelos streams dos arquivos e um índice PIDX no final.

Marcadores do footer:

```text
STKFile0PIDX
<uint32 tamanho do PIDX criptografado>
STKFile0PACKFILE
```

O PIDX é protegido com XOR usando a chave:

```text
82 EE 1D B3 57 E9 2C C2 2F 54 7B 10 4C 9A 75 49
```

Depois do XOR:

```text
uint32 tamanho do índice descompactado
zlib(index)
```

## Entrada do índice

A estrutura usada pelo repacker é:

```text
uint16  name_len
UTF-16LE name
6 bytes unknown
uint32  offset
uint32  size
4 bytes flags
uint32  uncompressed_size
uint8   header_len
header_len bytes header
```

O stream lógico é formado por:

```text
header armazenado no PIDX
+
payload físico armazenado no GPK
```

Quando `flags == DFLT`, o stream lógico precisa ser descompactado com zlib.

As demais entradas são tratadas como raw pela pipeline.

## Regras de preservação do repacker

`gpk_repack_v5_robust.py` foi construído para preservar ao máximo a estrutura original:

- mantém o prefixo/stub;
- mantém nomes e ordem das entradas;
- mantém campos desconhecidos do PIDX;
- preserva streams comprimidos originais quando o conteúdo lógico não mudou;
- preserva entradas raw;
- recompõe e valida o PIDX apenas quando necessário;
- só substitui a saída anterior depois da pós-validação.

## Observação sobre extrações externas

Algumas extrações produzidas por ferramentas externas podem conter bytes extras no fim do arquivo extraído. Por isso, um arquivo extraído não deve ser considerado automaticamente idêntico ao conteúdo lógico armazenado no GPK.

A pipeline compara o **conteúdo lógico** das entradas e não apenas nome ou tamanho externo do arquivo.

## Escopo

Estas informações não pretendem ser uma especificação completa do formato. São observações empíricas suficientes para reconstruir e validar os GPKs usados por esta pipeline.
