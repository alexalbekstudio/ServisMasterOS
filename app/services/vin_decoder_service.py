"""VIN dekoder servis — NHTSA API + fallback za EU vozila."""
import re
from typing import Any, Dict, Optional

import requests

# NHTSA API (besplatan, US vozila)
NHTSA_URL = "https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVin/{vin}?format=json"


class VinDecoderService:
    """Dekodira VIN i vraća podatke o vozilu."""

    # Fallback mapa za EU marke (NHTSA ih često ne prepoznaje)
    EU_MAKE_PREFIXES = {
        "VF": "Renault", "VF1": "Renault", "VF3": "Peugeot", "VF7": "Citroen",
        "VFA": "Alpine", "VWV": "Volkswagen", "WVW": "Volkswagen", "WVG": "Volkswagen",
        "WAU": "Audi", "WUA": "Audi", "WBA": "BMW", "WBS": "BMW",
        "WDB": "Mercedes-Benz", "WDD": "Mercedes-Benz", "TMB": "Škoda", "TM9": "Škoda",
        "ZFA": "Fiat", "ZFF": "Ferrari", "ZAR": "Alfa Romeo", "SJN": "Nissan",
        "SUP": "Nissan", "JMB": "Mitsubishi", "JHM": "Honda", "JTD": "Toyota",
        "JT2": "Toyota", "KMH": "Hyundai", "KNA": "Kia", "YV1": "Volvo",
        "YV4": "Volvo", "VSS": "Seat", "VX1": "Zastava", "SAJ": "Jaguar",
        "SAL": "Land Rover", "VF9": "Bugatti",
    }

    @classmethod
    def validate_vin(cls, vin: str) -> bool:
        """Proverava da li VIN ima 17 znakova i da nema O, I, Q."""
        if not vin or len(vin) != 17:
            return False
        if any(c in "OIQ" for c in vin.upper()):
            return False
        if not re.match(r"^[A-HJ-NPR-Z0-9]{17}$", vin.upper()):
            return False
        return True

    @classmethod
    def decode_nhtsa(cls, vin: str) -> Optional[Dict[str, Any]]:
        """Poziva NHTSA API za dekodiranje VIN-a."""
        try:
            url = NHTSA_URL.format(vin=vin)
            response = requests.get(url, timeout=10)
            if not response.ok:
                return None

            data = response.json()
            results = data.get("Results", [])

            field_map = {
                "Make": "make",
                "Model": "model",
                "ModelYear": "year",
                "Displacement (L)": "engine_displacement",
                "Engine Number of Cylinders": "cylinders",
                "Fuel Type - Primary": "fuel_type",
                "Vehicle Type": "vehicle_type",
                "Plant Country": "plant_country",
            }

            decoded = {}
            for item in results:
                variable = item.get("Variable")
                value = item.get("Value")
                if value and variable in field_map:
                    key = field_map[variable]
                    if key in ("make", "model"):
                        decoded[key] = str(value).strip().title()
                    elif key == "year":
                        try:
                            decoded[key] = int(value)
                        except (ValueError, TypeError):
                            pass
                    elif key == "engine_displacement":
                        try:
                            decoded[key] = float(value)
                        except (ValueError, TypeError):
                            pass
                    elif key == "cylinders":
                        try:
                            decoded[key] = int(value)
                        except (ValueError, TypeError):
                            pass
                    else:
                        decoded[key] = str(value).strip()

            if not decoded.get("make") and not decoded.get("model"):
                return None
            return decoded
        except Exception as e:
            print(f"[VIN NHTSA greška]: {e}")
            return None

    @classmethod
    def decode_eu_fallback(cls, vin: str) -> Optional[Dict[str, Any]]:
        """Fallback za EU vozila — prepoznaje marku po WMI prefiksu."""
        if not vin or len(vin) < 3:
            return None

        vin_upper = vin.upper()
        wmi = vin_upper[:3]
        wmi_2 = vin_upper[:2]

        make = cls.EU_MAKE_PREFIXES.get(wmi) or cls.EU_MAKE_PREFIXES.get(wmi_2)
        if not make:
            return None

        year_map = {
            "A": 2010, "B": 2011, "C": 2012, "D": 2013, "E": 2014, "F": 2015,
            "G": 2016, "H": 2017, "J": 2018, "K": 2019, "L": 2020, "M": 2021,
            "N": 2022, "P": 2023, "R": 2024, "S": 2025, "T": 2026,
        }
        year_char = vin_upper[9] if len(vin_upper) > 9 else None
        year = year_map.get(year_char)

        model_guess = None
        if make == "Renault":
            model_map = {"JZ": "Megane", "RF": "Megane", "AG": "Clio", "BB": "Clio",
                         "FL": "Captur", "HA": "Captur", "JV": "Kadjar", "VB": "Kangoo",
                         "FW": "Twingo", "KT": "Talisman", "KW": "Koleos"}
            model_code = vin_upper[3:5] if len(vin_upper) > 4 else ""
            model_guess = model_map.get(model_code)
        elif make == "Volkswagen":
            model_map = {"ZZ": "Golf", "1K": "Golf", "5N": "Tiguan", "3C": "Passat", "6R": "Polo"}
            model_code = vin_upper[3:5] if len(vin_upper) > 4 else ""
            model_guess = model_map.get(model_code)
        elif make == "Škoda":
            model_map = {"JG": "Octavia", "NE": "Octavia", "5J": "Fabia", "3V": "Superb", "NU": "Kodiaq"}
            model_code = vin_upper[3:5] if len(vin_upper) > 4 else ""
            model_guess = model_map.get(model_code)

        return {"make": make, "model": model_guess, "year": year, "source": "EU fallback"}

    @classmethod
    def decode(cls, vin: str) -> Dict[str, Any]:
        """Glavna metoda — prvo NHTSA, pa EU fallback."""
        if not cls.validate_vin(vin):
            return {
                "valid": False,
                "error": "Nevažeći VIN. Mora imati 17 znakova i ne sme sadržati O, I, Q.",
            }

        vin_upper = vin.upper().strip()

        decoded = cls.decode_nhtsa(vin_upper)
        if decoded and (decoded.get("make") or decoded.get("model")):
            return {"valid": True, "vin": vin_upper, "source": "NHTSA", **decoded}

        eu_decoded = cls.decode_eu_fallback(vin_upper)
        if eu_decoded:
            return {"valid": True, "vin": vin_upper, **eu_decoded}

        return {
            "valid": True,
            "vin": vin_upper,
            "source": "unknown",
            "message": "VIN je ispravan, ali nije mogao biti dekodiran. Unesite podatke ručno.",
        }