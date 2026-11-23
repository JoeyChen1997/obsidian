"""Local, resumable catalog and page-level full-text index for paperlist PDFs."""

import argparse
import asyncio
import concurrent.futures as futures
from contextlib import closing, contextmanager
import json
import multiprocessing
import os
from pathlib import Path
import re
import sqlite3
import sys
import time
import unicodedata


JOURNAL_ORDER = ('MKSC', 'JMR', 'MS', 'RAND', 'AEJ_MICRO', 'JPE_MICRO',
                 'AER_INSIGHT', 'RES', 'ECMA', 'JPE', 'QJE', 'AER')
PAGE_STRIDE = 1_000_000
FILE_INFO = re.compile(r'^(.*?)_((?:18|19|20)\d{2})_(.*)$')
STATUSES = ('pending', 'indexed', 'partial', 'no_text', 'error', 'missing')
LOCAL_DATA = Path(os.environ.get('LOCALAPPDATA') or Path.home() / '.local' / 'share')
DEFAULT_DB = LOCAL_DATA / 'PaperlistResearch' / 'papers.sqlite3'
DEFAULT_ROOT = Path(r'C:\paperlist')

SCHEMA = '''
CREATE TABLE IF NOT EXISTS papers (
    id INTEGER PRIMARY KEY, relpath TEXT NOT NULL UNIQUE, journal TEXT NOT NULL,
    author_hint TEXT NOT NULL, year INTEGER, title_hint TEXT NOT NULL,
    size INTEGER NOT NULL, mtime_ns INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending', pages INTEGER, text_pages INTEGER,
    error TEXT
);
CREATE INDEX IF NOT EXISTS paper_status ON papers(status, journal);
CREATE VIRTUAL TABLE IF NOT EXISTS catalog USING fts5(
    title, author, tokenize='unicode61 remove_diacritics 2'
);
CREATE VIRTUAL TABLE IF NOT EXISTS page_index USING fts5(
    paper_id UNINDEXED, pdf_page UNINDEXED, body,
    tokenize='unicode61 remove_diacritics 2'
);
CREATE TABLE IF NOT EXISTS ocr_attempts (rowid INTEGER PRIMARY KEY, result TEXT NOT NULL, error TEXT);
CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL);
'''


def configure_output():
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding='utf-8', errors='backslashreplace')


def connect(path, writable=False):
    path = path.resolve()
    if writable:
        path.parent.mkdir(parents=True, exist_ok=True)
        con = sqlite3.connect(path, timeout=20)
        con.execute('PRAGMA journal_mode=WAL')
        con.execute('PRAGMA synchronous=NORMAL')
        con.execute('PRAGMA cache_size=-65536')
        con.executescript(SCHEMA)
    else:
        if not path.is_file():
            raise ValueError(f'Index not found: {path}. Run build first.')
        con = sqlite3.connect(path.as_uri() + '?mode=ro', uri=True, timeout=20)
    con.row_factory = sqlite3.Row
    return con


