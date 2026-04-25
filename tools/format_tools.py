FORMAT_COMPARISON_DECL = {
    "name": "format_comparison",
    "description": (
        "Save one comparison row to the report. Call this once per category "
        "(Pricing, Compute, Storage, AI/ML, Use Cases)."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "category": {"type": "string"},
            "aws_details": {"type": "string"},
            "gcp_details": {"type": "string"},
            "azure_details": {"type": "string"},
            "winner": {"type": "string", "enum": ["AWS", "GCP", "Azure", "Tie"]},
        },
        "required": ["category", "aws_details", "gcp_details", "azure_details", "winner"],
    },
}

ADD_RECOMMENDATION_DECL = {
    "name": "add_recommendation",
    "description": "Add the final recommendation after all categories are done.",
    "parameters": {
        "type": "object",
        "properties": {
            "recommended_provider": {"type": "string", "enum": ["AWS", "GCP", "Azure"]},
            "reasoning": {"type": "string"},
            "caveats": {"type": "string"},
        },
        "required": ["recommended_provider", "reasoning", "caveats"],
    },
}

comparison_rows: list[dict[str, str]] = []
recommendation_store: dict[str, str] = {}
VALID_PROVIDERS = {"AWS", "GCP", "Azure", "Tie"}
REQUIRED_CATEGORIES = ["Pricing", "Compute", "Storage", "AI/ML", "Use Cases"]
MISSING_SENTINEL = "Insufficient data from research output."


def _clean_text(value: str) -> str:
    text = " ".join(str(value or "").split())
    if not text:
        return MISSING_SENTINEL
    return text[:220]


def _pick_winner_from_details(aws_details: str, gcp_details: str, azure_details: str) -> str:
    scores = {
        "AWS": sum(ch.isalnum() for ch in aws_details),
        "GCP": sum(ch.isalnum() for ch in gcp_details),
        "Azure": sum(ch.isalnum() for ch in azure_details),
    }
    max_score = max(scores.values())
    if max_score <= 0:
        return "Tie"
    top = [provider for provider, score in scores.items() if score == max_score]
    return top[0] if len(top) == 1 else "Tie"


def _normalize_category(value: str) -> str:
    lowered = str(value or "").strip().lower()
    aliases = {
        "pricing": "Pricing",
        "price": "Pricing",
        "cost": "Pricing",
        "compute": "Compute",
        "vm": "Compute",
        "storage": "Storage",
        "ai/ml": "AI/ML",
        "aiml": "AI/ML",
        "ai": "AI/ML",
        "ml": "AI/ML",
        "use cases": "Use Cases",
        "usecase": "Use Cases",
        "use case": "Use Cases",
    }
    return aliases.get(lowered, _clean_text(value))


def format_comparison(
    category: str,
    aws_details: str,
    gcp_details: str,
    azure_details: str,
    winner: str,
) -> str:
    normalized_category = _normalize_category(category)
    normalized_aws = _clean_text(aws_details)
    normalized_gcp = _clean_text(gcp_details)
    normalized_azure = _clean_text(azure_details)
    normalized_winner = str(winner).strip()
    if normalized_winner not in VALID_PROVIDERS:
        normalized_winner = _pick_winner_from_details(
            normalized_aws, normalized_gcp, normalized_azure
        )

    row = {
        "category": normalized_category,
        "AWS": normalized_aws,
        "GCP": normalized_gcp,
        "Azure": normalized_azure,
        "winner": normalized_winner,
    }

    # Replace existing category row to prevent duplicates.
    for idx, existing in enumerate(comparison_rows):
        if str(existing.get("category", "")).strip().lower() == normalized_category.lower():
            comparison_rows[idx] = row
            return f"Updated: {normalized_category} (winner: {normalized_winner})"

    comparison_rows.append(row)
    return f"Saved: {normalized_category} (winner: {normalized_winner})"


