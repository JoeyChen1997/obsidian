"""Query-time discovery of comparable assumptions, including pairs without an indexed citation."""

from collections import defaultdict
from itertools import combinations
import re

import corpus_rag
from semantic_context import BODY_CITE, sentences


# Only link text with the same explicitly named primitive and the same axis.
# Hypotheses are never added to the directed citation-derived graph.
PRIMITIVES = (
    ('advertising_rates', ('advertising rate', 'advertising rates', 'ad rate', 'ad rates'), ('determination',)),
    ('advertising_costs', ('advertising cost', 'advertising costs', 'ad cost', 'ad costs'), ('determination',)),
    ('advertising_exposure', ('advertising exposure', 'ad exposure', 'advertising reach', 'ad reach'),
     ('exposure',)),
    ('product_price', ('product price', 'product prices'), ('determination',)),
    ('retail_price', ('retail price', 'retail prices'), ('determination',)),
    ('wholesale_price', ('wholesale price', 'wholesale prices', 'wholesale pricing'),
     ('determination',)),
    ('product_quality', ('product quality', 'quality level', 'quality levels'),
     ('determination',)),
    ('market_entry', ('market entry', 'firm entry', 'seller entry', 'entry decision'),
     ('determination', 'timing')),
    ('consumer_information', ('consumer information', 'consumer knowledge'), ('determination', 'information')),
    ('consumer_awareness', ('consumer awareness',), ('determination',)),
    ('consumer_data', ('consumer data',), ('determination', 'information')),
    ('consumer_preferences', ('consumer preferences', 'consumer tastes', 'customer preferences'), ('heterogeneity',)),
    ('consumer_valuations', ('consumer valuations', 'customer valuations'), ('heterogeneity',)),
    ('consumer_search', ('consumer search',), ('timing',)),
    ('search_costs', ('search cost', 'search costs'), ('determination',)),
    ('promotion_timing', ('advertising and pricing', 'price and advertising', 'advertising spending and price'),
     ('timing',)),
    ('platform_entry', ('platform entry',), ('determination', 'timing')),
    ('platform_commission', ('platform commission', 'platform commissions', 'commission rate', 'commission rates'),
     ('determination',)),
    ('data_disclosure', ('information disclosure', 'information sharing', 'data sharing'),
     ('determination', 'timing')),
    ('product_compatibility', ('product compatibility', 'compatibility choice', 'compatibility choices'),
     ('determination', 'timing')),
    ('product_valuation', ('product valuation', 'product valuations', 'reservation values',
                           'reservation prices', 'valuation for each good'), ('heterogeneity', 'information')),
)
AXES = {
    'determination': (('exogenous', r'exogen\w*'), ('endogenous', r'endogen\w*')),
    'exposure': (('deterministic', r'deterministic'), ('probabilistic', r'probabilistic|stochastic|random')),
    'timing': (('simultaneous', r'simultaneous\w*'), ('sequential', r'sequential\w*')),
    'heterogeneity': (('homogeneous', r'homogeneous|identical'), ('heterogeneous', r'heterogeneous')),
    'information': (('public', r'public(?:ly known)?|common knowledge'), ('private', r'private')),
}
SCOPE = re.compile(r'\b(?:we (?:assume|model|allow|consider|set|take|treat|let|suppose)|'
                   r'(?:in|under) (?:our|the baseline|this) (?:model|setting|game|framework)|'
                   r'(?:our|the baseline|this) model|(?:is|are) (?:assumed|taken|treated) (?:to be|as|given))\b', re.I)
DISQUALIFY = re.compile(r'\b(?:whether|could|might|if|unlike|instead of|rather than|future research|'
                        r'previous studies|earlier studies|prior studies|other papers|'
                        r'(?:online |electronic )?appendix|e-companion|supplementary|'
                        r'relax(?:es|ed)?|no longer|need not|we do not|not)\b', re.I)
