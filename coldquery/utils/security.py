def sanitize_identifier(ident: str) -> str:
    """
    Sanitize a PostgreSQL identifier.
    Double-quotes the identifier and escapes internal quotes.
    """
    if not ident:
        raise ValueError("Identifier cannot be empty")

    # Postgres escaping for identifiers: Replace " with ""
    safe_ident = ident.replace('"', '""')
    return f'"{safe_ident}"'