@contextmanager
def build_lock(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.with_suffix('.build.lock').open('a+b') as lock:
        lock.seek(0)
        if os.name == 'nt':
            import msvcrt
            try:
                msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
            except OSError as exc:
                raise ValueError('Another build is already running for this database.') from exc
            lock.seek(0)
        else:
            import fcntl
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError as exc:
                raise ValueError('Another build is already running for this database.') from exc
        yield


def init_root(con, root):
    if not root.is_dir():
        raise ValueError(f'PDF root not found: {root}')
    stored = con.execute("SELECT value FROM settings WHERE key='root'").fetchone()
    if stored is not None and os.path.normcase(stored[0]) != os.path.normcase(str(root)):
        raise ValueError(f'This index belongs to {stored[0]}; use a different --db.')
    con.execute("INSERT OR IGNORE INTO settings VALUES ('root', ?)", (str(root),))
    con.commit()


def get_root(con):
    row = con.execute("SELECT value FROM settings WHERE key='root'").fetchone()
    if row is None:
        raise ValueError('Index root has not been set up. Run build first.')
    return Path(row[0])


def clear_pages(con, paper_id):
    start = paper_id * PAGE_STRIDE
    con.execute('DELETE FROM page_index WHERE rowid >= ? AND rowid < ?', (start, start + PAGE_STRIDE))
    con.execute('DELETE FROM ocr_attempts WHERE rowid >= ? AND rowid < ?', (start, start + PAGE_STRIDE))


def filename_hints(path):
    match = FILE_INFO.fullmatch(path.stem)
    if not match:
        return '', None, path.stem.replace('_', ' ')
    author, year, title = match.groups()
    return author.replace('_', ' '), int(year), title.replace('_', ' ')


def fail_walk(error):
    raise error


def inventory(con, root):
    existing = {r['relpath']: r for r in con.execute('SELECT id, relpath, size, mtime_ns, status FROM papers')}
    count = 0
    with con:
        for directory, folders, names in os.walk(root, onerror=fail_walk):
            folders.sort()
            for name in sorted(names):
                if not name.lower().endswith('.pdf'):
                    continue
                path = Path(directory) / name
                relpath = path.relative_to(root).as_posix()
                journal = relpath.split('/')[0] if '/' in relpath else '(root)'
                stat = path.stat()
                old = existing.pop(relpath, None)
                count += 1
                if old is None:
                    author, year, title = filename_hints(path)
                    paper_id = con.execute('''INSERT INTO papers
                        (relpath, journal, author_hint, year, title_hint, size, mtime_ns)
                        VALUES (?, ?, ?, ?, ?, ?, ?)''',
                        (relpath, journal, author, year, title, stat.st_size, stat.st_mtime_ns)).lastrowid
                    con.execute('INSERT INTO catalog(rowid, title, author) VALUES (?, ?, ?)', (paper_id, title, author))
                elif (old['size'], old['mtime_ns']) != (stat.st_size, stat.st_mtime_ns) or old['status'] == 'missing':
                    clear_pages(con, old['id'])
                    con.execute('''UPDATE papers SET size=?, mtime_ns=?, status='pending',
                        pages=NULL, text_pages=NULL, error=NULL WHERE id=?''', (stat.st_size, stat.st_mtime_ns, old['id']))
        if not count:
            raise ValueError('No PDFs found. Check the root before refreshing an existing index.')
        for old in existing.values():
            if old['status'] != 'missing':
                clear_pages(con, old['id'])
                con.execute("UPDATE papers SET status='missing', pages=NULL, text_pages=NULL, error=NULL WHERE id=?", (old['id'],))
    return count


def clean_text(raw):
    raw = unicodedata.normalize('NFKC', raw).replace('\xad', '').replace('\x00', '').replace('\r\n', '\n')
    raw = re.sub(r'(?<=[A-Za-z])-\n(?=[a-z])', '', raw)
    return re.sub(r'[^\S\n]+', ' ', raw).strip()


def pull_batch(root, batch):
    import pypdfium2 as pdfium

    results = []
    for paper_id, relpath, size, mtime in batch:
        path = Path(root) / relpath
        pages = []
        errors = []
        total = None
        try:
            with pdfium.PdfDocument(path) as pdf:
                total = len(pdf)
                if not 0 < total < PAGE_STRIDE:
                    raise ValueError(f'Invalid page count: {total}')
                for number in range(total):
                    try:
                        with closing(pdf[number]) as page, closing(page.get_textpage()) as textpage:
                            body = clean_text(textpage.get_text_bounded())
                        if body:
                            pages.append((number + 1, body))
                    except Exception as exc:
                        errors.append(f'p{number + 1}: {exc}')
            after = path.stat()
            if (after.st_size, after.st_mtime_ns) != (size, mtime):
                raise ValueError('File changed during indexing; run build again.')
            status = 'indexed' if len(pages) == total else 'partial' if pages else 'error' if errors else 'no_text'
        except Exception as exc:
            pages = []
            errors = [f'{type(exc).__name__}: {exc}']
            status = 'error'
        results.append((paper_id, status, total, pages, '; '.join(errors)[:1000] or None))
    return results


def save_batch(con, results):
    for paper_id, status, total, pages, error in results:
        clear_pages(con, paper_id)
        con.executemany('INSERT INTO page_index(rowid, paper_id, pdf_page, body) VALUES (?,?,?,?)',
                        ((paper_id * PAGE_STRIDE + page, paper_id, page, body) for page, body in pages))
        con.execute('UPDATE papers SET status=?, pages=?, text_pages=?, error=? WHERE id=?',
                    (status, total, len(pages), error, paper_id))


def queued_results(worker, root, tasks, workers, batch_size):
    batches = iter(tasks[i:i + batch_size] for i in range(0, len(tasks), batch_size))
    with futures.ProcessPoolExecutor(max_workers=workers) as pool:
        live = {pool.submit(worker, str(root), batch) for batch in
                (next(batches, None) for _ in range(workers * 2)) if batch is not None}
        while live:
            ready, live = futures.wait(live, return_when=futures.FIRST_COMPLETED)
            yield [task.result() for task in ready]
            for _ in ready:
                if (batch := next(batches, None)) is not None:
                    live.add(pool.submit(worker, str(root), batch))


def build(args):
    root = args.root.resolve()
    with build_lock(args.db.resolve()), connect(args.db, writable=True) as con:
        init_root(con, root)
        started = time.monotonic()
        print(f'Cataloged {inventory(con, root):,} PDFs from {root}', flush=True)
        requested = ('pending', 'error', 'partial', 'no_text') if args.retry else ('pending',)
        params = list(requested)
        query = f'''SELECT id, relpath, size, mtime_ns, journal FROM papers
                    WHERE status IN ({','.join('?' for _ in requested)})'''
        if args.journal:
            query += f" AND upper(journal) IN ({','.join('?' for _ in args.journal)})"
            params.extend(j.upper() for j in args.journal)
        rows = con.execute(query, params).fetchall()
        priority = {journal: rank for rank, journal in enumerate(JOURNAL_ORDER)}
        rows.sort(key=lambda row: (priority.get(row['journal'].upper(), len(priority)), row['relpath']))
        if args.limit:
            rows = rows[:args.limit]
        tasks = [tuple(row)[:4] for row in rows]
        print(f'Queued {len(tasks):,} PDFs; workers={args.workers}', flush=True)
        if not tasks:
            return
        done = 0
        text_pages = 0
        last_log = started
        for ready in queued_results(pull_batch, root, tasks, args.workers, 8):
            with con:
                for result in ready:
                    save_batch(con, result)
                    done += len(result)
                    text_pages += sum(len(pages) for _, _, _, pages, _ in result)
            now = time.monotonic()
            if now - last_log >= 12 or done == len(tasks):
                print(f'{done:,}/{len(tasks):,} checked; {text_pages:,} text pages; {now - started:.0f}s', flush=True)
                last_log = now
        print('Build pass finished. Run status and issues to check coverage.', flush=True)


def ocr_engine():
    deps = LOCAL_DATA / 'PaperlistResearch' / 'ocr-deps'
    if deps.is_dir() and str(deps) not in sys.path:
        sys.path.append(str(deps))
    try:
        from winrt.windows.media.ocr import OcrEngine
        from winrt.windows.globalization import Language
    except ImportError as exc:
        raise ValueError('OCR requires the Windows WinRT packages listed in the knowledge base guide.') from exc
    engine = OcrEngine.try_create_from_language(Language('en-US'))
    if engine is None:
        raise ValueError('The English (United States) Windows OCR language is not available.')
    return engine, OcrEngine.max_image_dimension


async def recognize_batch(root, batch):
    import pypdfium2 as pdfium
    engine, max_size = ocr_engine()
    from winrt.windows.graphics.imaging import BitmapAlphaMode, BitmapPixelFormat, SoftwareBitmap
    from winrt.windows.storage.streams import Buffer

    output = []
    for paper_id, relpath, size, mtime, numbers in batch:
        path = Path(root) / relpath
        results = []
        try:
            with pdfium.PdfDocument(path) as pdf:
                for number in numbers:
                    try:
                        with closing(pdf[number - 1]) as page:
                            scale = min(2.5, (max_size - 2) / max(page.get_size()))
                            with closing(page.render(scale=scale, grayscale=True)) as bitmap:
                                with bitmap.to_pil() as image:
                                    data = image.tobytes()
                                    width, height = image.size
                        buffer = Buffer(len(data))
                        buffer.length = len(data)
                        memoryview(buffer).cast('B')[:] = data
                        image = SoftwareBitmap.create_copy_from_buffer(buffer, BitmapPixelFormat.GRAY8,
                                                                        width, height, BitmapAlphaMode.IGNORE)
                        try:
                            recognized = await engine.recognize_async(image)
                            body = clean_text('\n'.join(line.text for line in recognized.lines))
                        finally:
                            image.close()
                        # Discard tiny noise from otherwise blank pages; this is not proof the page is blank.
                        if len(re.findall(r'[^\W\d_]{2,}', body)) < 4:
                            body = ''
                        results.append((number, body, None))
                    except Exception as exc:
                        results.append((number, '', f'{type(exc).__name__}: {exc}'[:500]))
            after = path.stat()
            if (after.st_size, after.st_mtime_ns) != (size, mtime):
                raise ValueError('File changed during OCR; run build again.')
        except Exception as exc:
            results = [(n, '', f'{type(exc).__name__}: {exc}'[:500]) for n in numbers]
        output.append((paper_id, results))
    return output


def ocr_batch(root, batch):
    return asyncio.run(recognize_batch(root, batch))


def ocr(args):
    ocr_engine()  # Fail before queueing work if OCR is unavailable.
    if not args.db.is_file():
        raise ValueError('Run build before OCR.')
    with build_lock(args.db.resolve()), connect(args.db, writable=True) as con:
        root = get_root(con)
        params = []
        query = "SELECT id, relpath, size, mtime_ns, pages FROM papers WHERE status IN ('no_text', 'partial')"
        if args.journal:
            query += f" AND upper(journal) IN ({','.join('?' for _ in args.journal)})"
            params.extend(j.upper() for j in args.journal)
        query += " ORDER BY (status='no_text') DESC, id"
        tasks = []
        for paper_id, relpath, size, mtime, pages in con.execute(query, params):
            start = paper_id * PAGE_STRIDE
            indexed = {row[0] - start for row in con.execute(
                'SELECT rowid FROM page_index WHERE rowid >= ? AND rowid < ?', (start, start + PAGE_STRIDE))}
            indexed.update(row[0] - start for row in con.execute(
                'SELECT rowid, result FROM ocr_attempts WHERE rowid >= ? AND rowid < ?',
                (start, start + PAGE_STRIDE)) if not args.retry or row[1] != 'error')
            numbers = [n for n in range(1, pages + 1) if n not in indexed]
            if numbers:
                tasks.append((paper_id, relpath, size, mtime, numbers))
                if args.limit and len(tasks) >= args.limit:
                    break
        total = sum(len(row[-1]) for row in tasks)
        print(f'Queued {total:,} pages from {len(tasks):,} PDFs for local English OCR; workers={args.workers}', flush=True)
        done = added = failures = 0
        since = last_log = time.monotonic()
        for ready in queued_results(ocr_batch, root, tasks, args.workers, 2):
            with con:
                for result in ready:
                    for paper_id, pages in result:
                        success = 0
                        for number, body, error in pages:
                            page_id = paper_id * PAGE_STRIDE + number
                            outcome = 'text' if body else 'error' if error else 'no_text'
                            con.execute('INSERT OR REPLACE INTO ocr_attempts(rowid, result, error) VALUES (?,?,?)',
                                        (page_id, outcome, error))
                            if body:
                                con.execute('INSERT INTO page_index(rowid, paper_id, pdf_page, body) VALUES (?,?,?,?)',
                                            (page_id, paper_id, number, body))
                                success += 1
                            failures += bool(error)
                        con.execute('''UPDATE papers SET text_pages=text_pages+?, status=CASE
                            WHEN text_pages+?=pages THEN 'indexed' WHEN text_pages+?>0 THEN 'partial'
                            ELSE 'no_text' END WHERE id=?''', (success, success, success, paper_id))
                        done += len(pages)
                        added += success
            now = time.monotonic()
            if now - last_log >= 12 or done == total:
                print(f'{done:,}/{total:,} OCR pages checked; {added:,} added; {failures:,} errors; {now - since:.0f}s', flush=True)
                last_log = now


def positive(raw):
    n = int(raw)
    if n < 1:
        raise argparse.ArgumentTypeError('must be positive')
    return n


def emit(rows):
    print(json.dumps(list(rows), ensure_ascii=False, indent=2))


def status(con, args):
    fields = ', '.join(f"SUM(status='{s}') AS {s}" for s in STATUSES)
    sql = f'''SELECT {{}} COUNT(*) AS total, {fields},
              COALESCE(SUM(pages),0) AS pdf_pages, COALESCE(SUM(text_pages),0) AS text_pages
              FROM papers {{}}'''
    overall = dict(con.execute(sql.format('', '')).fetchone())
    ocr_counts = {row[0]: row[1] for row in con.execute('SELECT result, COUNT(*) FROM ocr_attempts GROUP BY result')}
    print(json.dumps({'db': str(args.db.resolve()), 'root': str(get_root(con)), 'overall': overall,
                      'ocr': ocr_counts,
                      'journals': [dict(row) for row in con.execute(sql.format('journal,', 'GROUP BY journal ORDER BY journal'))]
                      if args.journals else None}, ensure_ascii=False, indent=2))


def add_filters(args, params):
    filters = ["p.status <> 'missing'"]
    if args.journal:
        filters.append(f"upper(p.journal) IN ({','.join('?' for _ in args.journal)})")
        params.extend(j.upper() for j in args.journal)
    if getattr(args, 'paper', None):
        filters.append('p.id=?')
        params.append(args.paper)
    for key, cmp in (('from_year', '>='), ('to_year', '<=')):
        value = getattr(args, key)
        if value is not None:
            filters.append(f'p.year {cmp} ?')
            params.append(value)
    return ' AND '.join(filters)


def match_expression(args):
    if args.fts:
        return args.query
    tokens = re.findall(r'[^\W_]+', unicodedata.normalize('NFKC', args.query))
    if not tokens:
        raise ValueError('Provide at least one search word.')
    if args.phrase:
        return '"' + ' '.join(tokens) + '"'
    return ' AND '.join('"' + word + '"' for word in tokens)


def search(con, args):
    params = [match_expression(args)]
    where = add_filters(args, params)
    root = get_root(con)
    info = 'p.id, p.journal, p.year, p.author_hint, p.title_hint, p.relpath'
    if args.cmd == 'catalog':
        rows = con.execute(f'''SELECT {info}, p.status FROM catalog
            JOIN papers p ON p.id=catalog.rowid WHERE catalog MATCH ? AND {where}
            ORDER BY rank, p.id LIMIT ?''', (*params, args.limit))
        emit(dict(row) | {'pdf': str(root / row['relpath'])} for row in rows)
        return
    rows = con.execute(f'''SELECT {info}, page_index.pdf_page,
            CASE WHEN ocr_attempts.result='text' THEN 'ocr' ELSE 'pdf_text' END AS source,
            snippet(page_index, 2, '«', '»', ' … ', 30) AS snippet
            FROM page_index JOIN papers p ON p.id=page_index.paper_id
            LEFT JOIN ocr_attempts ON ocr_attempts.rowid=page_index.rowid
            WHERE page_index MATCH ? AND {where} ORDER BY rank''', params)
    counts = {}
    checked = []
    for row in rows:
        if counts.get(row['id'], 0) >= args.per_paper:
            continue
        counts[row['id']] = counts.get(row['id'], 0) + 1
        checked.append(dict(row) | {'pdf': str(root / row['relpath'])})
        if len(checked) == args.limit:
            break
    emit(checked)


def issues(con, args):
    groups = args.status or ('partial', 'no_text', 'error', 'missing')
    placeholders = ','.join('?' for _ in groups)
    emit(dict(row) for row in con.execute(f'''SELECT id, journal, relpath, status, pages, text_pages, error
        FROM papers WHERE status IN ({placeholders}) ORDER BY journal, relpath LIMIT ?''', (*groups, args.limit)))


def page(con, args):
    paper = con.execute('SELECT relpath, status, pages FROM papers WHERE id=?', (args.id,)).fetchone()
    if paper is None:
        raise ValueError(f'Unknown paper ID: {args.id}')
    if paper['pages'] is not None and args.number > paper['pages']:
        raise ValueError(f"PDF has only {paper['pages']} pages.")
    hit = con.execute('''SELECT body, CASE WHEN ocr_attempts.result='text' THEN 'ocr' ELSE 'pdf_text' END AS source
        FROM page_index LEFT JOIN ocr_attempts ON ocr_attempts.rowid=page_index.rowid WHERE page_index.rowid=?''',
        (args.id * PAGE_STRIDE + args.number,)).fetchone()
    result = {'id': args.id, 'pdf': str(get_root(con) / paper['relpath']), 'pdf_page': args.number,
              'status': paper['status'], 'source': hit['source'] if hit else None, 'text': hit['body'] if hit else None}
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"{result['pdf']} | PDF page {args.number} | {paper['status']} | {result['source'] or 'no indexed text'}")
        print(result['text'] or '[No indexed text for this page. Open the original PDF.]')