CONDITION = re.compile(r'\b(?:necessary|sufficient|required|only when|only if)\b', re.I)
GOOD_SECTIONS = ('model', 'results', 'other', 'unknown', 'abstract', 'introduction', 'discussion')


def phrase_pattern(aliases):
    return re.compile(r'\b(?:'+'|'.join(re.escape(x) for x in
                                        sorted(aliases, key=len, reverse=True))+r')\b', re.I)


PATTERNS = {key: phrase_pattern(aliases) for key, aliases, _ in PRIMITIVES}


def evidence(text, section, selected):
    """Extract only scoped assertions (not literature mentions or counterfactuals)."""
    if section not in GOOD_SECTIONS or not SCOPE.search(text):
        return
    for a, b in sentences(text):
        claim = text[a:b].strip()
        if not 30 <= len(claim) <= 480 or not SCOPE.search(claim):
            continue
        if BODY_CITE.search(claim) or DISQUALIFY.search(claim):
            continue
        for key, aliases, axes in PRIMITIVES:
            if key not in selected:
                continue
            for m in PATTERNS[key].finditer(claim):
                for axis in axes:
                    options = AXES[axis]
                    tags = []
                    for value, pattern in options:
                        pat = r'\b(?:'+pattern+r')\b'
                        if not re.search(pat, claim, re.I):
                            continue
                        # Bind the value to this exact primitive rather than any term in the sentence.
                        subject = re.escape(m[0])
                        bound = (r'\b(?:' + pattern + r')\s+' + subject + r'\b|'
                                 + r'\b' + subject + r'\b\s+(?:(?:is|are|be|remains?|occurs?|and|'
                                   r'becomes?|assumed|determined|treated|taken|as|to|given|'
                                   r'set|fixed|chosen|chosen to|set to|across|in time)\s+){0,6}' + pat)
                        if re.search(bound, claim, re.I):
                            tags.append(value)
                    if len(tags) == 1 and sum(bool(re.search(r'\b(?:'+p+r')\b', claim, re.I))
                                               for _, p in options) == 1:
                        yield (key, axis, tags[0], m[0].lower(), claim)


