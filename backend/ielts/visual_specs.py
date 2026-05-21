"""Reusable visual JSON specs for Academic Writing Task 1 seeding."""

GENERIC_BAR = {
    "kind": "bar",
    "spec": {
        "title": "Sample data overview",
        "xLabel": "Category",
        "yLabel": "Value",
        "labels": ["A", "B", "C", "D"],
        "datasets": [
            {"label": "Series 1", "data": [42, 58, 35, 71]},
        ],
    },
}

HOUSEHOLD_INTERNET_LINE = {
    "kind": "line",
    "spec": {
        "title": "Household broadband internet access (%)",
        "xLabel": "Year",
        "yLabel": "Percentage of households",
        "labels": ["2010", "2012", "2014", "2016", "2018", "2020"],
        "datasets": [
            {"label": "North", "data": [45, 52, 61, 68, 74, 82]},
            {"label": "Central", "data": [38, 44, 52, 59, 66, 75]},
            {"label": "South", "data": [32, 39, 48, 55, 63, 72]},
        ],
    },
}

RENEWABLE_ELECTRICITY_BAR = {
    "kind": "bar",
    "spec": {
        "title": "Share of electricity from renewable sources (%)",
        "xLabel": "Country",
        "yLabel": "Percentage",
        "labels": ["Country A", "Country B", "Country C", "Country D", "Country E"],
        "datasets": [
            {"label": "Solar", "data": [12, 18, 8, 22, 15]},
            {"label": "Wind", "data": [25, 14, 30, 10, 20]},
            {"label": "Hydro", "data": [35, 42, 28, 38, 45]},
        ],
    },
}

WATER_TREATMENT_PROCESS = {
    "kind": "process",
    "spec": {
        "title": "Municipal wastewater treatment",
        "steps": [
            {"id": "screen", "label": "Screening"},
            {"id": "grit", "label": "Grit removal"},
            {"id": "primary", "label": "Primary settling"},
            {"id": "bio", "label": "Biological treatment"},
            {"id": "secondary", "label": "Secondary settling"},
            {"id": "disinfect", "label": "Disinfection"},
            {"id": "discharge", "label": "Treated water discharge"},
        ],
        "edges": [
            ["screen", "grit"],
            ["grit", "primary"],
            ["primary", "bio"],
            ["bio", "secondary"],
            ["secondary", "disinfect"],
            ["disinfect", "discharge"],
        ],
    },
}

ENERGY_CONSUMPTION_LINE = {
    "kind": "line",
    "spec": {
        "title": "Population aged 65+ (%) — three countries",
        "xLabel": "Year",
        "yLabel": "Percentage",
        "labels": ["1940", "1960", "1980", "2000", "2020", "2040"],
        "datasets": [
            {"label": "Country A", "data": [5, 8, 12, 18, 24, 32]},
            {"label": "Country B", "data": [7, 10, 14, 20, 28, 38]},
            {"label": "Country C", "data": [4, 6, 9, 14, 20, 28]},
        ],
    },
}

VILLAGE_MAP = {
    "kind": "map",
    "spec": {
        "title": "Chorleywood village — 1995 and present",
        "panels": [
            {
                "label": "1995",
                "features": ["Village centre", "Main road", "Park", "Few houses"],
            },
            {
                "label": "Present",
                "features": ["Motorway", "Station", "Housing estates", "Golf course", "Expanded centre"],
            },
        ],
    },
}
