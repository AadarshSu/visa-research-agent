# ruff: noqa: E501 — quoted passages, kept whole so they can be searched for
"""Item 75 test 1 (entry 241): the six oracle rows curated for Malaysia, Indonesia and Uruguay.

Judged by hand from `review.txt` / `r_<destination>.txt` and the stored pages, by the rules the other
rows use (`adjudicate_roles.txt` 4 to 7b, rule 11 for tools). `rows.py` prints them as YAML; they are
appended to `oracle/selection_oracle.yaml` by `rows.py --append`, which then validates the file with
`load_oracle`. No network, no model.
"""

import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ORACLE = ROOT / "oracle/selection_oracle.yaml"

IMI = "https://www.imi.gov.my/index.php"
EVISA = "https://evisa.imigrasi.go.id/front"
KEMLU = "https://kemlu.go.id"
GUB = "https://www.gub.uy"
MRREE = f"{GUB}/ministerio-relaciones-exteriores/comunicacion/publicaciones"

# --- Malaysia ------------------------------------------------------------------------------------

MY_LIST_EN = (
    f"{IMI}/en/main-services/visa/visa-requirement-by-country",
    "the Immigration Department's list, in English",
)
MY_LIST_MS = (
    f"{IMI}/perkhidmatan-utama/visa/keperluan-visa-mengikut-negara",
    "the same list in Malay",
)
MY_NA = {
    "document_checklist": "no visa application, so there are no documents to bring to one",
    "application_route": "there is nothing to apply for",
    "fees": "no application, no fee",
    "processing_times": "nothing is processed",
}
MY_UNVERIFIABLE = [
    f"{IMI}/en/main-services/entry-requirement-into-malaysia-en",
    f"{IMI}/en/pengumuman/malaysia-digital-arrival-card-mdac-for-foreign-visitors-2",
    f"{IMI}/en/pengumuman/malaysia-digital-arrival-card-mdac",
]
MY_ENTRY = (
    "the pages that state it — 'Entry requirements into Malaysia' and the Malaysia Digital Arrival "
    "Card notices — hold only the site's navigation in the store (about 2,500 characters each), so "
    "nobody could judge them; they are listed as unverifiable. The visa list's yellow-fever "
    "condition applies to arrivals from risk countries, which neither traveller's country is"
)
MY_EXCLUDED_IN = [
    {
        "url": f"{IMI}/en/main-services/visa/entri-for-indian-nationals",
        "why": (
            "describes eNTRI, a 15-day online registration for Indian nationals, which the "
            "page does not date; the visa list states a 30-day exemption in force until 31 "
            "December 2026, and the two cannot both describe entry today"
        ),
    },
    {
        "url": f"{IMI}/perkhidmatan-utama/visa/evisa/entri-bagi-warga-india",
        "why": "the eNTRI page in Malay, excluded for the same reason",
    },
]

MALAYSIA_IN = {
    "corridor": "malaysia/IN/GB/tourism",
    "contention": 309,
    "text_held": 214,
    "answers": {
        "visa_decision": [
            (
                *MY_LIST_EN,
                "India is on the list of countries needing a visa with the note 'India** citizen: "
                "visa exempts until 31st December 2026' — an Indian passport needs no visa for a "
                "social visit",
            ),
        ],
    },
    "not_applicable": MY_NA,
    "unanswered": {"general_entry": MY_ENTRY},
    "unverifiable": MY_UNVERIFIABLE,
    "excluded": MY_EXCLUDED_IN,
    "note": (
        "The Malay version of the visa list, "
        "https://www.imi.gov.my/index.php/perkhidmatan-utama/visa/keperluan-visa-mengikut-negara, "
        "states the same rule and is not in the pool: its link scores -26 (an 'off-scope: student' "
        "penalty) and its stored text scores only for application_route, on the English word "
        "'eVisa' — nothing in 'Visa tidak diperlukan' registers as a decision. Curated for item "
        "75's test 1 (entry 241)."
    ),
}

