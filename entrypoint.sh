#!/bin/sh
set -e

echo "Aguardando o banco de dados ficar disponivel..."
python - <<'PYEOF'
import os
import sys
import time

import psycopg2

for attempt in range(30):
    try:
        conn = psycopg2.connect(
            dbname=os.environ["POSTGRES_DB"],
            user=os.environ["POSTGRES_USER"],
            password=os.environ["POSTGRES_PASSWORD"],
            host=os.environ["POSTGRES_HOST"],
            port=os.environ["POSTGRES_PORT"],
        )
        conn.close()
        print("Banco de dados disponivel!")
        sys.exit(0)
    except psycopg2.OperationalError:
        print(f"Banco indisponivel (tentativa {attempt + 1}/30), tentando novamente em 1s...")
        time.sleep(1)

print("Nao foi possivel conectar ao banco de dados.")
sys.exit(1)
PYEOF

python manage.py migrate --noinput
exec python manage.py runserver 0.0.0.0:8000
