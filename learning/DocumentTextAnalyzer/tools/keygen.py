"""
keygen.py – Internes Lizenz-Key-Generator-Tool
VT Document Text Converter  |  vt-solutions GmbH
================================================
NUR FÜR DEN INTERNEN GEBRAUCH. Nicht weitergeben.

Verwendung:
  python tools/keygen.py --edition PRO --year 2026 --count 10
  python tools/keygen.py --edition STANDARD --year 2026 --serial 1 --count 5
  python tools/keygen.py --verify VT-2026-P001-XXXX

Ausgabe:
  Pro Lizenz eine Zeile:  VT-2026-P001-ABCD  (Standard | Pro)
"""

import argparse
import sys
from pathlib import Path

# Projektroot zum Suchpfad hinzufügen
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.licensing.license_crypto import generate_key, validate_key, EDITION_MAP


def _print_header(edition: str, year: int, count: int, start: int) -> None:
    print()
    print("+-------------------------------------------------------+")
    print("|   VT Document Text Converter  -  Key Generator        |")
    print("|   vt-solutions GmbH  |  NUR INTERNER GEBRAUCH         |")
    print("+-------------------------------------------------------+")
    print(f"  Edition : {edition}")
    print(f"  Jahr    : {year}")
    print(f"  Anzahl  : {count}  (Start-Seriennummer: {start})")
    print()
    print("  Schluessel")
    print("  " + "-" * 48)


def _print_footer() -> None:
    print()


def cmd_generate(args: argparse.Namespace) -> None:
    edition = args.edition.upper()
    if edition not in EDITION_MAP.values():
        print(f"Fehler: Unbekannte Edition '{edition}'. Erlaubt: STANDARD, PRO")
        sys.exit(1)

    year  = args.year
    start = args.serial
    count = args.count

    _print_header(edition, year, count, start)

    for i in range(count):
        serial = start + i
        key = generate_key(edition, year, serial)
        print(f"  {key}   (#{serial})")

    _print_footer()


def cmd_verify(key: str) -> None:
    print()
    print(f"  Schluessel : {key}")
    ok, edition = validate_key(key)
    if ok:
        print(f"  Status     : GUELTIG")
        print(f"  Edition    : {edition}")
    else:
        print(f"  Status     : UNGUELTIG")
    print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="VT Lizenz-Key-Generator (intern)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    subparsers = parser.add_subparsers(dest="cmd")

    # Unterbefehl: generate (Standard)
    gen = subparsers.add_parser("generate", help="Schlüssel erzeugen")
    gen.add_argument("--edition", choices=["STANDARD", "PRO"], required=True,
                     help="Lizenz-Edition")
    gen.add_argument("--year", type=int, default=2026,
                     help="Lizenzjahr (Standard: 2026)")
    gen.add_argument("--serial", type=int, default=1,
                     help="Start-Seriennummer (Standard: 1)")
    gen.add_argument("--count", type=int, default=1,
                     help="Anzahl zu erzeugender Schlüssel (Standard: 1)")

    # Unterbefehl: verify
    ver = subparsers.add_parser("verify", help="Schlüssel prüfen")
    ver.add_argument("key", help="Zu prüfender Schlüssel (z. B. VT-2026-P001-XXXX)")

    # Kurzform ohne Unterbefehl: --edition / --year / ...
    parser.add_argument("--edition", choices=["STANDARD", "PRO"],
                        help="(Kurzform) Lizenz-Edition")
    parser.add_argument("--year", type=int, default=2026,
                        help="(Kurzform) Lizenzjahr")
    parser.add_argument("--serial", type=int, default=1,
                        help="(Kurzform) Start-Seriennummer")
    parser.add_argument("--count", type=int, default=1,
                        help="(Kurzform) Anzahl Schlüssel")
    parser.add_argument("--verify", metavar="KEY",
                        help="(Kurzform) Schlüssel prüfen")

    args = parser.parse_args()

    # Unterbefehl 'verify'
    if args.cmd == "verify":
        cmd_verify(args.key)
        return

    # Unterbefehl 'generate'
    if args.cmd == "generate":
        cmd_generate(args)
        return

    # Kurzform --verify
    if args.verify:
        cmd_verify(args.verify)
        return

    # Kurzform --edition
    if args.edition:
        cmd_generate(args)
        return

    parser.print_help()


if __name__ == "__main__":
    main()
