import re
import sqlite3
from datetime import datetime
from pathlib import Path

DAY_HEADER_RE = re.compile(r'^\s*(Понеделник|Вторник|Сряда|Четвъртък|Петък|Събота|Неделя)\s*/\s*(\d{2}\.\d{2}\.\d{4})\s*$')
TEACHER_PAT = r'(?:[A-Za-zА-Яа-я]+)\s+[A-Za-zА-Яа-я]\.\s+(?:[A-Za-zА-Яа-я]+(?:-[A-Za-zА-Яа-я]+)?)'
LESSON_RE = re.compile(
    rf'^\s*(?P<num>\d+)\.\s+'
    rf'(?P<class_name>.+?)\s+'
    rf'(?P<teacher>{TEACHER_PAT})\s+'
    rf'(?P<room>\d+)\s+'
    rf'(?P<start>\d{{2}}:\d{{2}})\s*-\s*(?P<end>\d{{2}}:\d{{2}})\s*$'
)

def _parse_date_bg(dmy: str) -> str:
    return datetime.strptime(dmy, "%d.%m.%Y").strftime("%Y-%m-%d")

def _norm_subject(s: str) -> str:
    s = re.sub(r'\s*-\s*', ' - ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    s = s.lstrip('-–— ').strip()
    return s

def parse_schedule(text: str):
    days = []
    current = None
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        mday = DAY_HEADER_RE.match(line)
        if mday:
            if current:
                days.append(current)
            _, dmy = mday.groups()
            current = {"date": _parse_date_bg(dmy), "entries": []}
            continue
        if current:
            mles = LESSON_RE.match(line)
            if mles:
                g = mles.groupdict()
                current["entries"].append({
                    "class_number": int(g["num"]),
                    "class_name": _norm_subject(g["class_name"]),
                    "teacher": re.sub(r'\s+', ' ', g["teacher"]).strip(),
                    "room": g["room"].strip(),
                    "time": f'{g["start"]} - {g["end"]}',
                })
            else:
                tm = list(re.finditer(TEACHER_PAT, line))
                if tm:
                    t = tm[-1]
                    left = line[:t.start()].strip()
                    right = line[t.start():].strip()
                    num_m = re.match(r'^\s*(\d+)\.\s+(.*)$', left)
                    tail_m = re.match(rf'^({TEACHER_PAT})\s+(\d+)\s+(\d{{2}}:\d{{2}})\s*-\s*(\d{{2}}:\d{{2}})\s*$', right)
                    if num_m and tail_m:
                        class_number = int(num_m.group(1))
                        class_name = _norm_subject(num_m.group(2))
                        teacher, room, start, end = tail_m.groups()
                        current["entries"].append({
                            "class_number": class_number,
                            "class_name": class_name,
                            "teacher": re.sub(r'\s+', ' ', teacher).strip(),
                            "room": room.strip(),
                            "time": f"{start} - {end}",
                        })
    if current:
        days.append(current)
    return days

def _ensure_schema(conn: sqlite3.Connection):
    conn.executescript("""
    PRAGMA foreign_keys = ON;
    CREATE TABLE IF NOT EXISTS classes (
      class_id   INTEGER PRIMARY KEY,
      class_name TEXT UNIQUE
    );
    INSERT OR IGNORE INTO classes(class_id, class_name) VALUES(0, '—');
    CREATE TABLE IF NOT EXISTS schedule (
      date          TEXT NOT NULL,
      class_number  INTEGER NOT NULL,
      class_name    TEXT,
      time          TEXT NOT NULL,
      teacher       TEXT,
      room          TEXT,
      class_id      INTEGER NOT NULL DEFAULT 0,
      PRIMARY KEY (date, class_number),
      FOREIGN KEY (class_id) REFERENCES classes(class_id) ON DELETE SET DEFAULT
    );
    """)
    
def _class_id(conn: sqlite3.Connection, class_name: str) -> int:
    if not class_name or class_name.strip() == "":
        return 0
    cur = conn.cursor()
    cur.execute("SELECT class_id FROM classes WHERE class_name = ?", (class_name,))
    row = cur.fetchone()
    if row:
        return row[0]
    cur.execute("SELECT COALESCE(MAX(class_id), 0) FROM classes WHERE class_id >= 1")
    max_id = cur.fetchone()[0] or 0
    new_id = max_id + 1
    cur.execute("INSERT INTO classes(class_id, class_name) VALUES(?,?)", (new_id, class_name))
    return new_id

def _upsert_day(conn: sqlite3.Connection, date_iso: str, entries: list):
    cur = conn.cursor()
    for e in entries:
        cid = _class_id(conn, e["class_name"])
        cur.execute(
            """
            INSERT INTO schedule(date, class_number, class_name, time, teacher, room, class_id)
            VALUES(?,?,?,?,?,?,?)
            ON CONFLICT(date, class_number) DO UPDATE SET
              class_name = excluded.class_name,
              time       = excluded.time,
              teacher    = excluded.teacher,
              room       = excluded.room,
              class_id   = excluded.class_id
            """,
            (date_iso, e["class_number"], e["class_name"], e["time"], e["teacher"], e["room"], cid)
        )

def import_schedule():
    text = Path("output.txt").read_text(encoding="utf-8")
    days = parse_schedule(text)
    conn = sqlite3.connect("schedule.sqlite")
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        _ensure_schema(conn)
        for d in days:
            _upsert_day(conn, d["date"], d["entries"])
        conn.commit()
    finally:
        conn.close()
    return {"days": len(days), "entries": sum(len(d["entries"]) for d in days)}
