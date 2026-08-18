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
        "referral to", "state bar", "referred to the bar",
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

# remove negated sanction spans ("no monetary sanctions", "declined to impose") so a
# negated keyword can't set a tier. Runs before tier matching in both coding paths.
_NEG_SPAN = re.compile(
    r"\bno\s+(?:\w+\s+){0,3}?(sanction|monetar|fine|penalt|fee|cost|discipl|referr|"
    r"suspens|contempt|disqualif)\w*|declin\w+\s+to\s+(impose|award)|"
    r"denied\s+the\s+motion\s+for\s+sanctions|motion\s+for\s+sanctions\s+(is\s+)?denied", re.I)

def _strip_negated(text):
    return _NEG_SPAN.sub(" ", text)

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
    """Return an integer severity tier 0-4 (0 none .. 4 professional/terminal).

    Two paths, on purpose:
    - is_full_opinion=False  -> Charlotin's short `Outcome` field. The field *is* the
      outcome, so any tier keyword present sets that tier (original ladder, unchanged).
    - is_full_opinion=True   -> a full control opinion. Here a tier keyword appearing
      anywhere is NOT enough (legal prose mentions "dismiss"/"discipline" incidentally),
      so we require (a) a sanctions region, (b) no denial language, and (c) an actual
      imposition cue near the sanction type. This is what stops the controls over-coding
      to tier 4.
    """
    if not isinstance(text_or_outcome, str) or not text_or_outcome:
        return 0
    if is_full_opinion:
        return _severity_full(text_or_outcome)
    s = _strip_negated(str(text_or_outcome).lower())
    for tier in (4, 3, 2, 1):
        if any(k in s for k in _TIER[tier]):
            return tier
    return 0


# --- full-opinion severity: require an IMPOSED sanction, not just the topic ---
_DENIAL = re.compile(
    r"(sanctions?\s+(are|is|were|was)?\s*denied|deny(ing)?\s+the\s+motion\s+for\s+sanctions|"
    r"declin\w*\s+to\s+(impose|award)|no\s+sanctions?\s+(are|is|were|will|shall)|"
    r"motion\s+for\s+sanctions\s+is\s+denied|denying\s+.{0,20}sanctions)", re.I)
_IMPOSE = re.compile(
    r"(impos\w+|grant\w+|award\w+|we\s+sanction|is\s+sanctioned|are\s+sanctioned|"
    r"order\w*\s+to\s+pay|shall\s+pay|ordered\s+to|refer\w+|suspend\w+|disbar\w+|"
    r"disqualif\w+|struck|stricken|dismiss\w+|fined|held\s+in\s+contempt|accepts?\s+the\s+agreement)", re.I)
_T4F = re.compile(
    r"(bar\s+referr|referred\s+to\s+the\s+(state\s+)?bar|suspen\w+|disbar|disqualif|pro\s+hac\s+vice|"
    r"held\s+in\s+contempt|contempt\s+of\s+court|vexatious|dismiss\w*\s+as\s+a\s+sanction|"
    r"terminating\s+sanction|censure|disciplin\w+|referr\w*\s+to\s+(the\s+)?(state\s+)?bar|state\s+bar)", re.I)
_T3F = re.compile(
    r"(monetary\s+sanction|monetary\s+penalt|\bfine[ds]?\b|attorney'?s?\s+fees|adverse\s+costs|"
    r"shall\s+pay|ordered\s+to\s+pay|disgorge|sanction\w*\s+of\s+\$)", re.I)
_T2F = re.compile(
    r"(show\s+cause|struck|stricken|strike|waiv\w+|mandatory\s+cle|\bcle\b|certif\w+|"
    r"refile|amend\w*\s+(the\s+)?(brief|filing))", re.I)
_T1F = re.compile(r"(warning|admonish|caution|reprimand|rebuke|chastis)", re.I)

def _severity_full(text):
    region = locate_sanction_region(text)
    if not region:
        return 0
    region = _strip_negated(region)
    if _DENIAL.search(region):
        return 0
    imposed = bool(_IMPOSE.search(region))
    if _T4F.search(region) and imposed: return 4
    if _T3F.search(region) and imposed: return 3
    if _T2F.search(region) and imposed: return 2
    if _T1F.search(region):             return 1
    return 0


# --- frame filter: standalone bar-discipline proceedings are not Rule 11 litigation
#     sanctions, so they are not comparable to AI-hallucination cases. Drop them. ---
_BARDISC = re.compile(
    r"(bar\s+association|disciplinary\s+(proceeding|matter|board|counsel)|\brule\s*6\b|"
    r"reinstatement|resign\w*\s+with\s+disciplin|licensed\s+to\s+practice)", re.I)

def is_bar_discipline(text):
    """True for standalone attorney-discipline proceedings (wrong control population)."""
    return bool(isinstance(text, str) and _BARDISC.search(text))

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
