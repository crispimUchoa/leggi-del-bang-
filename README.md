# Leggi del Bang!

Aplicação Flask simples para criar, visualizar e editar cartas inspiradas em Bang!.

## Rodar localmente

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Acesse: http://127.0.0.1:5000/cartas

## Deploy no Render

Build Command:

```bash
pip install -r requirements.txt
```

Start Command:

```bash
gunicorn app:app
```

Para SQLite persistente no Render, configure um Persistent Disk e crie a variável de ambiente:

```bash
DATABASE_PATH=/var/data/leggi_del_bang.db
```

O caminho `/var/data` deve corresponder ao Mount Path do disco criado no Render.
# leggi-del-bang-
