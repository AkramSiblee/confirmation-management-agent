"""
E-confirmation platform integration — NOT YET IMPLEMENTED.

Native platform exports (see sample_data workbook's "E-Confirmation
Platform Export" tab for the shape: Confirmation_ID, Status_Code like
RESP-RECV / PEND-BANK, etc.) use provider-specific column names and
status vocabularies that must never surface directly in the tracker.
tracking.normalize_econfirmation_export() is the entry point that will
call into a provider-specific normalizer placed in this package (e.g.
a future confirmation_dot_com.py) once a real platform integration is
built. Kept as its own package (separate from integrations/google/)
because provider APIs here are unrelated to Gmail/Drive and may grow
to support more than one platform.
"""
