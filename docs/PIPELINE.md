# Pipeline de tradução de diálogos

Esta documentação cobre **somente a pipeline de tradução dos diálogos e escolhas** de School Days HQ para PT-BR.

As modificações gráficas de interface feitas separadamente em `System.GPK` não fazem parte deste fluxo.

## Visão geral

```text
ORIGINAL\Script\ENGLISH\00..05
        ↓
TOOLS\ors2xml_fixed_v5_folders.py
        ↓
XML\ORIGINAL_EN\00.xml .. 05.xml
        ↓
XML\PT_BR\00.xml .. 05.xml
        ↓
TOOLS\xml2ors_fixed_v4_ptbr_folder.py
        ↓
BUILD\Script
        ↓
TOOLS\gpk_repack_v5_robust.py
        ↓
OUTPUT\Script.GPK
```

## 1. Preparar os arquivos originais

Extraia os ORS do seu próprio `Script.GPK` e organize em:

```text
ORIGINAL\Script\ENGLISH\00
ORIGINAL\Script\ENGLISH\01
ORIGINAL\Script\ENGLISH\02
ORIGINAL\Script\ENGLISH\03
ORIGINAL\Script\ENGLISH\04
ORIGINAL\Script\ENGLISH\05
```

A estrutura e nomes devem permanecer iguais aos originais.

## 2. ORS → XML

Execute:

```bat
cd TOOLS
python ors2xml_fixed_v5_folders.py
```

Saída:

```text
XML\ORIGINAL_EN\00.xml
...
XML\ORIGINAL_EN\05.xml
```

Cada `PrintText` recebe um ID `PTxxxx` e cada `SetSELECT` recebe um ID `SELxxxx`. Esses IDs são usados para detectar exclusões, duplicações ou mudanças de ordem.

Os ORS esperados pela pipeline são tratados como **UTF-8 sem BOM** e usam **TAB** como separador de campos.

## 3. Traduzir os XMLs

Copie os XMLs gerados para:

```text
XML\PT_BR\
```

Traduza apenas:

- o texto entre `<PrintText>...</PrintText>`;
- `sel1` e `sel2` de `<SetSELECT>`;
- opcionalmente o atributo `name` de `<PrintText>` quando fizer sentido traduzir nomes genéricos.

Não altere:

- IDs;
- `name` de `<File>`;
- quantidade de elementos;
- ordem dos elementos;
- estrutura XML.

## 4. XML → ORS

Execute:

```bat
python xml2ors_fixed_v4_ptbr_folder.py
```

Antes de criar a BUILD, a ferramenta valida:

- arquivos ausentes, duplicados ou inesperados;
- contagem de `PrintText` e `SetSELECT`;
- IDs faltando, duplicados ou fora de ordem;
- TABs e quebras de linha perigosas;
- tags inesperadas;
- estrutura do XML.

A BUILD é criada em área temporária e só substitui a BUILD anterior se toda a validação passar.

Saída:

```text
BUILD\Script\
```

## 5. BUILD → Script.GPK

Coloque o `Script.GPK` original da sua própria instalação em:

```text
ORIGINAL\Script_original.GPK
```

Execute:

```bat
python gpk_repack_v5_robust.py
```

Saída:

```text
OUTPUT\Script.GPK
```

O repacker:

- usa o GPK original como base estrutural;
- preserva o prefixo/stub;
- preserva entradas raw;
- recompõe apenas entradas lógicas realmente alteradas;
- mantém nomes e ordem do PIDX;
- executa pós-validação do GPK antes de substituir uma saída anterior válida.

## 6. Teste

Copie o `Script.GPK` gerado para a pasta `Packs` do jogo, após a atualização oficial 1.02.

Para verificar se o arquivo instalado é exatamente o da BUILD:

```bat
certutil -hashfile "C:\CAMINHO\OUTPUT\Script.GPK" SHA256
certutil -hashfile "D:\JOGO\Packs\Script.GPK" SHA256
```

Os hashes devem ser iguais.
