"""
Genera src/fixtures/data.json a partire dal CSV del report adempimenti
(Report adempimenti di fine anno - Programmi svolti).

Uso:
    cd python
    python parse_csv.py

Produce:
    ../src/fixtures/data.json          -> dati consumati dalla web app
    ./normalization_review.md          -> tabella di revisione (originale -> normalizzato)
"""

import csv
import json
import os
import re
from collections import defaultdict

# --- percorsi ---------------------------------------------------------------
BASE = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(
    BASE, "..", "csv",
    "Report adempimenti di fine anno 25_26 - Programmi svolti.csv",
)
OUT_JSON = os.path.join(BASE, "..", "src", "fixtures", "data.json")
OUT_REVIEW = os.path.join(BASE, "normalization_review.md")


# --- normalizzazione MATERIE ------------------------------------------------
# chiave: forma "canonicalizzata" (maiuscolo, senza accenti/punteggiatura/spazi)
# valore: etichetta finale mostrata nelle card.
def _matkey(s):
    s = s.upper()
    s = (s.replace("À", "A").replace("È", "E").replace("É", "E")
           .replace("Ì", "I").replace("Ò", "O").replace("Ù", "U")
           .replace("'", ""))
    return re.sub(r"[^A-Z0-9]", "", s)


# raw label -> etichetta canonica
MATERIA_MAP_RAW = {
    "Antologia": "Antologia",
    "Biologia": "Biologia",
    "Chimica": "Chimica",
    "Chimica Analitica": "Chimica Analitica",
    "Chimica e laboratorio": "Chimica e Laboratorio",
    "CHIMICA ORGANICA E BIOCHIMICA": "Chimica Organica e Biochimica",
    "DIRITTO ED ECONOMIA": "Diritto ed Economia",
    "Diritto/Economia": "Diritto ed Economia",
    "Diritto ed Economia Politica": "Diritto ed Economia Politica",
    "Diritto/Economia Politica": "Diritto ed Economia Politica",
    "Educazione Civica": "Educazione Civica",
    "Elettrotecnica": "Elettrotecnica",
    "Elettronica ed Elettrotecnica": "Elettrotecnica ed Elettronica",
    "ELETTROTECNICA ED ELETTRONICA": "Elettrotecnica ed Elettronica",
    "FISICA e LABORATORIO": "Fisica e Laboratorio",
    "Geografia": "Geografia",
    "Geografia generale ed economica": "Geografia Generale ed Economica",
    "GEOPEDOLOGIA, ECONOMIA ED ESTIMO": "Geopedologia, Economia ed Estimo",
    "GESTIONE E SICUREZZA CANTIERE": "Gestione e Sicurezza del Cantiere",
    "INFORMATICA": "Informatica",
    "INGLESE": "Inglese",
    "LINGUA INGLESE": "Inglese",
    "LINGUA E CIVILTA' INGLESE": "Inglese",
    "Italiano": "Italiano",
    "Italiano (Grammatica)": "Italiano",
    "ITALIANO, LINGUA e LETTERATURA": "Italiano",
    "LINGUA E LETTERATURA ITALIANA": "Italiano",
    "MATEMATICA": "Matematica",
    "MATEMATICA E COMPLEMENTI": "Matematica e Complementi di Matematica",
    "MATEMATICA E COMPLEMENTI DI MATEMATICA": "Matematica e Complementi di Matematica",
    "Progettazione, Costruzioni e Impianti": "Progettazione, Costruzioni e Impianti",
    "PROGETTAZIONE, COSTRUZIONI, IMPIANTI": "Progettazione, Costruzioni e Impianti",
    "RELIGIONE CATTOLICA": "Religione Cattolica",
    "Religione cattolica/Educazione civica": "Religione Cattolica/Educazione Civica",
    "Scienze della Terra": "Scienze della Terra",
    "SCIENZE INTEGRATE (SCIENZE DELLA TERRA)": "Scienze della Terra",
    "SCIENZE E TECNOLOGIE APPLICATE": "Scienze e Tecnologie Applicate",
    "Scienze e Tecnologie Applicate (STA)": "Scienze e Tecnologie Applicate",
    "STA": "Scienze e Tecnologie Applicate",
    "Scienze Integrate (Biologia)": "Scienze Integrate (Biologia)",
    "SCIENZE INTEGRATE (CHIMICA)": "Scienze Integrate (Chimica)",
    "SCIENZE INTEGRATE (FISICA)": "Scienze Integrate (Fisica)",
    "SCIENZE INTEGRATE - FISICA": "Scienze Integrate (Fisica)",
    "SCIENZE MOTORIE": "Scienze Motorie e Sportive",
    "SCIENZE MOTORIE E SPORTIVE": "Scienze Motorie e Sportive",
    "Sistemi": "Sistemi Automatici",
    "Sistemi Automatici": "Sistemi Automatici",
    "Sistemi Automatici con Laboratorio": "Sistemi Automatici",
    "SISTEMI e RETI": "Sistemi e Reti",
    "STORIA": "Storia",
    "T.P.S.E.E.": "TPSEE",
    "TPSEE": "TPSEE",
    "TPSIT": "TPSIT",
    "Tecnologia e Tecniche di Rappresentazione Grafica":
        "Tecnologie e Tecniche di Rappresentazione Grafica",
    "Tecnologie e Tecniche di Rappresentazione Grafica":
        "Tecnologie e Tecniche di Rappresentazione Grafica",
    "TTRG": "Tecnologie e Tecniche di Rappresentazione Grafica",
    "Tecnologie chimiche industriali e laboratorio":
        "Tecnologie Chimiche Industriali e Laboratorio",
    "TECNOLOGIE INFORMATICHE": "Tecnologie Informatiche",
    "Telecomunicazioni": "Telecomunicazioni",
    "TOPOGRAFIA": "Topografia",
}
MATERIA_MAP = {_matkey(k): v for k, v in MATERIA_MAP_RAW.items()}


