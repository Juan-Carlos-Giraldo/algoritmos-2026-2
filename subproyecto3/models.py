from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Set, Tuple


@dataclass(frozen=True)
class Etapa:
    id: str
    tiempo_ejecucion: int
    costo_aceleracion: int
    duracion_acelerada: int

    @property
    def reduccion(self) -> int:
        return self.tiempo_ejecucion - self.duracion_acelerada


@dataclass(frozen=True)
class Interaccion:
    id: str
    categorias: frozenset[str]
    costo_auditoria: Optional[int] = None


@dataclass
class Entrada:
    presupuesto: int
    etapas: List[Etapa]
    precedencias: List[Tuple[str, str]] = field(default_factory=list)
    categorias: Set[str] = field(default_factory=set)
    interacciones: List[Interaccion] = field(default_factory=list)


@dataclass
class Solucion:
    metodo: str
    exacta: bool
    etapas_aceleradas: List[str]
    interacciones_auditadas: List[str]
    costo_aceleracion: int
    costo_auditoria: int
    reduccion_total: int
    duracion_total: int
    factible: bool
    registro: List[str]

    def to_dict(self) -> dict:
        return {
            "metodo": self.metodo,
            "exacta": self.exacta,
            "etapas_aceleradas": self.etapas_aceleradas,
            "interacciones_auditadas": self.interacciones_auditadas,
            "costo_aceleracion": self.costo_aceleracion,
            "costo_auditoria": self.costo_auditoria,
            "reduccion_total": self.reduccion_total,
            "duracion_total": self.duracion_total,
            "factible": self.factible,
            "registro": self.registro,
        }