MALAYSIA_PH = {
    "corridor": "malaysia/PH/PH/tourism",
    "contention": 305,
    "text_held": 211,
    "answers": {
        "visa_decision": [
            (
                *MY_LIST_EN,
                "'Visa is not required for a stay of less than one (1) month for ASEAN nationals "
                "except Myanmar' — the Philippines is an ASEAN member",
            ),
        ],
    },
    "not_applicable": MY_NA,
    "unanswered": {"general_entry": MY_ENTRY},
    "unverifiable": MY_UNVERIFIABLE,
    "note": (
        "The Malay version of the visa list, "
        "https://www.imi.gov.my/index.php/perkhidmatan-utama/visa/keperluan-visa-mengikut-negara, "
        "states the same rule and is not in the pool: its link scores -26 (an 'off-scope: student' "
        "penalty) and its stored text scores only for application_route, on the English word "
        "'eVisa' — nothing in 'Visa tidak diperlukan' registers as a decision. Curated for item "
        "75's test 1 (entry 241)."
    ),
}

# --- Indonesia -----------------------------------------------------------------------------------

EVOA = f"{EVISA}/info/evoa"
EVOA_FAQ = f"{EVISA}/faqs/university"
COPENHAGEN = f"{KEMLU}/copenhagen/pelayanan-perwakilan/visa/visa-on-arrival-and-e-visa-on-arrival"
BPS_HUB = "https://hub.bps.go.id/travel-and-visa"
LIMA = f"{KEMLU}/id/lima/pelayanan-perwakilan/visa-elektronik-saat-kedatangan-(e-voa)"

