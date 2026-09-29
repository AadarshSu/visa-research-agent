"""Item 75 test 1 (entry 241): what to read to curate oracle rows for three destinations whose visa
pages are mostly not in English. No network, no model.

The oracle refresh's method (`../oracle-refresh-2026-09-29/candidates.py`) with two changes, both
so that no arm's shortlist goes unjudged:
- candidates are the top `K` by each of link, stored-text keywords, embeddings (neutral) and
  embeddings (traveller), **plus** the top `FUSED` of today's fused order and of link + embeddings;
- the passage test that decides what is read looks for each role's words in English, Malay,
  Indonesian and Spanish, because an English-only filter would hide exactly the pages under test.

usage: EMBED_CAPTURES=var/embed-test1-2026-09-29/cap/new candidates.py > review.txt
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "embed-replay-2026-09-28"))

import common  # noqa: E402

from visa_research_agent.discovery.models import ROLE_ORDER  # noqa: E402
from visa_research_agent.discovery.selection_recall import same_pages  # noqa: E402

K = 10
FUSED = 25

SIGNAL = {
    "visa_decision": (
        r"(visa[- ]free|visa exemption|exempt(ed)? from (the )?visa|require[sd]? a visa|need a visa"
        r"|visa (is )?required|visa on arrival|without (a )?visa|bebas visa|visa kunjungan"
        r"|pengecualian visa|tanpa visa|visa saat kedatangan|visa on arrival|keperluan visa"
        r"|tidak memerlukan visa|memerlukan visa|dikecualikan|pengecualian"
        r"|requieren visa|requiere visa|exonerad|exentos? de visa|no necesitan visa|sin visa"
        r"|necesitan visa|visa consular)"
    ),
    "document_checklist": (
        r"(required documents|supporting documents|documents? (required|you (will )?need)"
        r"|passport[^.]{0,200}(photo|photograph|bank statement|itinerary|insurance)"
        r"|dokumen (yang )?(diperlukan|persyaratan)|persyaratan|syarat|dokumen sokongan"
        r"|pasport[^.]{0,200}(gambar|foto|penyata bank)|documentos? (requeridos|necesarios)"
        r"|requisitos|documentaci[oó]n)"
    ),
    "application_route": (
        r"(apply (online|in person|at|through|via)|application cent(re|er)|submit (your|the)"
        r" application|VFS|BLS|book an appointment|eVISA|e-visa|evisa|mohon|permohonan"
        r"|mengajukan|pengajuan|solicitud|solicitar|consulado|tr[aá]mite en l[ií]nea)"
    ),
    "fees": (
        r"((£|€|\$|USD|RM|MYR|IDR|Rp\.?|UYU|U\$S|UI)\s?\d|visa fee|application fee|bayaran|fi visa"
        r"|biaya|tarif|PNBP|arancel|tasa|costo)"
    ),
    "processing_times": (
        r"(processing time|within \d+ (working |calendar |business )?days|hari (kerja|bekerja)"
        r"|tempoh (proses|pemprosesan)|waktu (proses|penyelesaian)|d[ií]as h[aá]biles"
        r"|plazo)"
    ),
    "general_entry": (
        r"(passport[^.]{0,120}valid|entry (conditions|requirements)|return ticket|onward (ticket"
        r"|travel)|immigration (check|control)|masa berlaku paspor|sah laku|pasport[^.]{0,80}"
        r"(6|enam) bulan|tiket (pulang|kembali)|syarat masuk|pemeriksaan imigrasi"
        r"|pasaporte[^.]{0,120}(vigente|validez)|requisitos de ingreso|ingreso al pa[ií]s)"
    ),
}


def passages(body: str, role: str, limit: int = 3) -> list[str]:
    out, last = [], -10_000
    for m in re.finditer(SIGNAL[role], body, re.IGNORECASE):
        if m.start() - last < 500:
            continue
        last = m.start()
        s, e = max(0, m.start() - 220), min(len(body), m.end() + 260)
        out.append(" ".join(body[s:e].split()))
        if len(out) == limit:
            break
    return out


def main() -> None:
    con = common.connect()
    total = 0
    for name in common.names():
        cap = common.load(name)
        link, text = common.link_ranking(cap), common.text_ranking(cap)
        neutral = common.embed_ranking(cap, "neutral", con)
        traveller = common.embed_ranking(cap, "traveller", con)
        if neutral is None or traveller is None:
            sys.exit(f"{name}: no vectors; run embed.py with EMBED_CAPTURES set")
        fused = [
            [c.link.url for c in common.fused_order(cap, rankings)[:FUSED]]
            for rankings in ([link, text], [link, neutral])
        ]
        print(f"\n######## {name}  pool {len(cap['pool'])}, with text {len(cap['held'])}")
        for role in ROLE_ORDER:
            cands = set().union(*fused)
            for ranking in (link, text, neutral, traveller):
                cands |= set(ranking[role][:K])
            cands = sorted(u for u in cands if cap["held"].get(u))
            groups = same_pages(set(cands), {u: t for u, t in cap["held"].items() if t}, [])
            seen, shown = set(), []
            for u in cands:
                if u in seen:
                    continue
                twins = sorted(groups[u] - {u})
                seen |= groups[u]
                p = passages(cap["held"][u], role)
                if p:
                    shown.append((u + (f"  (= {', '.join(twins)})" if twins else ""), p))
            if not shown:
                continue
            print(f"\n=== {name} {role}  ({len(shown)})")
            for u, ps in shown:
                total += 1
                print(f"- {u}")
                for p in ps:
                    print(f"    « {p} »")
    print(f"\n{total} pairs to read", file=sys.stderr)


if __name__ == "__main__":
    main()