def main():
    configure_output()
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--db', type=Path, default=DEFAULT_DB)
    commands = p.add_subparsers(dest='cmd', required=True)
    b = commands.add_parser('build', help='scan all PDF paths, then index new and changed files')
    b.add_argument('--root', type=Path, default=DEFAULT_ROOT)
    b.add_argument('--workers', type=positive, default=min(12, os.cpu_count() or 4))
    b.add_argument('--journal', action='append')
    b.add_argument('--limit', type=positive)
    b.add_argument('--retry', action='store_true', help='also reprocess partial, no_text and error files')
    o = commands.add_parser('ocr', help='reprocess pages without text with local Windows English OCR')
    o.add_argument('--workers', type=positive, default=min(8, os.cpu_count() or 4))
    o.add_argument('--journal', action='append')
    o.add_argument('--limit', type=positive)
    o.add_argument('--retry', action='store_true', help='also retry pages with OCR errors')
    s = commands.add_parser('status', help='inspect exact corpus coverage')
    s.add_argument('--journals', action='store_true')
    for name in ('catalog', 'search'):
        q = commands.add_parser(name, help='search title/author hints' if name == 'catalog' else 'search indexed PDF pages')
        q.add_argument('query', help='words are ANDed by default; --fts enables phrases, OR, NOT and prefixes')
        syntax = q.add_mutually_exclusive_group()
        syntax.add_argument('--fts', action='store_true')
        syntax.add_argument('--phrase', action='store_true')
        q.add_argument('--journal', action='append')
        q.add_argument('--from-year', type=int)
        q.add_argument('--to-year', type=int)
        q.add_argument('--limit', type=positive, default=12)
        if name == 'search':
            q.add_argument('--per-paper', type=positive, default=1)
            q.add_argument('--paper', type=positive)
    i = commands.add_parser('issues', help='show files with missing text or read errors')
    i.add_argument('--status', action='append', choices=STATUSES)
    i.add_argument('--limit', type=positive, default=20)
    x = commands.add_parser('page', help='retrieve searchable text and original PDF path for one physical PDF page')
    x.add_argument('id', type=positive)
    x.add_argument('number', type=positive)
    x.add_argument('--json', action='store_true')
    args = p.parse_args()
    if args.cmd in ('build', 'ocr') and args.workers > 61 and os.name == 'nt':
        p.error('--workers cannot exceed 61 on Windows')
    try:
        if args.cmd in ('build', 'ocr'):
            try:
                import pypdfium2
            except ImportError as exc:
                raise ValueError('Install pypdfium2 with python -m pip install pypdfium2.') from exc
            {'build': build, 'ocr': ocr}[args.cmd](args)
        else:
            with connect(args.db) as con:
                {'status': status, 'search': search, 'catalog': search, 'issues': issues, 'page': page}[args.cmd](con, args)
    except (ValueError, OSError, sqlite3.Error) as exc:
        print(f'paperlist: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    multiprocessing.freeze_support()
    raise SystemExit(main())