INDONESIA_IN = {
    "corridor": "indonesia/IN/GB/tourism",
    "contention": 757,
    "text_held": 594,
    "answers": {
        "visa_decision": [
            (
                EVOA,
                "the eVisa portal's list of passports eligible for the (electronic) visa on "
                "arrival names India: a visa is needed, and it is issued on arrival or online (8g)",
            ),
            (
                f"{KEMLU}/chicago/pelayanan-perwakilan/untuk-wna-warga-negara-asing/visa",
                "'LIST OF SUBJECTS TO VISA ON ARRIVAL … India' — in English",
            ),
            (
                LIMA,
                "'VoA Countries … 32. India' — in English",
            ),
            (
                "https://www.kemlu.go.id/id/sofia/pelayanan-perwakilan/bebas-visa-kunjungan",
                "'subyek Visa Kunjungan Saat Kedatangan Khusus Wisata … 22) India' — the "
                "visa-on-arrival list, in Indonesian",
            ),
            (
                "https://jakartapusat.imigrasi.go.id/faqs",
                "'Negara mana saja yang terdaftar dalam daftar Electronic Visa on Arrival (E-VOA)? "
                "… 28. India' — in Indonesian",
            ),
            (
                "https://jogja.imigrasi.go.id/how-to-get-an-indonesia-visa-on-arrival",
                "the visa-on-arrival country list, 'Filipina Finlandia … India Inggris', under 'Who "
                "Can Get an Indonesia Visa on Arrival'",
            ),
        ],
        "document_checklist": [
            (
                EVOA,
                "'The documents to request an Visitor Visa are as follows: Full biodata page of "
                "passport with at least 6 months validity … Passport size photograph … Email "
                "address; and A valid Mastercard, Visa, or JCB credit card'",
            ),
            (
                EVOA_FAQ,
                "the same portal's FAQ: passport biodata page, photograph, email address and a "
                "credit card",
            ),
            (
                COPENHAGEN,
                "for the visa on arrival: 'Passport with minimum validity of 6 months … Return "
                "Flight tickets, Visa Fee (Rp 500.000) … Proof of health insurance' — a visa on "
                "arrival is not a post's process, so rule 5 does not exclude an embassy stating it",
            ),
            (
                BPS_HUB,
                "'Required documents: A passport that is still valid for at least 6 (six) months; A "
                "return ticket or a connecting ticket'",
            ),
        ],
        "application_route": [
            (
                EVOA,
                "the electronic visa on arrival is applied for on this portal before travel, or "
                "a visa on arrival is obtained 'at the port of entry'",
            ),
            (
                COPENHAGEN,
                "'foreign travellers can also get their visa on arrival before their actual arrival "
                "in Indonesia through e-VoA … apply e-VoA please visit https://evisa.imigrasi.go.id/'",
            ),
            (
                f"{KEMLU}/chicago/pelayanan-perwakilan/untuk-wna-warga-negara-asing/visa",
                "'To obtain an Electronic Visa On Arrival, please access: evisa.imigrasi.go.id'",
            ),
            (
                LIMA,
                "'The electronic Visa on Arrival was now possible to obtain by online prior to "
                "entering Indonesia, accessible at: https://molina.imigrasi.go.id/'",
            ),
            (
                f"{KEMLU}/caracas/pelayanan-perwakilan/visa",
                "'Visa on Arrival and Electronic Visa on Arrival (e-VoA)' through the portal before "
                "departure",
            ),
            (
                "https://jogja.imigrasi.go.id/how-to-get-an-indonesia-visa-on-arrival",
                "'Where to get it Airport: Soekarno Hatta, Jakarta, Ngurah Rai, Denpasar, Bali …'",
            ),
            (
                "https://sampit.imigrasi.go.id/e-voa",
                "'HOW TO APPLY 01 Register Create account on Molina website. 02 Upload … 03 Payment "
                "… 04 Download Receive e-VoA PDF instantly'",
            ),
            (
                BPS_HUB,
                "a visa on arrival 'upon arrival at Immigration Border Controls in certain "
                "airports, seaports, and border posts'",
            ),
        ],
        "fees": [
            (EVOA, "'The Visitor Visa fee is IDR 500.000,00'"),
            (COPENHAGEN, "'Visa Fee (Rp 500.000)'"),
            (LIMA, "'Visa on Arrival costs Rp. 500.000 for 30 days'"),
            (f"{KEMLU}/caracas/pelayanan-perwakilan/visa", "'The VoA/e-VoA costs Rp. 500.000'"),
            (
                "https://jogja.imigrasi.go.id/how-to-get-an-indonesia-visa-on-arrival",
                "'Visa on Arrival costs Rp 500.000'",
            ),
            (
                "https://soekarnohatta.imigrasi.go.id/layanan-publik/warga-negara-asing/"
                "visa-kunjungan-satu-kali/indeks-b211a",
                "'Tarif PNBP Visa Kunjungan Saat Kedatangan Khusus Wisata (Visa on Arrival): "
                "Rp500.000' — in Indonesian",
            ),
            (
                f"{EVISA}/faq/4eb7326f-ddfb-4e61-a24a-fb02adceb67f",
                "the portal's visa-on-arrival entry: 'Stay Up to 30 days (extendable for another 30 "
                "days) Cost Rp500.000'",
            ),
        ],
        "processing_times": [
            (
                "https://sampit.imigrasi.go.id/e-voa",
                "'04 Download Receive e-VoA PDF instantly' — issued on payment",
            ),
        ],
        "general_entry": [
            (
                EVOA_FAQ,
                "'foreigners who wish to enter Indonesia must hold a passport with an expiration "
                "date at least 6 (six) months from the date of arrival … Immigration Officer "
                "reserves the right to ask for your return ticket at entry'",
            ),
            (
                EVOA,
                "'Foreigners who wish to enter Indonesia must hold a passport with an expiration "
                "date at least 6 (six) months from the date of arrival'",
            ),
            (
                BPS_HUB,
                "passport valid six months and a return or onward ticket, at the border",
            ),
        ],
    },
    "excluded": [
        {
            "url": f"{KEMLU}/id/newdelhi/pelayanan-perwakilan/formulir-pengajuan-visa",
            "why": (
                "the embassy in New Delhi's visit-visa application, for applicants in India; this "
                "traveller applies from Britain (rule 5), and a visa on arrival needs no embassy"
            ),
        },
        {
            "url": "https://imigrasi.go.id/wna/daftar-visa-indonesia/F1",
            "why": (
                "the F1 visa on arrival, 7 days, 'eligible for specific countries' at named border "
                "posts — not the 30-day tourist visa on arrival an Indian passport receives"
            ),
        },
    ],
    "note": (
        "The embassy in Copenhagen's visa-on-arrival page answers the checklist, route and fee, "
        "but not the decision: it gives the rule for '86 countries' with the list behind a link "
        "(7b). Curated for item 75's test 1 (entry 241)."
    ),
}

BVK_NA = {
    "document_checklist": "no visa application, so there are no documents to bring to one",
    "application_route": "the exemption is given at the border; there is nothing to apply for",
    "fees": "'Visa exemption arrangement cost IDR 0' (A1 Tourism Visa Exemption)",
    "processing_times": "nothing is processed",
}

