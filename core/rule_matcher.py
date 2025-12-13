# ============================================================
# SMART RULE MATCHING (Final)
# ============================================================

def rule_matches(rule_text, filename):
    """
    Matches a rule against a filename using:
    - Tail match (last tokens)
    - Full token matches
    - Strict initials
    """

    rule = rule_text.lower().strip()
    filename = filename.lower().strip()

    parts = rule.split()

    # Tail choices
    tail1 = parts[-1]
    tail2 = " ".join(parts[-2:]) if len(parts) >= 2 else tail1

    # Head tokens (everything BEFORE the tail phrase)
    head_tokens = parts[:-2] if tail2 in rule else parts[:-1]

    # Extract initials
    initials = [p[0] for p in head_tokens]
    combined_initials = "".join(initials)

    # Extract name block
    block = filename.split(" - ")[-1] if " - " in filename else filename
    block = block.replace(".pdf", "").strip()
    block_tokens = block.split()

    # -------------------------
    # Tail must match first
    # -------------------------
    if not (tail2 in block or tail1 in block):
        return False

    # If only tail exists → match
    if not head_tokens:
        return True

    # -------------------------
    # Full token match
    # -------------------------
    for token in head_tokens:
        if token in block_tokens:
            return True

    # -------------------------
    # Merged initials match
    # Example: initials ['b','j'] → match "bj"
    # -------------------------
    for token in block_tokens:
        if token.startswith(combined_initials):
            return True

    # -------------------------
    # All initials must appear individually
    # -------------------------
    return all(
        any(token.startswith(init) or token == init for token in block_tokens)
        for init in initials
    )

