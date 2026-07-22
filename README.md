# programmi-svolti
![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)


Questo progetto è stato utilizzato per creare la lista di programmi svolti per l'a.s. 2025/26 dell'ITT Panetti Pitagora di Bari.

È un'applicazione web formata da un'unica pagina con un campo di ricerca che filtra una serie di card.
L'applicazione è scritta in React partendo dallo scheletro di default di web-app che `create-react-app` mette a disposizione.


## Front-End

L'applicazione front-end è un semplice elenco di card filtrabili mediante un campo di testo. I dati vengono caricati da una fixture json che si trova in `/src/fixtures/data.json`, generata dallo script Python presente in `/python/parse_csv.py`.

La struttura dati presente nella fixture json non è altro che un array di oggetti; ogni oggetto è fatto in questa maniera:

```json
  {
    "c": "1A",
    "name": "Matematica",
    "teachers": [
      "Spadone"
    ],
    "href": "https://drive.google.com/file/d/18K8iMYIl_Gg0ktF_bOnzJdXGwPovTNdX/view?usp=drivesdk",
    "validita": "VALIDA"
  }
```

Notiamo che:
- `c` contiene la classe di riferimento (normalizzata, es. `1A`, `3ITCAB`, `4ITIAC`)
- `name` contiene il nome della materia (normalizzato)
- `teachers` è un vettore con i cognomi dei docenti
- `href` è l'URL Google Drive del programma svolto
- `validita` è la stima di validità del documento (`VALIDA` / `NON VALIDA`); attualmente il front-end non la usa

## Generazione dei dati (Python)

I dati provengono da un export CSV del *Report adempimenti di fine anno* (colonne `Cognome`, `Nome`, `Classe`, `Materia`, `Link al documento`, `Stima validità`, …) collocato nella cartella `/csv`.

Lo script `/python/parse_csv.py` legge quel CSV e:
- **normalizza le materie** unificando le numerose varianti di grafia (maiuscole/minuscole, sinonimi e sigle: es. `TTRG` → *Tecnologie e Tecniche di Rappresentazione Grafica*, `STA` → *Scienze e Tecnologie Applicate*);
- **normalizza le classi** in un formato compatto (numeri romani → arabi, riconoscimento dell'articolazione `ITxx`/`CAT` e della sezione: es. `III ITIA/C` → `3ITIAC`);
- ricava i **docenti** dal cognome;
- mantiene i **link** a Google Drive in modalità anteprima (`/view`);
- **scarta** i record privi sia di classe sia di materia.

Lo script usa solo la libreria standard di Python (nessuna dipendenza esterna). Per rigenerare la fixture:

```bash
cd python
python parse_csv.py
```

Oltre a `../src/fixtures/data.json`, lo script produce `./normalization_review.md`: una tabella *canonico ← varianti* utile per verificare o correggere le mappature (con evidenziati i casi ambigui). Il file è rigenerato a ogni esecuzione e non è versionato.

## Sviluppo

```bash
npm install
npm start
```

TBD:
- ✅ struttura del file json contenente i file da filtrare
- ✅ pipeline di generazione dei dati da CSV
- ✅ modularizzazione del front-end
- pubblicazione delle fonti (URL del figma)
- EN version
- Integrazione con Redux
