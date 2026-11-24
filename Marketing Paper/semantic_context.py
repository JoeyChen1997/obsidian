"""Local discourse patterns for candidate theoretical relations in PDF text."""

import re


BREAK = re.compile(r"""(?<!et al)(?<!\be\.g)(?<!\bi\.e)[.!?](?:[”’"')]+)?(?=\d{0,3}\s+[A-Z]|$)""")
BODY_CITE = re.compile(
    r"\b[A-ZÀ-Þ][\w’'-]{1,}(?:\s+et al\.|(?:,\s*[A-ZÀ-Þ][\w’'-]+){0,2}"
    r"(?:,?\s+(?:and|&)\s+[A-ZÀ-Þ][\w’'-]+))?(?:['’]s)?"
    r"\s*,?\s*(?:\(\s*(?:18|19|20)\d\d[a-z]?(?=\s*[,;)])|"
    r"\s(?:18|19|20)\d\d[a-z]?(?=\s*[,;).]))")
PRIOR = re.compile(r"\b(?:model|framework|assumption|equilibrium|result|finding|"
                   r"assum(?:e|es|ed)|show(?:s|ed)|find(?:s)?|develop(?:s|ed)|"
                   r"study|studies|consider(?:s|ed)|analy[sz](?:e|es|ed)|examine[sd]?)\b", re.I)
DISCOURSE = re.compile(
    r"^\s*(?:\d{1,3}\s*)?(?:(?:by|in) contrast\b|unlike\b|whereas\b|however\b|"
    r"conversely\b|instead\b|we (?:relax|extend|generaliz\w*|depart from|build on|adopt|"
    r"retain|replicate|confirm|differ)\b|our (?:model|framework|approach) (?:extends?|differs?)\b)", re.I)
OWN_MODEL = re.compile(r"\b(?:we (?:assume|allow|consider|model|focus|introduce|incorporate|study|"
                       r"relax|extend|generaliz\w*|build|adopt|retain|differ|depart|add|let)|"
                       r"(?:our|this) (?:model|framework|analysis|setting))\b", re.I)
OUTCOME = re.compile(r"\b(?:we (?:show|find|obtain|confirm|replicate|demonstrate)|"
                     r"our (?:results?|findings?|conclusions?))\b", re.I)
JOINT = re.compile(r"^\s*(?:\d{1,3}\s*)?(?:both|these|the two) (?:papers|studies|models)"
                   r" (?:both )?(?:assume|feature|use|model|consider|take|treat|abstract from|do not)\b", re.I)
EQUIVALENCE = re.compile(r"\b(?:their (?:results?|model|equilibrium) (?:is|are) (?:interpretable|equivalent|"
                         r"obtained|recovered)|(?:we|our model) (?:can )?(?:replicate|recover|nest) "
                         r"(?:their|this|the) (?:results?|model|equilibrium))\b", re.I)
ORDINAL = re.compile(r"^\s*The (?P<rank>first|second) (?:paper |study |model )?(?:examines|considers|studies|"
                     r"models|analy[sz]es|develops|assumes|investigates)\b", re.I)
SCOPE_END = re.compile(r"^\s*(?:\d{1,3}\s*)?(?:The (?:first|second|third|next|other)\b|"
                       r"Another (?:paper|study|stream)\b|We (?:next|now) turn\b)", re.I)
DIMENSIONS = (
    (re.compile(r"\bexogen\w*\b", re.I), re.compile(r"\bendogen\w*\b", re.I)),
    (re.compile(r"\bdeterministic\b", re.I), re.compile(r"\b(?:probabilistic|stochastic|random)\b", re.I)),
    (re.compile(r"\b(?:simultaneous\w*|simultaneity)\b", re.I), re.compile(r"\b(?:sequential\w*|sequentiality)\b", re.I)),
    (re.compile(r"\b(?:symmetric|symmetry|homogeneous)\b", re.I), re.compile(r"\b(?:asymmetric|asymmetry|heterogeneous)\b", re.I)),
    (re.compile(r"\b(?:complete|perfect|full) information\b", re.I), re.compile(r"\b(?:incomplete|imperfect|private) information\b", re.I)),
    (re.compile(r"\b(?:monopoly|monopolist)\b", re.I), re.compile(r"\b(?:duopoly|oligopoly|competitive market)\b", re.I)),
)
STOP = set("""they their these those them about above also between both across using under this that
with from other which where when whose paper papers study studies model models framework analysis
results result findings setting assumption assumptions show find consider examines work allow allows
assume assumes extend develop earlier later approach compared different contrast common effect
effects important relationship previous our per can may would must will there thus therefore""".split())
WORD = re.compile(r"[A-Za-z]{4,}")


def vocabulary(text):
    return {w.casefold() for w in WORD.findall(text)} - STOP


