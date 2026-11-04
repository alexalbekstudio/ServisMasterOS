import re
from typing import Any, Dict

from fastapi import APIRouter, Form, HTTPException, status
from pydantic import BaseModel

router = APIRouter()


class DocumentParseRequest(BaseModel):
    raw_text: str


def clean_text(text: str) -> str:
    """Uklanja suvišne znakove i višestruke razmake."""
    t = re.sub(r"^[\s\-_:\.]+", "", text)
    return re.sub(r"\s+", " ", t).strip()


SERBIAN_PLATE_PREFIXES = (
    "AL", "AR", "AC", "BB", "BG", "BO", "BP", "BT", "BĆ", "BU", "BČ", "VA", "VB",
    "VL", "VS", "VR", "VŠ", "GL", "GM", "DE", "ĐA", "ZA", "ZR", "IN", "IC", "JA",
    "KA", "KC", "KV", "KG", "KŽ", "KI", "KL", "KM", "KO", "KŠ", "LB", "LE", "LO",
    "LU", "NV", "NG", "NI", "NP", "NS", "PA", "PB", "PE", "PZ", "PI", "PK", "PN",
    "PO", "PR", "PT", "RA", "RU", "SA", "SM", "SV", "SD", "SJ", "SO", "SP", "ST",
    "SU", "TO", "TS", "TT", "ĆU", "UB", "UE", "UŽ", "ČA", "ŠA", "ŠI"
)

CHAR_TO_DIGIT = {
    "Z": "2", "z": "2", "A": "4", "a": "4",
    "O": "0", "o": "0", "Q": "0", "D": "0",
    "I": "1", "l": "1", "|": "1", "T": "1",
    "S": "5", "s": "5", "G": "6", "b": "6", "B": "8",
}

DIGIT_TO_CHAR = {
    "0": "O", "1": "I", "2": "Z", "4": "A",
    "5": "S", "8": "B", "N": "R",
}


def fix_digits_part(digits_str: str) -> str:
    res = []
    for ch in digits_str:
        if ch.isdigit():
            res.append(ch)
        elif ch in CHAR_TO_DIGIT:
            res.append(CHAR_TO_DIGIT[ch])
        else:
            res.append(ch)
    return "".join(res)


def fix_suffix_part(suffix_str: str) -> str:
    res = []
    for ch in suffix_str.upper():
        if ch in DIGIT_TO_CHAR:
            res.append(DIGIT_TO_CHAR[ch])
        elif ch == "Q":
            res.append("O")
        else:
            res.append(ch)
    return "".join(res)


def extract_serbian_license_plate(raw_text: str) -> str | None:
    """Izvlači registarsku oznaku i ispravlja OCR greške."""
    normalized = raw_text.replace("\r", "\n").upper()
    lines = normalized.splitlines()

    # 1. Traženje reda koji počinje poljem A
    for line in lines:
        line = line.strip()
        match_a = re.search(r"^[A4I\^][\s\.:\-_]*([A-ZŠĐČĆŽ0-9\-\s]{5,14})", line)
        if match_a:
            raw_cand = re.sub(r"[^A-ZŠĐČĆŽ0-9]", "", match_a.group(1))
            for prefix in SERBIAN_PLATE_PREFIXES:
                if raw_cand.startswith(prefix) and len(raw_cand) >= 6:
                    rest = raw_cand[len(prefix):]
                    raw_digits = rest[:-2]
                    raw_suffix = rest[-2:]
                    fixed_digits = fix_digits_part(raw_digits)
                    fixed_suffix = fix_suffix_part(raw_suffix)
                    if fixed_digits.isdigit():
                        return f"{prefix}-{fixed_digits}-{fixed_suffix}"

    # 2. Pretraga bilo gde u tekstu sa prefiksom grada
    for prefix in SERBIAN_PLATE_PREFIXES:
        pattern = rf"\b{prefix}[\s\-_.:]*([A-Z0-9]{{3,5}})[\s\-_.:]*([A-Z0-9]{{2}})\b"
        match = re.search(pattern, normalized)
        if match:
            raw_digits = match.group(1)
            raw_suffix = match.group(2)
            fixed_digits = fix_digits_part(raw_digits)
            fixed_suffix = fix_suffix_part(raw_suffix)
            if fixed_digits.isdigit():
                return f"{prefix}-{fixed_digits}-{fixed_suffix}"

    # 3. Fallback — traži "slova-brojevi-slova"
    for line in lines:
        candidates = re.findall(r"\b([A-ZŠĐČĆŽ]{2})([0-9]{3,4})([A-ZŠĐČĆŽ]{2})\b", line)
        for prefix, digits, suffix in candidates:
            if prefix in SERBIAN_PLATE_PREFIXES:
                return f"{prefix}-{digits}-{suffix}"

    return None