def norm_materia(raw):
    s = (raw or "").strip()
    if s in ("", "-"):
        return ""
    key = _matkey(s)
    if key in MATERIA_MAP:
        return MATERIA_MAP[key]
    # fallback: Title Case, segnalata come non mappata
    return s.title()


# --- normalizzazione CLASSI -------------------------------------------------
# override espliciti per casi ambigui o irregolari (raw esatto -> canonico)
# Casi con doppia lettera in conflitto (lettera dopo l'anno vs lettera della
# sigla). Scelta: vince la lettera della sigla (notazione ITCA/B, ITIAC = sez.
# in coda). Elencati anche in FORCE_FLAG per la revisione manuale.
CLASS_OVERRIDE = {
    "3A ITCA/B": "3ITCAB",
    "4A ITCA/A": "4ITCAA",  # concordi (A e A): non ambiguo
    "4A ITCA/B": "4ITCAB",
    "4A ITIAC": "4ITIAC",
    "5a ITIAC": "5ITIAC",
}
FORCE_FLAG = {"3A ITCA/B", "4A ITCA/B", "4A ITIAC", "5a ITIAC"}

WORD_TO_YEAR = {"PRIMA": "1", "SECONDA": "2", "TERZA": "3",
                "QUARTA": "4", "QUINTA": "5"}
ROMAN = {"III": "3", "II": "2", "IV": "4", "V": "5", "I": "1"}
ARTIC_CODES = ["ITETS", "ITCA", "ITCM", "ITEC", "ITES", "ITET", "ITIA", "CAT"]
SECTIONS = set("ABCDEFGHIL")
NOISE = ["ITT PANETTI PITAGORA", "PANETTI PITAGORA",
         "INFORMATICA TELECOMUNICAZIONI", "SEZIONE", "SEZ",
         "ELETTROTECNICA", "INFORMATICA", "ITT", "IT"]