INDONESIA_PH = {
    "corridor": "indonesia/PH/PH/tourism",
    "contention": 758,
    "text_held": 591,
    "answers": {
        "visa_decision": [
            (
                f"{KEMLU}/en/doha/pelayanan-perwakilan/visa/bebas-visa-kunjungan",
                "the Visa Exemption under Presidential Regulation 95 of 2024, eligible nationals "
                "'… 13. Philippines …' — in English",
            ),
            (
                f"{KEMLU}/marseille/pelayanan-perwakilan/visa-exemption",
                "'Visit Visa Exemption (BVK) as outlined in Presidential Regulation No. 95/2024: "
                "a) Nationals of the following countries … ii. Philippines' — in English",
            ),
            (
                f"{KEMLU}/etc/informasi-bebas-visa-kunjungan-ke-republik-indonesia",
                "'Berdasarkan Peraturan Presiden Nomor 95 Tahun 2024 … Brunei Darussalam; Filipina; "
                "Kamboja …' — the ministry's own notice, in Indonesian",
            ),
            (
                f"{KEMLU}/id/newdelhi/pelayanan-perwakilan/formulir-pengajuan-visa",
                "the list of countries with Bebas Visa Kunjungan for ordinary passports, 'Filipina "
                "– 30 hari' — in Indonesian; the decision is not a post's, so rule 5 does not apply",
            ),
            (
                "https://kupang.imigrasi.go.id/bebas-visa-kunjungan",
                "'Daftar Negara Bebas … Brunei Darussalam Filipina Kamboja …' — in Indonesian",
            ),
        ],
        "general_entry": [
            (
                f"{KEMLU}/en/doha/pelayanan-perwakilan/visa/bebas-visa-kunjungan",
                "'Hold a passport valid for at least six (6) months from the intended date of entry "
                "… Hold a confirmed return ticket or onward ticket'",
            ),
            (
                f"{KEMLU}/marseille/pelayanan-perwakilan/visa-exemption",
                "'Travelers must present a national passport valid for at least six (6) months … "
                "Proof of onward or return tickets is required'",
            ),
            (
                EVOA_FAQ,
                "'foreigners who wish to enter Indonesia must hold a passport with an expiration "
                "date at least 6 (six) months from the date of arrival' — true of every foreigner",
            ),
            (
                EVOA,
                "the same six-month rule, stated for every foreigner entering",
            ),
        ],
    },
    "not_applicable": BVK_NA,
    "note": (
        "The eVisa portal's visa-on-arrival list also names the Philippines; it is not this "
        "traveller's decision, since a visa-exempt Filipino needs no visa on arrival. Curated for "
        "item 75's test 1 (entry 241)."
    ),
    "excluded": [
        {
            "url": "https://jogja.imigrasi.go.id/tag/bebas-visa-kunjungan",
            "why": (
                "a 2023 news post naming the ten exempt countries of that year's regulation; the "
                "2024 regulation's list is what applies, and other pages state it"
            ),
        },
    ],
}

# --- Uruguay -------------------------------------------------------------------------------------

UY_LIST = f"{GUB}/ministerio-interior/comunicacion/publicaciones/regimen-visas-admision"
UY_BY_COUNTRY = f"{MRREE}/regimen-de-visas-por-pais-1"
UY_VISAS = f"{MRREE}/visas-para-ingresar-uruguay"
UY_TRAMITE = f"{GUB}/tramites/inicio-solicitud-visas"
UY_OTHER_POSTS = (
    "the consulates in Madrid, Asunción, Rosario and Sydney and the embassies in Sweden and the "
    "Dominican Republic state their own requirements, fees and timings; rule 5 excludes each, and "
    "the store holds no Uruguayan post serving this traveller"
)