def dimension_change(earlier, later):
    """Opposite values on a model dimension, with an overlapping subject."""
    for left, right in DIMENSIONS:
        for a, b in ((left, right), (right, left)):
            am, bm = a.search(earlier), b.search(later)
            if am and bm and not b.search(earlier) and not a.search(later):
                # Rates set 'endogenously', as well as 'endogenous rates', remain local.
                shared = vocabulary(earlier[max(0, am.start()-70):am.end()+70]) & vocabulary(
                    later[max(0, bm.start()-70):bm.end()+70])
                if shared:
                    return 'endogenizes' if a is DIMENSIONS[0][0] else 'contrasts_assumptions'
    return None


def sentences(text):
    start = 0
    out = []
    for m in BREAK.finditer(text):
        if text[start:m.end()].strip():
            out.append((start, m.end()))
        start = m.end()
    if text[start:].strip():
        out.append((start, len(text)))
    return out


def cross_kind(prior, own):
    lowered = own.strip().casefold()
    if re.search(r"\bwe (?:relax|extend|generaliz\w*|build on)\b|\bour (?:model|framework) extends\b", lowered):
        if re.search(r"\b(?:this|that|the) (?:assumption|model|framework|setting|approach|analysis)|"
                     r"\b(?:their|these) (?:model|results|assumptions|findings|approach)\b", lowered):
            return 'extends_component'
    if re.search(r"\bwe (?:adopt|retain|follow|use) (?:this|their|the same)\b", lowered):
        return 'adopts_component'
    if EQUIVALENCE.search(own):
        return 'maps_model_component'
    if change := dimension_change(prior, own):
        return change
    shared = vocabulary(prior) & vocabulary(own)
    if re.search(r"\bwe (?:replicate|confirm|recover) (?:their|this|these)\b", lowered):
        return 'supports_result'
    if re.search(r"\b(?:their|these|this) (?:results?|findings?|conclusions?)\b.{0,40}"
                 r"\b(?:hold(?:s)? only|no longer hold|need(?:s)? not hold|fail(?:s)? to hold|are special to)\b",
                 lowered):
        return 'limits_result'
    if not DISCOURSE.search(own) or not shared:
        return None
    if OWN_MODEL.search(own):
        return 'contrasts_assumptions'
    if OUTCOME.search(own) and re.search(r"\b(?:show|find|result|conclude|predict)\w*\b", prior, re.I):
        return 'contrasts_results'
    return None


def discourse_relations(text, matches, spans):
    """Yield (match, kind, start, stop, method). Citation identity is resolved by the caller."""
    bounds = sentences(text)
    found_by_sentence = [[] for _ in bounds]
    for idx, (a, b) in enumerate(bounds):
        found_by_sentence[idx] = [m for m in matches if a <= m.start() < b]
    for idx, same in enumerate(found_by_sentence):
        if not same or idx+1 == len(bounds):
            continue
        a, b = bounds[idx]
        citation_sentence = text[a:b]
        cited_spans = sum(a <= m.start() < b for m in spans)
        lo, hi = bounds[idx+1]
        following = text[lo:hi]
        # A unique antecedent; stop at the next citation or topic marker.
        if (len(same) == cited_spans == 1 and PRIOR.search(citation_sentence)
                and not any(lo <= m.start() < hi for m in spans) and not SCOPE_END.search(following)):
            if (DISCOURSE.search(following) or EQUIVALENCE.search(following)
                    or re.match(r"^\s*(?:their|these|this) (?:finding|result|conclusion)", following, re.I)):
                if kind := cross_kind(citation_sentence, following):
                    yield same[0], kind, a, hi, 'adjacent_sentences'
        # Explicit plural anchor: 'A and B ... . These papers feature ...'.
        if 2 <= cited_spans <= 5 and JOINT.search(following):
            if any(lo <= m.start() < hi for m in spans):
                continue
            for k in range(idx+2, min(idx+5, len(bounds))):
                x, y = bounds[k]
                own = text[x:y]
                if SCOPE_END.search(own) or any(x <= m.start() < y for m in spans):
                    break
                if kind := cross_kind(following, own):
                    for m in same:
                        yield m, kind, a, y, 'explicit_group_comparison'
                    break
        # Ordered anchors: 'two papers: A and B. The first examines ...'.
        if cited_spans == 2 and re.search(r"\btwo (?:papers|studies)\b.{0,32}:", citation_sentence, re.I):
            if not (ordinal := ORDINAL.search(following)):
                continue
            targets = [m for m in spans if a <= m.start() < b]
            target = targets[0 if ordinal['rank'].lower() == 'first' else 1]
            scoped = [m for m in same if m.start() <= target.start() < m.end()
                      or target.start() <= m.start() < target.end()]
            if len(scoped) != 1:
                continue
            for k in range(idx+2, min(idx+5, len(bounds))):
                x, y = bounds[k]
                own = text[x:y]
                if SCOPE_END.search(own) or any(x <= m.start() < y for m in spans):
                    break
                if EQUIVALENCE.search(own):
                    yield scoped[0], 'maps_model_component', a, y, 'explicit_ordinal_comparison'
                    break
