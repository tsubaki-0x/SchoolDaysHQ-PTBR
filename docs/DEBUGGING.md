# Debugging da pipeline

A regra usada durante o projeto é simples:

```text
não remover uma validação apenas para fazer a BUILD passar
```

Quando algo falhar, descubra em qual camada o problema apareceu:

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

## XML

Problemas comuns:

### `mismatched tag`

Indica XML malformado, por exemplo um `<File>` sem fechamento correspondente.

Valide o XML antes de qualquer conversão.

### `PrintText diferente`

A quantidade de `<PrintText>` do XML não corresponde à quantidade de comandos `[PrintText]` do ORS original.

Possíveis causas:

- fala apagada;
- fala duplicada;
- estrutura XML quebrada;
- `<File>` incorreto.

### `SetSELECT diferente`

Mesmo princípio, mas para escolhas.

### IDs inválidos

IDs `PTxxxx` ou `SELxxxx` faltando, duplicados ou fora de ordem indicam que a estrutura da tradução foi alterada.

## ORS

Os ORS usados pela pipeline são tratados como UTF-8 sem BOM e usam TAB como separador de campos.

Não substitua TABs por espaços.

O parser considera o **último `;` da linha** como terminador do comando, permitindo que o texto da fala contenha ponto e vírgula.

## BUILD

`xml2ors_fixed_v4_ptbr_folder.py` cria a BUILD de forma transacional:

```text
BUILD temporária
↓
processar tudo
↓
validar tudo
↓
substituir BUILD anterior
```

Se a pré-validação falhar, a BUILD anterior permanece intacta.

## GPK

`gpk_repack_v5_robust.py` também usa arquivo temporário e pós-validação.

Antes de aceitar a saída, verifique:

- quantidade de entradas;
- nomes e ordem do PIDX;
- conteúdo lógico das entradas DFLT;
- preservação das entradas raw;
- prefixo/stub original;
- footer `STKFile0PIDX` / `STKFile0PACKFILE`.

## Dentro do jogo

### Jogo continua em inglês

Verifique se o `Script.GPK` correto foi realmente copiado para `Packs\`.

### Letras desaparecem

Verifique a `System.GPK` usada na instalação final do patch.

### Jogo abre e volta para o menu

Possíveis causas:

- `Script.GPK` incompatível;
- jogo sem atualização 1.02;
- GPK corrompido;
- estrutura do script alterada.

Restaure o backup e teste novamente.

### Save antigo apresenta comportamento estranho

Faça primeiro o teste com nova partida. Saves antigos podem apontar para estados de script produzidos por outra versão do `Script.GPK`.

## Comparação por SHA-256

Nunca conclua que dois arquivos são iguais apenas porque têm o mesmo nome.

Use:

```bat
certutil -hashfile "C:\CAMINHO\Script.GPK" SHA256
certutil -hashfile "D:\JOGO\Packs\Script.GPK" SHA256
```

Faça o mesmo para `System.GPK` quando necessário.

## Método de teste recomendado

Durante debugging:

```text
1 alteração
1 BUILD
1 repack
1 teste
```

Isso torna a origem de uma regressão muito mais fácil de localizar.