def uruguay(nat: str, res: str, country: str) -> dict:
    return {
        "corridor": f"uruguay/{nat}/{res}/tourism",
        "contention": 55,
        "text_held": 33,
        "answers": {
            "visa_decision": [
                (
                    UY_LIST,
                    f"the Interior Ministry's table: '{country} Necesita Visa (5)' for an ordinary "
                    "passport, footnote (5) 'Necesita autorización previa' — in Spanish",
                ),
            ],
            "document_checklist": [
                (
                    UY_BY_COUNTRY,
                    "'Requisitos para ingresar a Uruguay: Formulario completo y firmado Carta "
                    "invitación o reserva de hotel Pasaporte vigente por al menos 6 meses … 1 foto "
                    "tamaño pasaporte Reserva de viaje' — the foreign ministry's general list",
                ),
                (
                    UY_TRAMITE,
                    "'Requisitos Formulario / Ficha de inscripción. Carta invitación o reserva de "
                    "hotel y solvencia económica … Pasaporte vigente por al menos 6 meses … 1 foto "
                    "tamaño pasaporte. Reserva de viaje'",
                ),
            ],
            "application_route": [
                (
                    UY_VISAS,
                    "'Los Consulados de la República en el exterior son los encargados de recibir "
                    "las solicitudes de visa … deberán contactarse con el Consulado más cercano'",
                ),
                (
                    UY_BY_COUNTRY,
                    "the same instruction: apply at a Uruguayan consulate, which issues the visa "
                    "once the Dirección Nacional de Migración authorises it",
                ),
                (
                    UY_TRAMITE,
                    "the consular affairs directorate's procedure for starting a visa application "
                    "at a consulate",
                ),
            ],
            "fees": [
                (UY_BY_COUNTRY, "'Costo: US$ 42 (se cobra solo si la visa es otorgada)'"),
                (
                    UY_TRAMITE,
                    "'Costos 3 pesos consulares = 42 USD (únicamente si la visa es otorgada)'",
                ),
            ],
            "processing_times": [
                (
                    UY_VISAS,
                    "'La autorización de la visa es otorgada por la Dirección Nacional de "
                    "Migraciones y suele tomar al menos 20 días hábiles'",
                ),
                (UY_BY_COUNTRY, "the same: 'suele tomar al menos 20 días hábiles'"),
            ],
        },
        "unanswered": {
            "general_entry": (
                "no page states conditions at the border beyond the visa's own requirements; the "
                "passport-validity rule appears only as a requirement of the visa application"
            )
        },
        "excluded": [
            {
                "url": f"{GUB}/ministerio-relaciones-exteriores/consulado-general-madrid/visas/visa-turismo",
                "why": UY_OTHER_POSTS,
            },
            {
                "url": f"{GUB}/ministerio-relaciones-exteriores/embajada-republica-oriental-del-uruguay-republica-dominicana/tramites-consulares/ciudadanos",
                "why": "for Dominican citizens (rule 6)",
            },
        ],
        "note": (
            "Uruguay's visa pages are in Spanish; the pool is 55 pages, smaller than the 40 + 40 "
            "and 120 + 40 cuts, so these rows cannot separate one ranking from another. Curated "
            "for item 75's test 1 (entry 241)."
        ),
    }


ROWS = [
    MALAYSIA_IN,
    MALAYSIA_PH,
    INDONESIA_IN,
    INDONESIA_PH,
    uruguay("IN", "GB", "India"),
    uruguay("PH", "PH", "Filipinas"),
]


def folded(text: str, indent: int) -> str:
    pad = " " * indent
    return "\n".join(textwrap.wrap(text, 100 - indent, initial_indent=pad, subsequent_indent=pad))


def render(row: dict) -> str:
    out = [
        f"  - corridor: {row['corridor']}",
        f"    contention: {row['contention']}",
        f"    text_held: {row['text_held']}",
        "    answers:",
    ]
    for role, pages in row["answers"].items():
        out.append(f"      {role}:")
        for url, *said in pages:
            why = " — ".join(said)
            out += [f"        - url: {url}", "          seen: text", "          why: >-"]
            out.append(folded(f"Curated for item 75's test 1 (entry 241): {why}", 12))
    for key in ("not_applicable", "unanswered"):
        if row.get(key):
            out.append(f"    {key}:")
            for role, why in row[key].items():
                out += [f"      {role}: >-", folded(why, 8)]
    if row.get("unverifiable"):
        out.append("    unverifiable:")
        out += [f"      - {u}" for u in row["unverifiable"]]
    if row.get("excluded"):
        out.append("    excluded:")
        for e in row["excluded"]:
            out += [f"      - url: {e['url']}", "        why: >-", folded(e["why"], 10)]
    if row.get("note"):
        out += ["    note: >-", folded(row["note"], 6)]
    return "\n".join(out)


def main() -> None:
    text = "\n".join(render(r) for r in ROWS) + "\n"
    if "--append" not in sys.argv:
        print(text)
        return
    current = ORACLE.read_text(encoding="utf-8")
    if "malaysia/IN/GB/tourism" in current:
        sys.exit("already appended")
    ORACLE.write_text(current.rstrip("\n") + "\n" + text, encoding="utf-8")
    sys.path.insert(0, str(ROOT / "src"))
    from visa_research_agent.discovery.selection_recall import load_oracle

    oracle = load_oracle(ORACLE)
    print(f"appended; the oracle now holds {len(oracle.corridors)} corridors")


main()
