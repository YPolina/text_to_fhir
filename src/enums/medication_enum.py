from enum import Enum

class AdherenceEnum(str, Enum):
    taking = "taking"
    taking_as_directed = "taking-as-directed"
    taking_not_as_directed = "taking-not-as-directed"
    not_taking = "not-taking"
    on_hold = "on-hold"
    on_hold_as_directed = "on-hold-as-directed"
    on_hold_not_as_directed = "on-hold-not-as-directed"
    stopped = "stopped"
    stopped_as_directed = "stopped-as-directed"
    stopped_not_as_directed = "stopped-not-as-directed"
    unknown = "unknown"

class PeriodUnitEnum(str, Enum):
    s = "s"
    min = "min"
    h = "h"
    d = "d"
    wk = "wk"
    mo = "mo"
    a = "a"