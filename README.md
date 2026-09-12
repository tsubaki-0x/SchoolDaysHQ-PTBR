<img width="1672" height="941" alt="School Days HQ PT-BR" src="https://github.com/user-attachments/assets/ae443712-0b3d-4735-9954-50c8bdd6d4d9" />

# School Days HQ — Tradução PT-BR

Tradução brasileira não oficial de **School Days HQ** para PC.

> **Status: concluído**
>
> Compatibilidade: **School Days HQ v1.02**.
>
> O patch de usuário final é composto por `Script.GPK` e `System.GPK`.

Este projeto não distribui o jogo completo nem arquivos GPK originais. Os arquivos proprietários necessários para reconstrução devem vir da instalação do próprio usuário.

## Escopo do repositório

A **pipeline documentada neste repositório é dedicada à tradução dos diálogos e escolhas para PT-BR**, culminando na reconstrução do `Script.GPK`.

As modificações gráficas de interface feitas separadamente em `System.GPK` — por exemplo TITLE, MENUBAR, OPTION, SAVELOAD, BACKLOG, EXIT, ROUTEMAP, REPLAY e SCREEN/TELOP — **não fazem parte desta pipeline de diálogos**. Elas são um patch separado e não são necessárias para reproduzir o fluxo ORS → XML → ORS → Script.GPK.

O utilitário de fonte em `TOOLS/system_font_patch_v3_project.py` é mantido como ferramenta auxiliar de compatibilidade da versão final do patch, não como parte do fluxo principal de tradução dos diálogos.

## Instalação

1. Instale **School Days HQ** e confirme que o jogo abre normalmente.
2. Aplique a atualização oficial **1.02**: https://schooldays.us/support
3. Faça backup de `Script.GPK` e `System.GPK` da pasta `Packs\`.
4. Baixe a versão mais recente em **Releases**:
   https://github.com/tsubaki-0x/SchoolDaysHQ-PTBR/releases
5. Extraia o pacote e copie `Script.GPK` e `System.GPK` para:

```text
School Days HQ\Packs\
```

6. Confirme a substituição e inicie o jogo.

A ordem correta é:

```text
School Days HQ
        ↓
Atualização oficial 1.02
        ↓
Patch PT-BR
        ↓
Jogar
```

Se a atualização 1.02 for aplicada novamente depois do PT-BR, reaplique o patch PT-BR.

### Tutorial em vídeo

<p align="center">
  <a href="https://www.youtube.com/watch?v=zgHaBVeXS-Q">
    <img src="https://img.youtube.com/vi/zgHaBVeXS-Q/maxresdefault.jpg" alt="Tutorial de instalação — School Days HQ PT-BR" width="720">
  </a>
</p>

<p align="center"><strong><a href="https://www.youtube.com/watch?v=zgHaBVeXS-Q">Assistir ao tutorial de instalação</a></strong></p>

## Pipeline de diálogos

```text
ORIGINAL\Script\ENGLISH\00..05
        │
        ▼
TOOLS\ors2xml_fixed_v5_folders.py
        │
        ▼
XML\ORIGINAL_EN\00.xml .. 05.xml
        │
        ▼
XML\PT_BR\00.xml .. 05.xml
        │
        ▼
TOOLS\xml2ors_fixed_v4_ptbr_folder.py
        │
        ▼
BUILD\Script
        │
        ▼
TOOLS\gpk_repack_v5_robust.py
        │
        ▼
OUTPUT\Script.GPK
```

Os arquivos em `XML\ORIGINAL_EN` são **gerados localmente** a partir da instalação do usuário e não são versionados no repositório.

### Execução básica

Coloque os arquivos extraídos do seu próprio `Script.GPK` em:

```text
ORIGINAL\Script\ENGLISH\00
ORIGINAL\Script\ENGLISH\01
ORIGINAL\Script\ENGLISH\02
ORIGINAL\Script\ENGLISH\03
ORIGINAL\Script\ENGLISH\04
ORIGINAL\Script\ENGLISH\05
```

Depois execute:

```bat
cd TOOLS
python ors2xml_fixed_v5_folders.py
python xml2ors_fixed_v4_ptbr_folder.py
python gpk_repack_v5_robust.py
```

Para o repack automático, coloque também o `Script.GPK` da sua própria instalação em:

```text
ORIGINAL\Script_original.GPK
```

O arquivo final será criado em:

```text
OUTPUT\Script.GPK
```

## Validações principais

A pipeline foi construída para falhar antes de substituir uma BUILD válida quando encontra problemas. Entre as verificações estão:

- XML inválido;
- `<File>` ausente, duplicado ou inesperado;
- `PrintText` e `SetSELECT` ausentes ou adicionais;
- IDs `PTxxxx` e `SELxxxx` fora de ordem ou duplicados;
- TABs e quebras de linha perigosas;
- quantidade de comandos diferente do ORS original;
- estrutura e ordem do PIDX alteradas;
- conteúdo lógico do GPK gerado diferente da BUILD;
- preservação de entradas raw e do prefixo original do GPK.

Regra de debugging usada no projeto:

```text
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

Quando houver dúvida sobre qual arquivo está instalado, compare SHA-256:

```bat
certutil -hashfile "C:\CAMINHO\Script.GPK" SHA256
certutil -hashfile "D:\JOGO\Packs\Script.GPK" SHA256
```

## Estrutura do repositório

```text
SchoolDaysHQ-PTBR\
├── ORIGINAL\          # entradas locais do usuário; arquivos do jogo não são versionados
├── XML\
│   ├── ORIGINAL_EN\   # gerado localmente
│   └── PT_BR\         # tradução PT-BR
├── TOOLS\             # pipeline e ferramentas de validação/repack
├── SYSTEM\            # área auxiliar; sem assets proprietários versionados
├── BUILD\             # saída intermediária local
├── OUTPUT\            # GPKs gerados localmente
├── docs\
├── .gitignore
├── LICENSE
└── README.md
```

## Documentação técnica

- [Pipeline completa](docs/PIPELINE.md)
- [Debugging](docs/DEBUGGING.md)
- [Notas sobre o formato GPK](docs/GPK_FORMAT.md)

## Origem das ferramentas

A base inicial de ferramentas utilizada no projeto é:

**21-ko — School-Days-Translation-Tools**  
https://github.com/21-ko/School-Days-Translation-Tools

O projeto original é licenciado sob **Apache License 2.0**. Esta versão contém adaptações para o fluxo PT-BR, validação estrutural, BUILD transacional, repack robusto e diagnóstico adicional.

## Uso de IA

Ferramentas de IA foram utilizadas como apoio na análise técnica, debugging, criação/revisão de scripts e documentação. A tradução dos diálogos também contou com auxílio do Google Gemini. As decisões finais e testes no jogo foram realizados pelo responsável pelo projeto.

## Créditos

**Suzu / tsubaki-0x** — direção do projeto, tradução, organização, debugging, testes e validação final.  
**21-ko** — ferramentas originais que serviram de base para parte da pipeline.  
**Google Gemini / OpenAI** — apoio durante tradução, análise e desenvolvimento.

## Direitos autorais

Este é um projeto independente de fã e não possui vínculo oficial com os desenvolvedores ou publicadores de **School Days HQ**. Os direitos sobre o jogo e seus recursos pertencem aos respectivos detentores.

A licença deste repositório cobre o **código-fonte e a documentação próprios/derivados conforme indicado**, não concede direitos sobre School Days HQ nem sobre seus assets, textos, marcas ou demais conteúdos proprietários.