def compare(rag, seeds, terms, journals=(), from_year=None, to_year=None, limit=8):
    seeds = list(dict.fromkeys(seeds))[:12]
    selected = {key for key, pat in PATTERNS.items() if any(pat.search(t) for t in terms)}
    # Exact named primitives in the prompt focus the expensive corpus-wide expansion.
    if not selected:
        return {'pairs': [], 'expanded_primitives': [], 'seed_count': len(seeds),
                'note': 'For a mechanism comparison add specific search phrases, e.g. advertising exposure or wholesale price.'}
    chosen = [p for p in PRIMITIVES if p[0] in selected][:4]
    selected = {p[0] for p in chosen}
    records = defaultdict(dict)
    used = set()
    seed_set = set(seeds)
    section_quality = {'model': 4, 'results': 3, 'abstract': 2, 'other': 2}

    def add(row):
        pid, paper, page, section, text = row
        if pid in used:
            return
        used.add(pid)
        for key, axis, value, alias, claim in evidence(text, section, selected):
            rank = (section_quality.get(section, 1), len(alias), -page)
            slot = records[key, axis]
            if (prior := slot.get((paper, value))) is None or rank > prior[0]:
                slot[paper, value] = rank, {'paper_id': paper, 'page': page, 'section': section,
                                            'passage': pid, 'value': value, 'term': alias, 'excerpt': claim,
                                            'role': 'conditional_statement' if CONDITION.search(claim)
                                            else 'model_statement_candidate'}

    for seed in seeds:
        lo = seed * corpus_rag.PASSAGE_BASE
        for row in rag.execute('SELECT rowid,paper,page,section,text FROM passages WHERE rowid>=? AND rowid<?',
                               (lo, lo + corpus_rag.PASSAGE_BASE)):
            add(row)

    filters = []
    params = []
    if journals:
        filters.append('upper(d.journal) IN ('+','.join('?' for _ in journals)+')')
        params.extend(v.upper() for v in journals)
    if from_year is not None:
        filters.append('d.year>=?')
        params.append(from_year)
    if to_year is not None:
        filters.append('d.year<=?')
        params.append(to_year)
    where = ''.join(' AND '+f for f in filters)
    for key, aliases, axes in chosen:
        lhs = '('+' OR '.join('"'+x+'"' for x in aliases)+')'
        values = {
            'determination': ('exogen*', 'endogen*'), 'timing': ('simultaneous*', 'sequential*'),
            'exposure': ('deterministic', 'probabilistic', 'stochastic', 'random'),
            'heterogeneity': ('homogeneous', 'identical', 'heterogeneous'), 'information': ('public', 'private'),
        }
        for axis in axes:
            # Query both sides separately so rare alternatives are not crowded out.
            for term in values[axis]:
                query = f'{lhs} AND {term}'
                for row in rag.execute(f'''SELECT p.rowid,p.paper,p.page,p.section,p.text FROM passages p
                         JOIN docs d ON d.id=p.paper WHERE passages MATCH ?{where}
                         ORDER BY rank LIMIT 140''', (query, *params)):
                    add(row)

    # Only surface comparisons involving a search seed if that facet has seeded evidence.
    # Otherwise the fallback requires opposing values and returns fewer pairs.
    ranked = []
    for (key, axis), entries in records.items():
        canonical = defaultdict(dict)
        for (paper, value), item in entries.items():
            canonical[paper][value] = item
        one = [(p, next(iter(v.values()))) for p, v in canonical.items() if len(v) == 1]
        one.sort(key=lambda item: (item[0] not in seed_set, -item[1][0][0], item[0]))
        one = one[:42]
        has_seed = any(p in seed_set for p, _ in one)
        for (p, (ar, a)), (q, (br, b)) in combinations(one, 2):
            seeded = int(p in seed_set)+int(q in seed_set)
            different = a['value'] != b['value']
            if (has_seed and not seeded) or (not has_seed and not different):
                continue
            if not different and seeded < 1:
                continue
            rank = (-int(different), -seeded, -min(ar[0],br[0]), -(ar[0]+br[0]), p, q)
            ranked.append((rank, key, axis, different, a, b))
    ranked.sort(key=lambda x: x[0])
    pairs, done, per_facet = [], set(), defaultdict(int)
    for _, key, axis, different, a, b in ranked:
        p, q = a['paper_id'], b['paper_id']
        pair = min(p,q), max(p,q)
        if pair in done or per_facet[key,axis] >= (4 if any(x in seed_set for x in pair) else 2):
            continue
        cit = rag.execute('SELECT 1 FROM links WHERE (citing=? AND cited=?) OR (citing=? AND cited=?) LIMIT 1',
                          (p,q,q,p)).fetchone()
        if cit:
            continue
        documents = dict((r['id'], dict(r)) for r in rag.execute(
            'SELECT id,title,year AS filename_year,relpath,journal FROM docs WHERE id IN (?,?)', (p,q)))
        if len(documents) != 2 or corpus_rag.normalized_title(documents[p]['title']) == corpus_rag.normalized_title(documents[q]['title']):
            continue
        done.add(pair)
        per_facet[key,axis] += 1
        papers = sorted((a,b), key=lambda v: (documents[v['paper_id']]['filename_year'] or 9999, v['paper_id']))
        pairs.append({'primitive': key, 'axis': axis, 'kind': 'different_modeling_choice' if different else 'parallel_modeling_choice',
                      'state': 'comparison_hypothesis', 'direct_citation': 'not_found_in_local_index',
                      'evidence': [ev | {'paper': documents[ev['paper_id']]} for ev in papers]})
        if len(pairs) >= limit:
            break
    return {'pairs': pairs, 'expanded_primitives': sorted(selected), 'seed_count': len(seeds),
            'note': 'Two independently located excerpts suggest a comparison. No inheritance, priority or absence of citation is established.'}
