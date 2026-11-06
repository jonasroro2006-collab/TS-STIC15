import csv
import json
import os
import secrets
import urllib.request
import urllib.error

URL = os.environ["SUPABASE_URL"]
SECRET = os.environ["SUPABASE_SECRET"]
DOMAINE = "stic-chat.com"
NOMBRE = 50
ALPHABET = "abcdefghjkmnpqrstuvwxyz23456789"


def generer_code(longueur=8):
    return "".join(secrets.choice(ALPHABET) for _ in range(longueur))


def requete(methode, chemin, corps=None, extra=None):
    en_tetes = {
        "apikey": SECRET,
        "Authorization": f"Bearer {SECRET}",
        "Content-Type": "application/json",
    }
    en_tetes.update(extra or {})
    donnees = json.dumps(corps).encode() if corps is not None else None
    req = urllib.request.Request(URL + chemin, data=donnees, headers=en_tetes, method=methode)
    try:
        with urllib.request.urlopen(req) as rep:
            return json.loads(rep.read() or b"{}")
    except urllib.error.HTTPError as e:
        raise SystemExit(f"Erreur {e.code} : {e.read().decode()}")


def main():
    with open("codes_eleves.csv", "w", newline="", encoding="utf-8-sig") as sortie:
        ecrivain = csv.writer(sortie)
        ecrivain.writerow(["identifiant", "code"])

        for i in range(1, NOMBRE + 1):
            identifiant = f"eleve{i:02d}"
            code = generer_code()

            compte = requete("POST", "/auth/v1/admin/users", {
                "email": f"{identifiant}@{DOMAINE}",
                "password": code,
                "email_confirm": True,
            })
            requete("POST", "/rest/v1/profils", {
                "id": compte["id"],
                "nom_affiche": f"Élève {i:02d}",
            }, {"Prefer": "return=minimal"})

            ecrivain.writerow([identifiant, code])
            print("Créé :", identifiant)


if __name__ == "__main__":
    main()