def _fix_common_ocr_name_errors(name: str) -> str:
    """Ispravlja najčešće OCR greške u srpskim imenima."""
    if not name:
        return name

    KNOWN_NAMES = {
        "STAVICA": "SLAVICA", "BURBIEVIE": "BURBEVIĆ", "DURBEVIC": "ĐURĐEVIĆ",
        "ĐURĐEVIĆ": "ĐURĐEVIĆ", "DURĐEVIĆ": "ĐURĐEVIĆ", "DJURDJEVIC": "ĐURĐEVIĆ",
        "BURBEVIC": "ĐURĐEVIĆ", "BURBEVIĆ": "ĐURĐEVIĆ",
        "JOVANA": "JOVANA", "DRAGANA": "DRAGANA", "MILICA": "MILICA",
        "JELENA": "JELENA", "ANA": "ANA", "IVANA": "IVANA",
        "SNEZANA": "SNEŽANA", "SNEŽANA": "SNEŽANA", "MARIJA": "MARIJA",
        "MILAN": "MILAN", "MARKO": "MARKO", "NIKOLA": "NIKOLA",
        "STEFAN": "STEFAN", "ALEKSANDAR": "ALEKSANDAR", "DRAGAN": "DRAGAN",
        "NENAD": "NENAD", "BOJAN": "BOJAN", "VLADIMIR": "VLADIMIR", "ZORAN": "ZORAN",
    }

    SURNAME_FIXES = {
        "ĐURĐEVIĆ": "ĐURĐEVIĆ", "DURĐEVIĆ": "ĐURĐEVIĆ", "ĐURDEVIC": "ĐURĐEVIĆ",
        "DURDEVIC": "ĐURĐEVIĆ", "DJURDJEVIC": "ĐURĐEVIĆ", "DJURDJEVIĆ": "ĐURĐEVIĆ",
        "BURBEVIC": "ĐURĐEVIĆ", "BURBEVIĆ": "ĐURĐEVIĆ", "DURBEVIC": "ĐURĐEVIĆ",
        "JOVANOVIC": "JOVANOVIĆ", "JOVANOVIĆ": "JOVANOVIĆ",
        "PETROVIC": "PETROVIĆ", "PETROVIĆ": "PETROVIĆ",
        "NINKOVIC": "NINKOVIĆ", "NINKOVIĆ": "NINKOVIĆ",
        "KOSTIC": "KOSTIĆ", "KOSTIĆ": "KOSTIĆ",
        "LUKIC": "LUKIĆ", "LUKIĆ": "LUKIĆ",
        "MARKOVIC": "MARKOVIĆ", "MARKOVIĆ": "MARKOVIĆ",
        "STANKOVIC": "STANKOVIĆ", "STANKOVIĆ": "STANKOVIĆ",
        "ILIC": "ILIĆ", "ILIĆ": "ILIĆ",
        "PAVLOVIC": "PAVLOVIĆ", "PAVLOVIĆ": "PAVLOVIĆ",
        "NIKOLIC": "NIKOLIĆ", "NIKOLIĆ": "NIKOLIĆ",
        "STOJANOVIC": "STOJANOVIĆ", "STOJANOVIĆ": "STOJANOVIĆ",
    }

    parts = name.split()
    fixed = []
    for part in parts:
        upper = part.upper()
        if upper in KNOWN_NAMES:
            fixed.append(KNOWN_NAMES[upper])
        elif upper in SURNAME_FIXES:
            fixed.append(SURNAME_FIXES[upper])
        else:
            fixed.append(part)

    result = []
    for word in " ".join(fixed).split():
        result.append(word[0].upper() + word[1:].lower() if word else word)
    return " ".join(result)


