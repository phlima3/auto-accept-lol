# Auto-Accept LoL

Auto-aceitar partidas no League of Legends. Roda silenciosamente na bandeja do sistema (system tray) do Windows.

## Como funciona

O script usa a **LCU API** (API local do cliente do League of Legends) para detectar quando uma partida é encontrada e aceitá-la automaticamente — sem reconhecimento de imagem, sem macros.

## Download

Baixe o executável pronto na aba [Releases](../../releases).

## Uso

1. Abra o cliente do League of Legends
2. Execute `AutoAcceptLoL.exe`
3. O ícone aparece na bandeja do sistema (perto do relógio)
4. Pronto — as partidas serão aceitas automaticamente
5. Para fechar: clique direito no ícone > **Sair**

## Rodando a partir do código-fonte

### Pré-requisitos

- Python 3.10+

### Instalação

```bash
pip install -r requirements.txt
```

### Execução

```bash
pythonw auto_accept.py
```

> Use `pythonw` para rodar sem abrir janela de terminal.

### Gerar o .exe

```bash
pyinstaller --onefile --noconsole --name "AutoAcceptLoL" --icon=icon.ico --add-data "tray_icon.png;." auto_accept.py
```

O executável será gerado em `dist/AutoAcceptLoL.exe`.

## Configuração

Por padrão, o script procura o League of Legends em:

```
D:\Riot Games\League of Legends
```

Se o seu LoL estiver em outro caminho, edite a variável `LOCKFILE_PATH` no arquivo `auto_accept.py`.

## Licença

MIT