def norm_class(raw):
    s = (raw or "").strip()
    if s in ("", "-"):
        return ("", False)
    if s in CLASS_OVERRIDE:
        return (CLASS_OVERRIDE[s], False)

    u = s.upper()
    u = u.replace("_", " ").replace("/", " ").replace("-", " ")
    u = u.replace("ª", " ").replace("°", " ").replace("^", " ").replace(".", " ")
    for w in NOISE:
        u = re.sub(r"\b" + re.escape(w) + r"\b", " ", u)
    u = re.sub(r"\s+", " ", u).strip()
    tokens = u.split()
    if not tokens:
        return ("", True)

    # --- anno ---
    year = None
    first = tokens[0]
    if first in WORD_TO_YEAR:
        year = WORD_TO_YEAR[first]
        tokens = tokens[1:]
    else:
        m = re.match(r"^(III|II|IV|V|I)(.*)$", first)
        m2 = re.match(r"^([1-5])(.*)$", first)
        if m:
            year = ROMAN[m.group(1)]
            rest = m.group(2)
            tokens = ([rest] if rest else []) + tokens[1:]
        elif m2:
            year = m2.group(1)
            rest = m2.group(2)
            tokens = ([rest] if rest else []) + tokens[1:]
    if year is None:
        return (s, True)  # anno non riconosciuto -> verifica

    # --- articolazione + sezione dal resto ---
    rest = "".join(tokens)
    artic = ""
    for code in ARTIC_CODES:
        if code in rest:
            artic = code
            rest = rest.replace(code, "", 1)
            break
    letters = [ch for ch in rest if ch in SECTIONS]
    ambiguous = len([ch for ch in rest if ch.isalpha()]) != len(letters) \
        or len(letters) > 1
    section = letters[0] if letters else ""

    canon = f"{year}{artic}{section}"
    return (canon, ambiguous)


# --- teacher ----------------------------------------------------------------
def norm_teacher(cognome):
    c = (cognome or "").strip()
    return [c.title()] if c else []


# --- link (mantiene /view cosi' com'e') -------------------------------------
def norm_href(link):
    return (link or "").strip()


# --- main -------------------------------------------------------------------
def main():
    with open(CSV_PATH, encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))

    out = []
    review_class = defaultdict(set)   # canonico -> {raw}
    review_mat = defaultdict(set)
    flagged_class = set()
    unmapped_mat = set()

    for r in rows:
        raw_c = r["Classe"].strip()
        raw_m = r["Materia"].strip()
        c, amb = norm_class(raw_c)
        m = norm_materia(raw_m)

        review_class[c].add(raw_c)
        review_mat[m].add(raw_m)
        if amb or raw_c in FORCE_FLAG:
            flagged_class.add(raw_c)
        if raw_m not in ("", "-") and _matkey(raw_m) not in MATERIA_MAP:
            unmapped_mat.add(raw_m)

        # scarta i record senza NE' classe NE' materia (card vuote)
        if not c and not m:
            continue

        out.append({
            "c": c,
            "name": m,
            "teachers": norm_teacher(r["Cognome"]),
            "href": norm_href(r["Link al documento"]),
            "validita": r["Stima validità"].strip(),
        })

    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)

    # --- file di revisione ---
    lines = ["# Revisione normalizzazione\n"]
    lines.append(f"Totale record: **{len(out)}**\n")

    if flagged_class:
        lines.append("## ⚠️ Classi AMBIGUE (verifica manuale)\n")
        for raw in sorted(flagged_class):
            c, _ = norm_class(raw)
            lines.append(f"- `{raw}` → `{c}`")
        lines.append("")

    if unmapped_mat:
        lines.append("## ⚠️ Materie NON mappate (fallback Title Case)\n")
        for raw in sorted(unmapped_mat):
            lines.append(f"- `{raw}` → `{norm_materia(raw)}`")
        lines.append("")

    lines.append("## Classi: canonico ← varianti\n")
    for c in sorted(review_class):
        variants = ", ".join(f"`{v}`" for v in sorted(review_class[c]))
        lines.append(f"- **{c or '(vuoto)'}** ← {variants}")
    lines.append("\n## Materie: canonico ← varianti\n")
    for m in sorted(review_mat):
        variants = ", ".join(f"`{v}`" for v in sorted(review_mat[m]))
        lines.append(f"- **{m or '(vuoto)'}** ← {variants}")

    with open(OUT_REVIEW, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))

    print(f"Scritti {len(out)} record in {OUT_JSON}")
    print(f"Classi canoniche: {len(review_class)} | Materie canoniche: {len(review_mat)}")
    print(f"Classi ambigue: {len(flagged_class)} | Materie non mappate: {len(unmapped_mat)}")
    print(f"Revisione: {OUT_REVIEW}")


if __name__ == "__main__":
    main()