def add_recommendation(recommended_provider: str, reasoning: str, caveats: str) -> str:
    provider = str(recommended_provider).strip()
    if provider not in {"AWS", "GCP", "Azure"}:
        provider = infer_best_provider(no_tie=True)
    recommendation_store.update(
        {
            "provider": provider,
            "reasoning": _clean_text(reasoning),
            "caveats": _clean_text(caveats),
        }
    )
    return "Recommendation saved."


def _row_lookup() -> dict[str, dict[str, str]]:
    return {str(row.get("category", "")).strip(): row for row in comparison_rows}


def _tie_break_provider() -> str:
    rows = _row_lookup()
    # Deterministic tie-break order emphasizing cost + workload fit.
    priority_categories = ["Pricing", "AI/ML", "Compute", "Storage", "Use Cases"]
    for category in priority_categories:
        row = rows.get(category, {})
        winner = str(row.get("winner", "")).strip()
        if winner in {"AWS", "GCP", "Azure"}:
            return winner
    return "AWS"


def infer_best_provider(no_tie: bool = False) -> str:
    counts = {"AWS": 0, "GCP": 0, "Azure": 0}
    for row in comparison_rows:
        winner = str(row.get("winner", "")).strip()
        if winner in counts:
            counts[winner] += 1
    max_score = max(counts.values()) if counts else 0
    top = [provider for provider, score in counts.items() if score == max_score and score > 0]
    if len(top) != 1:
        if no_tie:
            return _tie_break_provider()
        return "Tie"
    return top[0]


def get_best_provider() -> str:
    if count_missing_categories() > 2:
        return "Insufficient data"
    provider = str(recommendation_store.get("provider", "")).strip()
    if provider in {"AWS", "GCP", "Azure"}:
        return provider
    return infer_best_provider(no_tie=True)


def get_provider_ranking() -> list[str]:
    if count_missing_categories() > 2:
        return []
    points = {"AWS": 0, "GCP": 0, "Azure": 0}
    for row in comparison_rows:
        winner = str(row.get("winner", "")).strip()
        if winner in points:
            points[winner] += 2
        elif winner == "Tie":
            for provider in points:
                points[provider] += 1
    ranking = sorted(points.keys(), key=lambda p: (-points[p], p))
    return ranking


def ensure_required_categories() -> None:
    existing = {str(row.get("category", "")).strip() for row in comparison_rows}
    for category in REQUIRED_CATEGORIES:
        if category in existing:
            continue
        format_comparison(
            category=category,
            aws_details=MISSING_SENTINEL,
            gcp_details=MISSING_SENTINEL,
            azure_details=MISSING_SENTINEL,
            winner="Tie",
        )


def count_missing_categories() -> int:
    count = 0
    for row in comparison_rows:
        aws = str(row.get("AWS", ""))
        gcp = str(row.get("GCP", ""))
        azure = str(row.get("Azure", ""))
        missing_tokens = ("insufficient data", "data unavailable")
        if (
            any(token in aws.lower() for token in missing_tokens)
            and any(token in gcp.lower() for token in missing_tokens)
            and any(token in azure.lower() for token in missing_tokens)
        ):
            count += 1
    return count


def get_comparison_markdown() -> str:
    ensure_required_categories()
    lines = [
        "| Category | AWS | GCP | Azure | Winner |",
        "|----------|-----|-----|-------|--------|",
    ]
    for row in comparison_rows:
        lines.append(
            f"| {row['category']} | {row['AWS']} | {row['GCP']} | "
            f"{row['Azure']} | {row['winner']} |"
        )

    md = "\n".join(lines)
    best = get_best_provider()
    ranking = get_provider_ranking()
    if recommendation_store or best:
        md += f"\n\n**Best Provider:** {best}\n"
        if ranking:
            md += (
                f"**Ranking:** 1) {ranking[0]}  2) {ranking[1]}  3) {ranking[2]}\n"
            )
        else:
            md += "**Ranking:** Not available due to insufficient evidence.\n"
        md += f"**Why:** {recommendation_store.get('reasoning', '')}\n"
        md += f"**Caveats:** {recommendation_store.get('caveats', '')}"
    return md