def parse_vehicle_registration_document(raw_text: str) -> Dict[str, Any]:
    """Robustan parser za srpske saobraćajne dozvole."""
    data = {
        "license_plate": None,
        "owner_name": None,
        "vin": None,
        "make": None,
        "model": None,
        "raw_text": raw_text,
    }

    normalized = raw_text.replace("\r", "\n")
    upper_text = normalized.upper()

    # 1. REGISTARSKA OZNAKA
    plate = extract_serbian_license_plate(raw_text)
    if plate:
        data["license_plate"] = plate

    # 2. VLASNIK (C.1.1 Prezime, C.1.2 Ime)
    last_name = None
    first_name = None

    ln_match = re.search(
        r"C[\.:]?\s*1[\.:]?\s*1[\.\s:]+\s*([A-ZŠĐČĆŽ][A-ZŠĐČĆŽa-zšđčćž\-]{1,30})",
        normalized, re.IGNORECASE,
    )
    if ln_match:
        last_name = ln_match.group(1)

    fn_match = re.search(
        r"C[\.:]?\s*1[\.:]?\s*2[\.\s:]+\s*([A-ZŠĐČĆŽ][A-ZŠĐČĆŽa-zšđčćž\-]{1,30})",
        normalized, re.IGNORECASE,
    )
    if fn_match:
        first_name = fn_match.group(1)

    if first_name and last_name:
        full = f"{first_name.title()} {last_name.title()}"
        data["owner_name"] = _fix_common_ocr_name_errors(full)
    elif last_name:
        data["owner_name"] = _fix_common_ocr_name_errors(last_name.title())

    # 3. VIN (E)
    vin_match = re.search(
        r"(?:^|\n|\s)E[\s\.:\-\)]*([A-HJ-NPR-Z0-9]{17})(?![A-HJ-NPR-Z0-9])",
        normalized, re.IGNORECASE,
    )
    if vin_match:
        data["vin"] = vin_match.group(1).upper()
    else:
        vin_long = re.search(
            r"(?:^|\n|\s)E[\s\.:\-\)]*([A-HJ-NPR-Z0-9]{18,20})",
            normalized, re.IGNORECASE,
        )
        if vin_long:
            data["vin"] = vin_long.group(1)[:17].upper()
        else:
            gen_vin = re.search(r"\b([A-HJ-NPR-Z0-9]{17})\b", upper_text)
            if gen_vin:
                data["vin"] = gen_vin.group(1)

    if data["vin"]:
        data["vin"] = data["vin"].replace("O", "0").replace("Q", "0")

    # 4. MARKA (D.1)
    make_match = re.search(r"D[\.:]?\s*1[\s\.:\-_]+([A-Za-z0-9\-\s]+)", normalized, re.IGNORECASE)
    if make_match:
        extracted_make = clean_text(make_match.group(1).splitlines()[0])
        if len(extracted_make) >= 2 and not extracted_make.startswith("-"):
            data["make"] = extracted_make.title()

    # 5. MODEL (D.3)
    model_match = re.search(r"(?:D[\.:]?\s*3|0[\.:]?\s*3|D3)[\s\.:\-_]+([A-Za-z0-9\-\s]+)", normalized, re.IGNORECASE)
    if model_match:
        extracted_model = clean_text(model_match.group(1).splitlines()[0])
        if len(extracted_model) >= 2 and not extracted_model.startswith("-"):
            data["model"] = extracted_model.title()

    # Fallback za marke
    known_makes = [
        "RENAULT", "VOLKSWAGEN", "VW", "AUDI", "BMW", "MERCEDES-BENZ", "MERCEDES",
        "PEUGEOT", "CITROEN", "OPEL", "FIAT", "SKODA", "ŠKODA", "FORD", "TOYOTA",
        "HYUNDAI", "KIA", "SEAT", "NISSAN", "ALFA ROMEO", "VOLVO", "MAZDA", "DACIA",
    ]
    if not data["make"]:
        for m in known_makes:
            if re.search(r"\b" + re.escape(m) + r"\b", upper_text):
                data["make"] = "Volkswagen" if m == "VW" else m.title()
                break

    return data


@router.post("/scan-license", response_model=Dict[str, Any])
async def scan_license_endpoint(raw_text: str = Form(...)) -> Any:
    """Endpoint za obradu OCR teksta saobraćajne dozvole."""
    if not raw_text or not raw_text.strip():
        raise HTTPException(status_code=400, detail="Tekst je prazan.")
    if len(raw_text.strip()) < 10:
        raise HTTPException(status_code=400, detail="Tekst je prekratak za parsiranje.")
    return parse_vehicle_registration_document(raw_text)


@router.post("/parse-text", response_model=Dict[str, Any])
def parse_ocr_text_endpoint(payload: DocumentParseRequest) -> Any:
    return parse_vehicle_registration_document(payload.raw_text)