"""Muestra, caso a caso, lo que diagnosticó un modelo frente a lo esperado. Uso: python ver.py <modelo>"""

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
model = sys.argv[1]
rows = json.loads((Path(__file__).parent / "resultados" / (model.replace("/", "__") + ".json")).read_text(encoding="utf-8"))
for r in rows:
    out = r.get("respuesta")
    if not isinstance(out, dict):
        print(f"--- {r['caso']}  SIN JSON: {str(out)[:200]!r} {r.get('error', '')}")
        continue
    print(f"--- {r['caso']}  aciertos {r.get('aciertos')}/{r.get('esperados')}  FP {r.get('falsos_positivos')}"
          f"  {r.get('segundos')}s  rechazado={out.get('rechazado')}")
    for p in out.get("problemas", []):
        kind = (p.get("tipo") or "?")[:1].upper()
        what = (p.get("fragmento") or p.get("falta") or "")[:70]
        print(f"   [{kind} {p.get('categoria')} {p.get('gravedad')}] {what}  ::  {p.get('explicacion', '')[:100]}")
