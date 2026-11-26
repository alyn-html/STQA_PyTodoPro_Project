"""
Manual test-case IDs from Weeks 1-5 that the automated tests trace back to.

IDs that the Week 1-5 findings reports name exactly (TC-WB-xxx, TC-USA-xxx,
TC-GUI-012/013, TC-CMP-001/005, API-xxx, SEC-xxx) are written in full inside
the test files.

The black-box report lists TC-BB-001..028 but not which ID tests which
behaviour, and the Week 3 report names only some TC-GUI / TC-ACC IDs. Those are
kept HERE as placeholders. Replace each right-hand value with the real ID from
your test-case sheet; reports/traceability.csv is regenerated on the next run,
so the mapping lives in one place.
"""

BB = {
    "register_valid":    "TC-BB-?? Registration EP valid",
    "register_invalid":  "TC-BB-?? Registration EP/BVA invalid",
    "register_dup":      "TC-BB-?? Duplicate username (DEF-003)",
    "register_second":   "TC-BB-?? Second account same browser (DEF-004)",
    "login":             "TC-BB-?? Login decision table",
    "logout":            "TC-BB-?? Logout / protected routes state transition",
    "create":            "TC-BB-?? Create task EP",
    "due_5digit":        "TC-BB-?? Due date EP 5-digit year (DEF-001)",
    "urgency":           "TC-BB-?? Urgency BVA -2/-1/+1/+2/+3/blank",
    "urgency_today":     "TC-BB-?? Urgency BVA =0 (DEF-002)",
    "edit":              "TC-BB-?? Edit task",
    "toggle":            "TC-BB-?? Done/reopen state transition",
    "delete":            "TC-BB-?? Delete task state transition",
    "filters":           "TC-BB-?? Filter decision table (category/status/q)",
    "dashboard":         "TC-BB-?? Dashboard counters state transition",
}

GUI = {
    "nav":           "TC-GUI-?? Links & navigation",
    "forms":         "TC-GUI-?? Forms / date picker",
    "buttons":       "TC-GUI-?? Buttons / toggle",
    "messages":      "TC-GUI-?? Messages",
    "data_display":  "TC-GUI-?? Data display (titles, badges)",
    "delete_confirm": "TC-GUI-012",
    "filters_persist": "TC-GUI-013",
}

ACC = {
    "labels":        "TC-ACC-?? Labels associated (DEF-010)",
    "filter_names":  "TC-ACC-?? Filter control names (DEF-016)",
    "toggle_name":   "TC-ACC-?? Toggle button name (DEF-014)",
    "table_headers": "TC-ACC-?? Table headers (DEF-019)",
    "axe":           "TC-ACC-?? axe-core WCAG 2 A/AA scan",
}
