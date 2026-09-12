<img width="1672" height="941" alt="ChatGPT Image 11 de set  de 2026, 05_04_12" src="https://github.com/user-attachments/assets/ae443712-0b3d-4735-9954-50c8bdd6d4d9" />



# School Days HQ — Tradução PT-BR

> Tradução brasileira não oficial de **School Days HQ** para PC.
>
> **Status: CONCLUÍDO**
>
> Todos os diálogos da versão trabalhada pelo projeto foram traduzidos para português brasileiro.
>
> A instalação final do patch é composta por apenas dois arquivos:
>
> ```text
> Script.GPK
> System.GPK
> ```
>
> O jogo deve estar previamente atualizado para a **versão 1.02**.

---

This project does not distribute School Days HQ or any original game files. A legally obtained copy of the game is required. All extraction and patching processes use files from the user's own installation.

## Sumário

- [Sobre o projeto](#sobre-o-projeto)
- [Status atual](#status-atual)
- [Requisitos](#requisitos)
- [Instalação](#instalação)
- [Ordem correta dos patches](#ordem-correta-dos-patches)
- [O que o patch modifica](#o-que-o-patch-modifica)
- [Desinstalação](#desinstalação)
- [Troubleshooting rápido](#troubleshooting-rápido)
- [Pipeline de desenvolvimento](#pipeline-de-desenvolvimento)
- [Estrutura do projeto](#estrutura-do-projeto)
- [ORS → XML](#ors--xml)
- [Tradução dos XMLs](#tradução-dos-xmls)
- [XML → ORS](#xml--ors)
- [BUILD → Script.GPK](#build--scriptgpk)
- [System.GPK e a fonte](#systemgpk-e-a-fonte)
- [Sistema de validação](#sistema-de-validação)
- [Debugging detalhado](#debugging-detalhado)
- [Debugging de XML](#debugging-de-xml)
- [Debugging de ORS](#debugging-de-ors)
- [Debugging de GPK](#debugging-de-gpk)
- [Debugging dentro do jogo](#debugging-dentro-do-jogo)
- [Notas técnicas sobre GPK](#notas-técnicas-sobre-gpk)
- [Checklist de release](#checklist-de-release)
- [Origem das ferramentas](#origem-das-ferramentas)
- [Uso de IA](#uso-de-ia)
- [Direitos autorais](#direitos-autorais)
- [Créditos](#créditos)

---

# Sobre o projeto

Este é um projeto **100% independente, não oficial e feito por fã**.

O objetivo foi criar uma tradução direta de **School Days HQ** para português brasileiro, preservando ao máximo a estrutura e o funcionamento original do jogo.

O projeto começou como uma tentativa de simplesmente substituir os diálogos ingleses, mas acabou evoluindo para uma pipeline completa de:

```text
extração
↓
conversão
↓
tradução
↓
validação
↓
reconstrução
↓
repack
↓
debugging
↓
teste real no jogo
```

A prioridade sempre foi evitar modificações desnecessárias no jogo.

# Status atual

```
Diálogos 00        CONCLUÍDO
Diálogos 01        CONCLUÍDO
Diálogos 02        CONCLUÍDO
Diálogos 03        CONCLUÍDO
Diálogos 04        CONCLUÍDO
Diálogos 05        CONCLUÍDO

ORS → XML          OK
XML → ORS          OK
Validação XML      OK
BUILD automática   OK
Repack Script.GPK  OK
System.GPK         OK
Teste no jogo      OK
```

## Patch final

O jogador precisa apenas de:

```
Script.GPK
System.GPK
```

e deve colocá-los na pasta:

```
School Days HQ\Packs\
```

depois da instalação da atualização 1.02.

# Requisitos

Você precisa de:

- School Days HQ para PC
- Atualização 1.02
- Patch PT-BR deste projeto
- Windows

Use uma cópia do jogo obtida legalmente. Este projeto não fornece o jogo.

# Instalação

### 1. Instale School Days HQ

Instale o jogo normalmente. Antes de aplicar qualquer patch, abra o jogo pelo menos uma vez e confirme que ele funciona.

### 2. Instale a atualização 1.02
Link da atualização: https://schooldays.us/support

A versão 1.02 é obrigatória para a versão deste patch PT-BR. Aplique a atualização antes da tradução.

Depois:

```
abra o jogo
↓
confirme que funciona
↓
feche o jogo
```

### 3. Baixe o patch PT-BR

Abra a aba **Releases** deste repositório e baixe o ZIP da versão mais recente. Dentro dele estarão:

```
Script.GPK
System.GPK
```

### 4. Localize a pasta Packs

Na instalação de School Days HQ, abra:

```
School Days HQ\
└── Packs\
```

Dentro dela já devem existir arquivos semelhantes a:

```
Script.GPK
System.GPK
Ini.GPK
...
```

### 5. Faça backup

Antes de substituir qualquer coisa, copie:

```
Script.GPK
System.GPK
```

para algum local seguro. Exemplo:

```
BACKUP_1.02\
├── Script.GPK
└── System.GPK
```

### 6. Instale a tradução

Pegue `Script.GPK` e `System.GPK` do ZIP PT-BR e copie para:

```
School Days HQ\Packs\
```

Confirme a substituição. A estrutura ficará:

```
School Days HQ\
└── Packs\
    ├── Script.GPK
    ├── System.GPK
    ├── Ini.GPK
    └── ...
```

### 7. Abra o jogo

Inicie School Days HQ normalmente. Os diálogos deverão aparecer em português brasileiro.

# Ordem correta dos patches

A ordem correta é:

```
School Days HQ
        ↓
Patch oficial 1.02
        ↓
Patch PT-BR
        ↓
Jogar
```

**Não faça:**

```
PT-BR
↓
1.02
```

porque a atualização 1.02 também modifica arquivos do jogo e pode substituir partes do patch PT-BR.

Se isso acontecer, aplique novamente `Script.GPK` + `System.GPK` depois da 1.02.

# O que o patch modifica

## Script.GPK

Este é o arquivo principal da tradução. Ele contém os scripts responsáveis por:

- diálogos
- escolhas
- eventos
- execução das cenas

A tradução modifica principalmente comandos `[PrintText]` e `[SetSELECT]`, mantendo o restante da estrutura original.

## System.GPK

A `System.GPK` incluída no patch final fornece a modificação de compatibilidade da fonte necessária para o texto em português. A versão inglesa do jogo não possui suporte adequado para diversos caracteres usados em português brasileiro. Sem essa modificação, letras podem simplesmente desaparecer.

### Limitação atual da fonte

A solução estável adotada pelo projeto prioriza fazer com que nenhuma letra desapareça. Alguns caracteres acentuados reutilizam o glifo da letra-base. Exemplos:

```
á → a
ã → a
é → e
ç → c
õ → o
```

Portanto, `você → voce` e `não → nao` pode ocorrer visualmente. Isso é uma limitação conhecida da fonte original e não significa que o diálogo esteja faltando no Script.GPK.

# Desinstalação

Feche o jogo. Restaure os arquivos que você salvou antes da instalação (`Script.GPK`, `System.GPK`) para `Packs\`.

Se não possui backup, restaure/reinstale o jogo e aplique novamente a atualização 1.02.

# Troubleshooting rápido

**O jogo continua em inglês**
Verifique `Packs\Script.GPK`. Provavelmente o arquivo PT-BR não foi copiado, foi copiado para a instalação errada, ou foi sobrescrito depois.

**Letras desaparecem**
Verifique `Packs\System.GPK`. A System.GPK do patch provavelmente não está instalada.

**O jogo abre e volta para o menu**
Possíveis causas: Script.GPK errada, versão diferente do jogo, patch 1.02 ausente, arquivo corrompido. Restaure o backup e teste novamente.

**Save antigo apresenta erro**
Salve seus arquivos de save antes dos testes. Depois de mudar uma Script.GPK, um save feito com outra versão do script pode não corresponder ao estado esperado pelo jogo. Primeiro teste: nova partida.

**Verificação por SHA-256**
Quando existir dúvida sobre qual arquivo está realmente instalado, use:

```
certutil -hashfile "C:\CAMINHO\Script.GPK" SHA256
certutil -hashfile "D:\JOGO\Packs\Script.GPK" SHA256
```

Os hashes devem ser iguais. Faça o mesmo para `System.GPK`. Nunca conclua que dois arquivos são iguais apenas porque possuem o mesmo nome.

# Pipeline de desenvolvimento

```
ORIGINAL\Script\ENGLISH\00..05
        │
        ▼
ors2xml_fixed_v5_folders.py
        │
        ▼
XML\ORIGINAL_EN
        │
        ▼
XML\PT_BR
        │
        ▼
xml2ors_fixed_v4_ptbr_folder.py
        │
        ▼
BUILD\Script
        │
        ▼
gpk_repack_v5_robust.py
        │
        ▼
OUTPUT\Script.GPK
```

A fonte possui processo separado:

```
ORIGINAL\System_original.GPK
        +
SYSTEM\FONTDATA_PTBR_SEM_ACENTOS.DAT
        │
        ▼
system_font_patch_v3_project.py
        │
        ▼
OUTPUT\System.GPK
```

# Estrutura do projeto

```
SchoolDays_PTBR\
│
├── ORIGINAL\
│   ├── Script_original.GPK
│   ├── System_original.GPK
│   │
│   └── Script\
│       ├── .DS_STORE
│       └── ENGLISH\
│           ├── .DS_STORE
│           ├── 00\
│           ├── 01\
│           ├── 02\
│           ├── 03\
│           ├── 04\
│           └── 05\
│
├── XML\
│   ├── ORIGINAL_EN\
│   │   ├── 00.xml
│   │   ├── 01.xml
│   │   ├── 02.xml
│   │   ├── 03.xml
│   │   ├── 04.xml
│   │   └── 05.xml
│   │
│   └── PT_BR\
│       ├── 00.xml
│       ├── 01.xml
│       ├── 02.xml
│       ├── 03.xml
│       ├── 04.xml
│       └── 05.xml
│
├── SYSTEM\
│   └── FONTDATA_PTBR_SEM_ACENTOS.DAT
│
├── TOOLS\
│   ├── ors2xml_fixed_v5_folders.py
│   ├── xml2ors_fixed_v4_ptbr_folder.py
│   ├── gpk_repack_v5_robust.py
│   └── system_font_patch_v3_project.py
│
├── BUILD\
│   └── Script\
│
└── OUTPUT\
    ├── Script.GPK
    └── System.GPK
```

# ORS → XML

Ferramenta: `ors2xml_fixed_v5_folders.py`

Execução:

```
cd TOOLS
python ors2xml_fixed_v5_folders.py
```

Ela lê `ORIGINAL\Script\ENGLISH\00` até `05` e gera `XML\ORIGINAL_EN\00.xml` até `05.xml`.

### Encoding dos ORS

A pipeline final trabalha com **UTF-8 sem BOM**. Durante o desenvolvimento ocorreram erros como `UnicodeDecodeError`, `shift_jis`, `byte 0x80`, mas os arquivos analisados foram posteriormente confirmados como compatíveis com UTF-8. Também foram encontrados caracteres residuais japoneses e `U+3000` (espaço ideográfico). A presença desses caracteres não significa que todo o arquivo deva ser interpretado como Shift-JIS.

### Estrutura das linhas ORS

Exemplo:

```
[PrintText]=00:32:12	Makoto	O que foi?	00:33:11;
```

Os campos são separados por **TAB**. Não substitua TABs por espaços.

### Ponto e vírgula

O texto de uma fala pode conter `;`. Por isso o parser utiliza o último ponto e vírgula da linha como terminador do comando.

### Proteção contra sobrescrita

O comando `python ors2xml_fixed_v5_folders.py` não sobrescreve automaticamente XMLs existentes. Para regenerar explicitamente:

```
python ors2xml_fixed_v5_folders.py --force
```

Use isso com cuidado.

# Tradução dos XMLs

Os XMLs originais ficam em `XML\ORIGINAL_EN`. A tradução fica em `XML\PT_BR`.

### PrintText

```xml
<PrintText id="PT0001" name="Makoto">
    Texto
</PrintText>
```

Traduza apenas o conteúdo textual.

### SetSELECT

```xml
<SetSELECT
    id="SEL0001"
    sel1="'Choice 1'"
    sel2="'Choice 2'"
/>
```

Traduza `sel1` e `sel2` sem alterar a estrutura.

### Não altere

- id de PrintText
- id de SetSELECT
- name de `<File>`
- quantidade de elementos
- ordem dos elementos
- estrutura do XML

### IDs de validação

Os XMLs atuais utilizam `PT0001`, `PT0002`, `PT0003`... e `SEL0001`, `SEL0002`... Esses IDs existem exclusivamente para debugging. Eles não são enviados ao jogo.

# XML → ORS

Ferramenta: `xml2ors_fixed_v4_ptbr_folder.py`

Execução:

```
python xml2ors_fixed_v4_ptbr_folder.py
```

Entrada: `XML\PT_BR` — Saída: `BUILD\Script`

A ferramenta compara a tradução com os ORS originais antes de gerar a BUILD.

## Sistema de validação

A pipeline detecta problemas como:

- XML inválido
- File faltando / duplicado / inesperado
- PrintText faltando / duplicado / adicional
- SetSELECT faltando / duplicado / adicional
- ID faltando / duplicado / inesperado
- ordem alterada
- tag inesperada
- TAB perigoso
- quebra de linha perigosa

### BUILD transacional

A BUILD é criada primeiro em uma área temporária:

```
BUILD temporária
↓
processar tudo
↓
validar tudo
```

Se houver qualquer erro, a BUILD nova é descartada e a BUILD anterior é preservada. Somente quando tudo passa:

```
BUILD temporária
↓
BUILD\Script
```

# BUILD → Script.GPK

Ferramenta: `gpk_repack_v5_robust.py`

Execução:

```
python gpk_repack_v5_robust.py
```

Entrada: `BUILD\Script` + `ORIGINAL\Script_original.GPK` — Saída: `OUTPUT\Script.GPK`

### Estratégia do repacker

O arquivo original é utilizado como template. A ferramenta procura preservar ordem das entries, nomes internos, caminhos, streams não modificadas, compressão, metadados, stub, PIDX e footer — substituindo somente o necessário.

### Pré-validação do repack

Antes do repack: a GPK original é lida, o PIDX é analisado, o footer é verificado, as entries são comparadas e a BUILD é validada. Arquivos faltando ou extras interrompem a operação.

### Pós-validação

Depois da criação:

```
GPK gerada
↓
aberta novamente
↓
PIDX relido
↓
conteúdo lógico extraído
↓
comparado com BUILD
```

Somente então `OUTPUT\Script.GPK` é considerado válido.

# System.GPK e a fonte

Ferramenta: `system_font_patch_v3_project.py`

Entrada: `ORIGINAL\System_original.GPK` + `SYSTEM\FONTDATA_PTBR_SEM_ACENTOS.DAT` — Saída: `OUTPUT\System.GPK`

O patcher é propositalmente conservador. Ele modifica apenas `SYSTEM/FONTDATA_ENG.DAT` no fluxo principal da tradução.

### CRASSGUI e G\r\n

Durante o desenvolvimento foi identificado que algumas extrações feitas pelo CRASSGUI acrescentam `47 0D 0A` ao fim do arquivo (em texto: `G\r\n`). Esses bytes não fazem parte do conteúdo lógico esperado. A remoção só deve ocorrer quando o tamanho = esperado + 3 e o arquivo realmente terminar em `47 0D 0A`.

# Debugging detalhado

A regra principal deste projeto é:

> **NUNCA remover uma validação só porque ela está impedindo o build.**

A validação geralmente está mostrando que alguma coisa anterior está errada. O fluxo correto é:

```
erro
↓
reproduzir
↓
identificar a camada
↓
comparar original/modificado
↓
corrigir origem
↓
validar
↓
build
↓
repack
↓
testar
```

### As camadas do projeto

```
XML
↓
ORS
↓
BUILD
↓
GPK
↓
arquivo instalado
↓
jogo
```

Antes de culpar o jogo, responda: O XML está correto? O ORS gerado está correto? A BUILD está correta? O GPK contém o arquivo correto? A GPK instalada é a mesma?

# Debugging de XML

**mismatched tag** — a linha mostrada pelo parser nem sempre é onde o problema começou. Pode existir anteriormente um `<File>` sem `</File>` correspondente.

**File aberto e não fechado** — comece a investigação no `<File>` indicado, e não apenas no fim do XML.

**invalid token** — verifique `&`, `<`, `>`, aspas, tags cortadas, caracteres de controle. Um `&` literal deve normalmente ser `&amp;`.

**PrintText diferente** (ex.: ORS=16, XML=14) — indica que falas foram apagadas, fundidas, quebradas ou deixaram de ser reconhecidas. Não force o build.

**SetSELECT diferente** — a quantidade deve continuar idêntica à estrutura original.

# Debugging de ORS

**Arquivo não abre como UTF-8** — não conclua imediatamente que é Shift-JIS. Verifique encoding real, BOM, caracteres japoneses residuais, U+3000, bytes isolados, TAB perdido. Se `[TAB]` for convertido para espaços, o ORS pode parecer legível visualmente e ainda assim estar estruturalmente errado.

**Texto com `;`** — o parser não deve dividir uma fala no primeiro `;`. A pipeline utiliza o último terminador da linha.

# Debugging de GPK

**Jogo não abre** — verifique GPK base correta, BUILD correta, footer, PIDX, offsets, streams.

**Jogo volta ao menu** — pode indicar archive legível mas script interno inválido. Volte para BUILD → ORS → XML.

**STKFile0PIDX ausente** — não faça repack. O arquivo pode estar truncado, incompatível ou em formato diferente.

# Debugging dentro do jogo

Para cada release, teste pelo menos: início do jogo, diálogo, escolha, mudança de cena, save, load, fechar, abrir novamente.

### Teste de uma cena específica

```
cena com problema
↓
descobrir ORS
↓
descobrir pasta 00–05
↓
conferir XML
↓
conferir ORS gerado
↓
conferir BUILD
↓
conferir GPK
↓
conferir hash instalado
↓
jogo
```

### Uma alteração por vez

Durante debugging: 1 modificação, 1 build, 1 teste. Esse princípio foi essencial durante o desenvolvimento.

# Notas técnicas sobre GPK

O formato analisado possui um prefixo/stub antes do conteúdo principal. Valor observado: `0x1400`.

### Footer

Estrutura encontrada:

```
STKFile0PIDX
<uint32 tamanho>
STKFile0PACKFILE
PIDX
```

O índice utiliza `uint32 tamanho descompactado + zlib(index)`, seguido do XOR utilizado pelo formato.

### Chave XOR observada

```
82 EE 1D B3 57 E9 2C C2
2F 54 7B 10 4C 9A 75 49
```

### Estrutura das entries

```
uint16 tamanho do nome
UTF-16LE name
6 bytes desconhecidos
uint32 offset
uint32 size
4 bytes flags
uint32 uncompressed size
uint8 header_len
header
```

### Streams DFLT

Quando `flags = DFLT`, a stream utiliza zlib.

### Header armazenado no PIDX

Particularidade importante: stream completa = header armazenado no PIDX + payload físico do GPK. Ignorar isso pode gerar arquivos aparentemente válidos, mas internamente incorretos.

# Checklist de release

```
[ ] jogo 1.02
[ ] 00.xml traduzido
[ ] 01.xml traduzido
[ ] 02.xml traduzido
[ ] 03.xml traduzido
[ ] 04.xml traduzido
[ ] 05.xml traduzido

[ ] XML válido
[ ] PrintText validado
[ ] SetSELECT validado
[ ] IDs validados

[ ] BUILD criada
[ ] Script.GPK criada
[ ] pós-validação passou

[ ] System.GPK criada
[ ] FONTDATA validada

[ ] jogo inicia
[ ] diálogos funcionam
[ ] escolhas funcionam
[ ] save funciona
[ ] load funciona

[ ] hashes SHA-256 registrados
[ ] ZIP final conferido
```

### Estrutura da release

```
SchoolDaysHQ_PTBR_v1.0.zip
│
├── Script.GPK
├── System.GPK
└── README.txt
```

Os dois `.GPK` são instalados em `Packs\`.

# Origem das ferramentas

Este projeto utilizou como base:

**21-ko — School-Days-Translation-Tools**
https://github.com/21-ko/School-Days-Translation-Tools

A partir dessa base foram feitas diversas modificações e melhorias, entre elas: pipeline reorganizada, caminhos automáticos, XML original separado, XML PT-BR separado, proteção contra sobrescrita, IDs de validação, validação estrutural, BUILD transacional, repack robusto, pós-validação, patch de fonte, debugging e documentação.

Respeite a licença do projeto original ao reutilizar código derivado.

# Uso de IA

Ferramentas de inteligência artificial participaram do desenvolvimento. Foram utilizadas para: análise de formatos, debugging, criação de scripts, revisão de scripts, análise de XML, análise de ORS, análise do formato GPK, validações e documentação.

A tradução dos XMLs para PT-BR contou com auxílio do **Google Gemini**.

A parte técnica, debugging e documentação também contou com assistência de IA sob supervisão do responsável pelo projeto.

O resultado foi construído através de: ferramentas existentes + trabalho humano + tradução assistida + análise assistida + testes reais no jogo + correções sucessivas.

# Direitos autorais

School Days HQ e seus recursos pertencem aos respectivos detentores dos direitos autorais.

Este projeto:

- não é oficial
- não possui vínculo com os desenvolvedores
- não reivindica propriedade sobre o jogo

Arquivos `.GPK` completos podem conter material protegido por direitos autorais. Antes de publicar ou espelhar arquivos completos do jogo, confirme se você possui autorização para essa forma de redistribuição.

Quando isso não estiver claro, prefira distribuir: patch diferencial, patcher, dados próprios da tradução, scripts, documentação — e solicitar que o usuário forneça localmente os arquivos originais de uma cópia legalmente obtida.

A mesma cautela se aplica à redistribuição de patches oficiais.

# Créditos

### Direção, testes e supervisão

**Suzu** — direção do projeto, organização, testes reais, debugging, validação manual, decisões técnicas finais.

### Ferramentas originais

**21-ko** — School-Days-Translation-Tools
https://github.com/21-ko/School-Days-Translation-Tools

### Tradução PT-BR

Tradução dos diálogos realizada com auxílio de **Google Gemini**.

### Desenvolvimento assistido por IA

Análise técnica, debugging, evolução da pipeline e documentação realizadas com auxílio de inteligência artificial sob supervisão do responsável pelo projeto.

---

## Projeto concluído

Depois de: extração dos ORS → erros de encoding → conversão para XML → tradução → XML quebrado → mismatched tags → validação → reconstrução dos ORS → repack do Script.GPK → análise do PIDX → problemas de fonte → patch da System.GPK → testes reais no jogo —

o fluxo final ficou:

```
School Days HQ
↓
Patch 1.02
↓
Script.GPK PT-BR
+
System.GPK PT-BR
↓
Packs\
↓
School Days HQ em português brasileiro
```

E a pipeline permanece:

```
ORS
↓
XML
↓
PT-BR
↓
validação
↓
ORS
↓
BUILD
↓
GPK
↓
teste
↓
release
```

**Projeto concluído.**
