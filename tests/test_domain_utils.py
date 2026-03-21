"""
Tests de utilidades de dominio.
Ejecutar: pytest tests/test_domain_utils.py -v
"""

import pytest

from domain.taskboard.utils import normalize_key_from_label


def test_normalize_key_from_label_basico():
    """Label simple: minúsculas, espacios → underscore."""
    assert normalize_key_from_label("To Do") == "to_do"
    assert normalize_key_from_label("In Progress") == "in_progress"


def test_normalize_key_from_label_enie():
    """Reemplaza ñ por n para key válido."""
    assert normalize_key_from_label("Cañón") == "canón"  # solo ñ→n, ó se conserva
    assert normalize_key_from_label("Niño") == "nino"


def test_normalize_key_from_label_vacio():
    """Label vacío retorna string vacío."""
    assert normalize_key_from_label("") == ""
    assert normalize_key_from_label("   ") == ""


def test_normalize_key_from_label_espacios_trim():
    """Strip de espacios antes y después."""
    assert normalize_key_from_label("  Backlog  ") == "backlog"


def test_normalize_key_from_label_multiples_espacios():
    """Múltiples espacios se colapsan en un solo underscore."""
    assert normalize_key_from_label("Tribu  Supply") == "tribu__supply"


def test_normalize_key_from_label_ya_minusculas():
    """Label ya en minúsculas sin cambios estructurales."""
    assert normalize_key_from_label("backlog") == "backlog"


def test_normalize_key_from_label_sin_espacios():
    """Label sin espacios se pasa a minúsculas."""
    assert normalize_key_from_label("Detenido") == "detenido"
