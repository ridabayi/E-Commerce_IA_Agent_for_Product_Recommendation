import hvac
import os

VAULT_ADDR = "http://127.0.0.1:8200"
VAULT_TOKEN = os.environ.get("VAULT_TOKEN")

if not VAULT_TOKEN:
    raise RuntimeError("❌ VAULT_TOKEN non défini dans les variables d’environnement PowerShell ou terminal.")

client = hvac.Client(url=VAULT_ADDR, token=VAULT_TOKEN)

try:
    secret = client.secrets.kv.v2.read_secret_version(path="apis")["data"]["data"]
except Exception as e:
    raise RuntimeError(f"❌ Erreur de lecture des secrets Vault : {e}")

# Injection dans os.environ
for key, value in secret.items():
    if value:
        os.environ[key] = value

"""
from load_secrets import *  # charge et injecte automatiquement les clés dans os.environ
# Exemple d’utilisation
import os
print("🔐 GROQ =", os.environ.get("GROQ_API_KEY"))
"""