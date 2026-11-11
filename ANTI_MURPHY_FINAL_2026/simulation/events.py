"""Catálogo de perturbações para o Murphy Lab."""

EVENT_PRESETS = {
    "Sem perturbação": {"duration_h": 0.0, "label": "Operação nominal"},
    "Microparada": {"duration_h": 1.0, "label": "Parada curta de 1h"},
    "Quebra crítica": {"duration_h": 4.0, "label": "Indisponibilidade de 4h"},
    "Colapso de turno": {"duration_h": 8.0, "label": "Posto indisponível por 8h"},
}
