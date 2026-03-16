"""
Constantes de diseño de la UI.
Centraliza objectNames, dimensiones y valores reutilizables.
Mantiene el diseño separado de la lógica de negocio.
"""

from dataclasses import dataclass
from typing import Final

# MIME type para drag & drop de tareas entre columnas
MIME_TASK_PREFIX: Final[str] = "deepflow:"


@dataclass(frozen=True)
class ObjectNames:
    """Nombres de objectName para estilos QSS."""

    MAIN_WINDOW: Final[str] = "mainWindow"
    MAIN_CENTRAL: Final[str] = "mainCentralWidget"
    TITLE_BAR: Final[str] = "titleBar"
    HEADER_BAR: Final[str] = "headerBar"
    TASKBOARD_VIEW: Final[str] = "taskboardView"
    REPORTS_VIEW: Final[str] = "reportsView"
    REPORTS_TABLE: Final[str] = "reportsTable"
    REPORTS_TITLE: Final[str] = "reportsTitle"
    EMPTY_STATE: Final[str] = "emptyState"
    IN_PROGRESS_COMPACT: Final[str] = "inProgressCompact"
    SECTION_HEADER: Final[str] = "sectionHeader"
    COMPACT_TASK_ROW: Final[str] = "compactTaskRow"
    COMPACT_TASK_NAME: Final[str] = "compactTaskName"
    COMPACT_TASK_DURATION: Final[str] = "compactTaskDuration"
    TASK_CARD: Final[str] = "taskCard"
    COLUMN: Final[str] = "column"
    PRIMARY_BTN: Final[str] = "primaryBtn"
    TASK_INPUT_DIALOG: Final[str] = "taskInputDialog"
    TASK_INPUT_TEXT: Final[str] = "taskInputText"


@dataclass(frozen=True)
class Layout:
    """Dimensiones y márgenes reutilizables."""

    # Task detail / dialogs
    TASK_DETAIL_MIN_WIDTH: Final[int] = 560
    TASK_DETAIL_MIN_HEIGHT: Final[int] = 420
    TASK_DETAIL_DEFAULT_WIDTH: Final[int] = 640
    TASK_DETAIL_DEFAULT_HEIGHT: Final[int] = 520

    # Modal módulos (Reports con muchas columnas necesita más ancho)
    MODAL_MIN_WIDTH: Final[int] = 720
    MODAL_MIN_HEIGHT: Final[int] = 360
    MODAL_DEFAULT_WIDTH: Final[int] = 920
    MODAL_DEFAULT_HEIGHT: Final[int] = 480

    # Task input
    TASK_INPUT_MIN_WIDTH: Final[int] = 420
    TASK_INPUT_MIN_HEIGHT: Final[int] = 320

    # Compact task row
    TASK_ROW_HEIGHT: Final[int] = 44
    MAX_TASKS_VISIBLE: Final[int] = 3
    MAX_NAME_LEN: Final[int] = 50

    # Main shell / dashboard
    SHELL_MIN_WIDTH: Final[int] = 400
    SHELL_MIN_HEIGHT: Final[int] = 320
    SHELL_DEFAULT_WIDTH: Final[int] = 440
    SHELL_DEFAULT_HEIGHT: Final[int] = 360


