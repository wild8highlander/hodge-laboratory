"""The multilingual layer (v1.11): user-facing strings of the
laboratory in English and Russian, with a fallback to English.

Usage:
    from .i18n import set_lang, t
    set_lang("ru")            # or via the CLI flag --lang ru
    print(t("all_checks_passed"))

The catalogs cover every protocol/stand message the runner prints;
adding a language = appending a dict here (the keys are stable).
"""

from typing import Dict

CATALOGS: Dict[str, Dict[str, str]] = {
    "en": {
        "lab_title": "VER-HODGE laboratory",
        "version": "version",
        "author": "author",
        "all_checks_passed": "ALL CHECKS PASSED",
        "failures": "FAILURES",
        "results_written": "results written",
        "stand": "stand",
        "run": "run",
        "pass": "PASS",
        "fail": "FAIL",
        "verdict_certificate": "ALGEBRAIC CERTIFICATE",
        "verdict_not_determined": "NOT-DETERMINED",
        "protocol_header": "verification protocol",
        "claims_registry": "claims registry",
        "complexity_ledger": "complexity ledger",
        "near_miss": "near miss",
        "counterexample": "counterexample",
        "lang_set": "language set to {lang}",
        "quick_mode": "quick mode (reduced grids)",
        "full_mode": "full mode",
        "stand_dwork": "the Dwork pencil stand",
        "stand_pf_operator": "the mod-p Picard-Fuchs operator stand",
        "stand_pf_closure": "the PF derivation closure (the psi-gauge theorem)",
        "stand_dwork_family": ("the Dwork family at every Calabi-Yau "
                               "degree d = 3, 4, 5"),
        "open_commitment": "open commitment",
        "resolved": "resolved",
        "computed_negative": "computed negative",
        "status": "status",
    },
    "ru": {
        "lab_title": "Лаборатория VER-HODGE",
        "version": "версия",
        "author": "автор",
        "all_checks_passed": "ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ",
        "failures": "ПРОВАЛЫ",
        "results_written": "результаты записаны",
        "stand": "стенд",
        "run": "прогон",
        "pass": "ПРОЙДЕНО",
        "fail": "ПРОВАЛ",
        "verdict_certificate": "АЛГЕБРАИЧЕСКИЙ СЕРТИФИКАТ",
        "verdict_not_determined": "НЕ-ОПРЕДЕЛЕНО",
        "protocol_header": "протокол верификации",
        "claims_registry": "реестр претензий",
        "complexity_ledger": "журнал сложности",
        "near_miss": "почти-промах",
        "counterexample": "контрпример",
        "lang_set": "язык установлен: {lang}",
        "quick_mode": "быстрый режим (сокращённые сетки)",
        "full_mode": "полный режим",
        "stand_dwork": "стенд карандаша Дворка",
        "stand_pf_operator": "стенд мод-p оператора Пикара–Фукса",
        "stand_pf_closure": ("замыкание вывода ПФ-оператора "
                             "(теорема о ψ-калибровке)"),
        "stand_dwork_family": ("семейство Дворка всех кэлеровых степеней "
                               "d = 3, 4, 5"),
        "open_commitment": "открытая претензия",
        "resolved": "разрешено",
        "computed_negative": "вычисленное отрицание",
        "status": "статус",
    },
}

_current = {"lang": "en"}


def set_lang(lang: str) -> None:
    lang = (lang or "en").lower()
    if lang not in CATALOGS:
        lang = "en"
    _current["lang"] = lang


def get_lang() -> str:
    return _current["lang"]


def t(key: str, **kw) -> str:
    """Translate a key in the current language (fallback: English)."""
    lang = _current["lang"]
    cat = CATALOGS.get(lang, CATALOGS["en"])
    s = cat.get(key) or CATALOGS["en"].get(key) or key
    return s.format(**kw) if kw else s


def available_langs():
    return sorted(CATALOGS)
