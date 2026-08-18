"""
label_lib.py  —  one coding pipeline for BOTH arms (AI cases and non-AI controls).

The point of this module: code the AI cases and the control cases the SAME way,
from the SAME kind of source (the underlying opinion text), so that an "AI vs non-AI"
comparison isn't contaminated by differences in how the two groups were labeled.

Every rule here is defined in LABELING_CODEBOOK.md. If you change a rule, change it
in both places.
"""
import re

# ----------------------------------------------------------------------
# 1. SEVERITY  (ordinal 0-4; see codebook). Assign the MOST SEVERE tier present.
# ----------------------------------------------------------------------
_TIER = {
    4: ["bar referr", "disciplinary referr", "grievance", "referred to the",
        "suspend", "suspension", "disbar", "disqualif", "pro hac vice",
        "revoc", "revoked", "contempt", "vexatious", "filing bar",
        "dismiss", "default judgment", "terminat", "struck the case", "censure"],
    3: ["monetary", "fine", "sanction of $", "costs order", "adverse cost",
        "attorney's fee", "attorneys' fee", "attorney fee", "fees and cost",
        "pay the", "disgorge", "$"],
    2: ["order to show cause", "show cause", "order to explain", "struck", "stricken",
        "strike", "waived", "forfeit", "disregard", "cle ", "continuing legal education",
        "certif", "disclos", "corrected filing", "refile", "amend", "notify the client"],
    1: ["warning", "admonish", "caution", "reprimand", "rebuke", "displeasure", "chastis"],
}
_NO_SANCTION = ["no sanction", "sanctions denied", "motion for sanctions is denied",
                "declined to impose", "no monetary", "no further action", "not sanction"]

_TRIGGER = re.compile(r"(rule\s*11|§?\s*1927|section\s*1927|inherent\s+authority|"
                      r"sanction|show\s+cause|disciplin|referr)", re.I)

def locate_sanction_region(text, window=1200):
    """Return the slice of an opinion around the first sanctions trigger.
    Coding severity on the whole opinion invites false hits; code the region."""
    if not text:
        return ""
    m = _TRIGGER.search(text)
    if not m:
        return ""                      # no sanctions discussion found
    i = m.start()
    return text[max(0, i - 200): i + window]

def code_severity(text_or_outcome, is_full_opinion=False):
    """Return an integer severity tier 0-4.
    - For CONTROL opinions (raw text): pass is_full_opinion=True so we first
      locate the sanctions region.
    - For Charlotin's short `Outcome` field: pass is_full_opinion=False.
    Both paths then run the identical tier ladder."""
    if not isinstance(text_or_outcome, str) or not text_or_outcome:
        return 0
    s = (locate_sanction_region(text_or_outcome) if is_full_opinion
         else str(text_or_outcome)).lower()
    if not s:
        return 0
    # explicit "no sanction" wins only if no higher tier keyword is present
    for tier in (4, 3, 2, 1):
        if any(k in s for k in _TIER[tier]):
            return tier
    if any(k in s for k in _NO_SANCTION):
        return 0
    return 0

# ----------------------------------------------------------------------
# 2. REPRESENTATION  (pro se vs counseled). Return 1, 0, or None (unclear).
# ----------------------------------------------------------------------
_PROSE = re.compile(r"\b(pro\s+se|self[-\s]represent|in\s+propria\s+persona|"
                    r"without\s+counsel|appearing\s+pro\s+se)\b", re.I)

def code_pro_se(text=None, docket_attorney_present=None, sanctioned_is_attorney=None):
    """Decision order (codebook): docket attorney field -> text markers ->
    'sanctioned actor is the attorney' implies counseled. Unclear -> None."""
    if docket_attorney_present is not None:          # most reliable
        return 0 if docket_attorney_present else 1
    if sanctioned_is_attorney:                        # a lawyer was sanctioned -> counseled
        return 0
    if isinstance(text, str) and _PROSE.search(text):
        return 1
    return None                                       # do NOT guess

# ----------------------------------------------------------------------
# 3. CONTAMINATION FILTER  (controls only). True = drop, it's actually an AI case.
# ----------------------------------------------------------------------
_AI = re.compile(r"(hallucinat|fabricated\s+(cit|case|authorit)|non[-\s]?existent\s+case|"
                 r"chatgpt|\bgpt\b|generative\s+a\.?i|\bllm\b|google\s+bard|\bclaude\b|"
                 r"artificial\s+intelligence.{0,40}(cit|case))", re.I)

def is_ai_contaminated(text):
    """A 'non-AI' control that mentions AI-fabrication markers is not a clean control."""
    return bool(isinstance(text, str) and _AI.search(text))

# ----------------------------------------------------------------------
# 4. LEGAL FIELD  (prefer structured Nature-of-Suit code over text).
# ----------------------------------------------------------------------
_NOS = {  # partial map; extend from the federal NOS code list
    "190": "contract", "110": "contract", "196": "contract",
    "440": "civil rights", "442": "civil rights", "443": "civil rights", "550": "civil rights",
    "360": "tort", "365": "tort", "380": "tort",
    "710": "employment", "442e": "employment",
    "895": "administrative", "899": "administrative",
    "422": "bankruptcy", "423": "bankruptcy",
    "463": "immigration", "465": "immigration",
    "820": "IP", "830": "IP", "840": "IP",
    "530": "habeas", "540": "habeas",
    "870": "tax",
}
def field_from_nos(nos_code):
    """Return field from a federal Nature-of-Suit code, else None (fall back to text)."""
    if nos_code is None:
        return None
    return _NOS.get(str(nos_code).strip().lower(), "other")

# ----------------------------------------------------------------------
# 5. ONE-SHOT: code a whole case into a dict (both arms use this).
# ----------------------------------------------------------------------
def code_case(text, ai_flag, nos_code=None, docket_attorney_present=None,
              sanctioned_is_attorney=None):
    """Run every coder on one case. `text` is the opinion text (controls) OR the
    Charlotin Outcome/Details (AI arm). Returns a flat dict ready for a DataFrame."""
    return {
        "ai": int(ai_flag),
        "severity": code_severity(text, is_full_opinion=(ai_flag == 0)),
        "pro_se": code_pro_se(text, docket_attorney_present, sanctioned_is_attorney),
        "field": field_from_nos(nos_code),
        "contaminated": (is_ai_contaminated(text) if ai_flag == 0 else False),
    }
