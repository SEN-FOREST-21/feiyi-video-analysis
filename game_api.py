"""
时间错位 · 密码学版 API
=======================
时间线被撕开，四道封印各用一种古典密码锁住。每关先用时间逻辑推出密钥，
再用密钥解密——算错时间，密码就解不开。

    关卡1 · 位移的日志   算出日志被挪走的分钟数 → 凯撒位移
    关卡2 · 倒错的碎片   还原碎片先后 → 列换位重排文件块
    关卡3 · 循环的栅栏   算出循环次数 → 栅栏密码栏数
    关卡4 · 第一重时间锁 前三章明文拼成密钥 → 维吉尼亚解密
    关卡5 · 仿射的编号   模 26 求逆元 → 仿射解密
    关卡6 · 一次性时间线 五章明文首字母铸成密钥流 → 一次性密码本

闯关规则：逐章解锁，答对即进入下一章；作答次数不限，提示随时可看、不扣任何东西。
最末一章的密钥由前五章明文拼成，所以每一章都得吃透。
"""

import json
import os
import random
import re
import time
import uuid
from datetime import datetime
from flask import Flask, jsonify, request

app = Flask(__name__)

# ---------------------------------------------------------------------------
# 存储（内存 + 落盘）
# ---------------------------------------------------------------------------
STORE_PATH = os.environ.get(
    "GAME_STORE",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), ".game_sessions.json"),
)
SESSIONS: dict[str, dict] = {}


def _restore(raw: dict) -> dict:
    raw["puzzles"] = {int(k): v for k, v in raw.get("puzzles", {}).items()}
    raw["answers"] = {int(k): v for k, v in raw.get("answers", {}).items()}
    raw["hints"] = {int(k): v for k, v in raw.get("hints", {}).items()}
    raw.setdefault("mistakes", 0)
    for stale in ("score", "wrong_attempts", "lives"):
        raw.pop(stale, None)
    return raw


def _load_sessions() -> None:
    if not os.path.exists(STORE_PATH):
        return
    try:
        with open(STORE_PATH, encoding="utf-8") as f:
            SESSIONS.update({k: _restore(v) for k, v in json.load(f).items()})
    except Exception:
        pass


def _save_sessions() -> None:
    try:
        with open(STORE_PATH, "w", encoding="utf-8") as f:
            json.dump(SESSIONS, f, ensure_ascii=False)
    except Exception:
        pass


_load_sessions()


# ---------------------------------------------------------------------------
# 密码学工具
# ---------------------------------------------------------------------------
def caesar(text: str, shift: int) -> str:
    return "".join(
        chr((ord(c) - 65 + shift) % 26 + 65) if c.isalpha() else c
        for c in text.upper()
    )


def rail_pattern(length: int, rails: int) -> list[int]:
    """栅栏密码的轨道序列，例如 3 栏长度 7 → 0,1,2,1,0,1,2"""
    pattern, r, d = [], 0, 1
    for _ in range(length):
        pattern.append(r)
        if r == 0:
            d = 1
        elif r == rails - 1:
            d = -1
        r += d
    return pattern


def rail_encrypt(text: str, rails: int) -> str:
    rows = [[] for _ in range(rails)]
    for ch, r in zip(text, rail_pattern(len(text), rails)):
        rows[r].append(ch)
    return "".join("".join(row) for row in rows)


def rail_decrypt(cipher: str, rails: int) -> str:
    pattern = rail_pattern(len(cipher), rails)
    counts = [pattern.count(i) for i in range(rails)]
    rows, idx, pos = [], 0, [0] * rails
    for c in counts:
        rows.append(list(cipher[idx: idx + c]))
        idx += c
    out = []
    for r in pattern:
        out.append(rows[r][pos[r]])
        pos[r] += 1
    return "".join(out)


def vigenere_encrypt(text: str, key: str) -> str:
    out = []
    for i, c in enumerate(text.upper()):
        k = key[i % len(key)].upper()
        out.append(chr((ord(c) - 65 + ord(k) - 65) % 26 + 65))
    return "".join(out)


def affine_encrypt(text: str, a: int, b: int) -> str:
    return "".join(
        chr(((a * (ord(c) - 65) + b) % 26) + 65) if c.isalpha() else c
        for c in text.upper()
    )


def vigenere_decrypt(text: str, key: str) -> str:
    out = []
    for i, c in enumerate(text.upper()):
        k = key[i % len(key)].upper()
        out.append(chr((ord(c) - 65 - (ord(k) - 65)) % 26 + 65))
    return "".join(out)


# ---------------------------------------------------------------------------
# 关卡 1：位移的日志（凯撒）
# ---------------------------------------------------------------------------
LOG_CHAIN = [
    ("A", "主电源跳闸", 0),
    ("B", "备用电源启动", 2),
    ("C", "值班员抵达配电室", 8),
    ("D", "冷却系统重启", 5),
    ("E", "系统全面恢复", 12),
]
PLAIN_1 = ["ANCHOR", "VORTEX", "MIRROR", "ORACLE", "STATIC", "ECHOES", "CHIMES"]


def _fmt(minutes: int) -> str:
    minutes %= 24 * 60
    return f"{minutes // 60:02d}{minutes % 60:02d}"


def _generate_caesar_puzzle() -> dict:
    base = random.randint(0, 23) * 60 + random.choice([0, 15, 30, 45])

    true_times, cursor = [], base
    for _, _, gap in LOG_CHAIN:
        cursor += gap
        true_times.append(cursor % (24 * 60))

    idx = random.choice([1, 2, 3])
    gap_after = true_times[idx + 1] - true_times[idx]
    delta = gap_after + random.randint(1, 10)
    if delta > 24:
        delta = 24

    shown = list(true_times)
    shown[idx] = (shown[idx] + delta) % (24 * 60)
    while shown[idx] in [shown[i] for i in range(len(shown)) if i != idx]:
        shown[idx] = (shown[idx] + 1) % (24 * 60)

    plain = random.choice(PLAIN_1)
    cipher = caesar(plain, delta)
    letter = LOG_CHAIN[idx][0]

    return {
        "type": "caesar",
        "story": "地下实验室断电，应急日志被时间乱流撕开——一条记录的时间被向后挪了。墙上留着一串加密的字段。",
        "clues": [
            "备用电源在主电源跳闸后 2 分钟启动；",
            "值班员在备用电源启动后 8 分钟抵达配电室；",
            "冷却系统在值班员抵达后 5 分钟重启；",
            "系统在冷却系统重启后 12 分钟全面恢复。",
        ],
        "logs": [
            {"id": lid, "time": _fmt(shown[i]), "event": name}
            for i, (lid, name, _) in enumerate(LOG_CHAIN)
        ],
        "cipher": cipher,
        "cipher_note": "密文中的每个字母，都是明文字母向后移动 Δ 位得到的（A→B 记作 1 位）。",
        "question": "找出被挪位的那条日志，算出它被向后挪了多少分钟（Δ）。把密文向前推回 Δ 位，得到明文单词。",
        "answer": plain,
        "answer_hint": "先算链条：从 A 依次累加间隔，看哪条日志的时间对不上，差值就是 Δ。再用 Δ 做凯撒位移还原。",
    }


# ---------------------------------------------------------------------------
# 关卡 2：倒错的碎片（列换位）
# ---------------------------------------------------------------------------
FRAGMENTS = [
    "时间裂缝在机库中央张开",
    "观测仪的警报响彻整层",
    "值班员冲进控制室",
    "时间锚点被启动",
    "裂缝彻底闭合",
]
PLAIN_2 = ["RETROGRADE", "CHRONOLOGY", "TIMEPIECES"]


def _generate_transposition_puzzle() -> dict:
    letters = list("ABCDE")
    random.shuffle(letters)

    gaps = [random.randint(1, 4) for _ in range(len(FRAGMENTS) - 1)]
    hours, cur = [], random.randint(2, 10)
    hours.append(cur)
    for g in gaps:
        cur += g
        hours.append(cur)

    clues = [
        f"{letters[i]} 比 {letters[i + 1]} 早 {gaps[i]} 小时"
        for i in range(len(FRAGMENTS) - 1)
    ]
    extra = [(0, 2), (1, 3), (2, 4)]
    random.shuffle(extra)
    for i, j in extra[:2]:
        clues.append(f"{letters[i]} 比 {letters[j]} 早 {hours[j] - hours[i]} 小时")
    random.shuffle(clues)

    plain = random.choice(PLAIN_2)
    blocks = [plain[i: i + 2] for i in range(0, len(plain), 2)]
    # 第 k 块属于时间线第 k 个事件；密文按字母 A→E 书写
    cipher_blocks = ["??"] * 5
    for pos_in_time, letter in enumerate(letters):
        cipher_blocks[ord(letter) - 65] = blocks[pos_in_time]

    return {
        "type": "transposition",
        "story": "时间裂缝闭合时甩出五块碎片。档案员把明文切成了五块，按事件的时间顺序排好，却又按字母顺序抄了下来——于是块全乱了。",
        "fragments": [{"id": letters[i], "event": FRAGMENTS[i]} for i in range(5)],
        "clues": clues,
        "cipher_blocks": cipher_blocks,
        "cipher_note": "下列五块按字母 A→E 排列，每块 2 个字母，但它们并不是明文的真实块序。",
        "question": "先用线索排出五个事件的先后。第 1 块属于最早的事件，第 5 块属于最晚的事件——按这个顺序把块重新拼起来，写出 10 个字母的明文。",
        "answer": plain,
        "answer_hint": "线索是条链：找出比谁都早的那块，然后顺着“早 N 小时”一路往下接，得到 A-E 的时间顺序。再把密文块按这个顺序重排。",
    }


# ---------------------------------------------------------------------------
# 关卡 3：循环的栅栏（栅栏密码）
# ---------------------------------------------------------------------------
PLAIN_3 = ["GROUNDHOGDAY", "SAMEOLDSONG1", "DEJAVUALLDAY"]


def _generate_railfence_puzzle() -> dict:
    loops = random.randint(3, 5)
    start_no = random.randint(1, 40)
    now_no = start_no + loops - 1

    plain = "GROUNDHOGDAY"
    cipher = rail_encrypt(plain, loops)

    return {
        "type": "railfence",
        "story": "你被困在同一个 24 小时里。每循环一次，墙上的编号就加一；而密文每循环一次，就被重新排成一层栅栏。",
        "clues": [
            f"第一次循环时编号是 {start_no:02d}；",
            "每完整经历一次循环，编号加 1；",
            f"现在编号是 {now_no:02d}。",
        ],
        "cipher": cipher,
        "cipher_note": "密文是用 N 栏栅栏密码写下的：把明文沿 N 条轨道来回填，再逐行读出。",
        "question": "先算出你现在处于第几次循环（记为 N）。再用 N 栏栅栏密码还原密文，写出 12 个字母的明文。",
        "answer": plain,
        "answer_hint": "循环次数 = 当前编号 − 起始编号 + 1。栅栏还原：先按 N 条轨道的波形分配每行字母数，再逐字填回。",
    }


# ---------------------------------------------------------------------------
# 关卡 4：时间锁（维吉尼亚，密钥来自前三章明文）
# ---------------------------------------------------------------------------
PLAIN_4 = ["CIPHER", "UNLOCK", "REBOOT", "ESCAPE", "RETURN", "STATIC"]


def _generate_vigenere_puzzle(answers: list[str]) -> dict:
    key = answers[0][:2] + answers[1][:2] + answers[2][:2]
    plain = random.choice(PLAIN_4)
    cipher = vigenere_encrypt(plain, key)
    return {
        "type": "vigenere",
        "story": "三道封印解开，第一重时间锁浮现。它用你解出的三段明文当作钥匙。",
        "key_rule": "密钥 = 第一章明文前 2 字母 + 第二章明文前 2 字母 + 第三章明文前 2 字母（共 6 位）。",
        "cipher": cipher,
        "cipher_note": "维吉尼亚：明文字母序号 = 密文字母序号 − 密钥字母序号（A=0，B=1 … Z=25，结果按 26 取模）。",
        "question": "用你自己拼出的密钥解开第一重锁，写出 6 字母明文。",
        "answer": plain,
        "answer_hint": "密钥由你前三章的答案拼成。逐位相减，负数就加 26；0 对应 A，25 对应 Z。",
    }


# ---------------------------------------------------------------------------
# 关卡 5：仿射的编号（仿射密码）
# ---------------------------------------------------------------------------
PLAIN_5 = ["MIDNIGHT", "BLACKOUT", "ECLIPSES", "TIMEWARP"]
AFFINE_A, AFFINE_B = 7, 11


def _generate_affine_puzzle() -> dict:
    plain = random.choice(PLAIN_5)
    cipher = affine_encrypt(plain, AFFINE_A, AFFINE_B)
    return {
        "type": "affine",
        "story": "锁后是一条编号走廊，每个字母都被重新编了号——编号被拧了一下，拧的角度藏在那道公式里。",
        "formula": f"y = ({AFFINE_A}x + {AFFINE_B}) mod 26",
        "params": {"a": AFFINE_A, "b": AFFINE_B},
        "cipher": cipher,
        "cipher_note": "x 是明文字母的编号（A=0 … Z=25），y 是密文字母的编号。要解密就得反着来。",
        "question": "解开这条仿射密码，写出 8 字母明文。",
        "answer": plain,
        "answer_hint": f"先求 {AFFINE_A} 在模 26 下的逆元（乘起来 ≡ 1 mod 26），得到 {15}；再用 x = {15}(y − {AFFINE_B}) mod 26 逐位还原。",
    }


# ---------------------------------------------------------------------------
# 关卡 6：一次性时间线（一次性密码本）
# ---------------------------------------------------------------------------
PLAIN_6 = ["AFTERIMAGE", "TIMESTREAM", "PARALLAXES"]


def _generate_otp_puzzle(answers: list[str]) -> dict:
    key = "".join(a[0] for a in answers)
    plain = random.choice(PLAIN_6)
    cipher = vigenere_encrypt(plain, key)
    return {
        "type": "otp",
        "story": "最后一道门没有锁孔。它只认一把一次性密钥——钥匙就是你一路解出的五段明文的第一个字母。",
        "key_rule": "密钥流 = 前五章明文的第一个字母，依次拼接成 5 位，循环使用。",
        "cipher": cipher,
        "cipher_note": "一次性密码本：明文字母 = 密文字母 − 密钥字母（逐位，mod 26）。密钥只用一次，解密后即焚。",
        "question": "用你自己铸出的密钥解开最后一道门，写出 10 字母明文。",
        "answer": plain,
        "answer_hint": "把前五章答案的首字母按顺序连起来当密钥流，逐位相减，负数加 26。",
    }


# ---------------------------------------------------------------------------
# 关卡定义
# ---------------------------------------------------------------------------
LEVEL_NAMES = {
    1: "第一关 · 位移的日志",
    2: "第二关 · 倒错的碎片",
    3: "第三关 · 循环的栅栏",
    4: "第四关 · 第一重时间锁",
    5: "第五关 · 仿射的编号",
    6: "终极关 · 一次性时间线",
}
TOTAL_LEVELS = 6
FINAL_LEVEL = 6


def _new_session(player_name: str = "匿名特工") -> dict:
    pid = str(uuid.uuid4())[:8]
    return {
        "session_id": pid,
        "player": player_name,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "current_level": 1,
        "puzzles": {
            1: _generate_caesar_puzzle(),
            2: _generate_transposition_puzzle(),
            3: _generate_railfence_puzzle(),
            5: _generate_affine_puzzle(),
        },
        "answers": {},
        "hints": {},
        "final_puzzle": None,
        "solved": False,
        "mistakes": 0,
    }


def _normalize(s: str) -> str:
    return re.sub(r"[\s,，、。.:：;；!！?？\-—–_/|\\]", "", str(s)).upper()


def _public_session(s: dict) -> dict:
    return {
        "session_id": s["session_id"],
        "player": s["player"],
        "created_at": s["created_at"],
        "current_level": s["current_level"],
        "solved": s["solved"],
        "total_levels": TOTAL_LEVELS,
        "level_names": LEVEL_NAMES,
        "mistakes": s["mistakes"],
        "hints_used": sum(s["hints"].values()),
    }


# ---------------------------------------------------------------------------
# API
# ---------------------------------------------------------------------------
@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "service": "time-rift-crypto-api"})


@app.post("/api/game/create")
def create_game():
    player = (request.json or {}).get("player", "匿名特工")
    session = _new_session(player)
    SESSIONS[session["session_id"]] = session
    _save_sessions()
    return jsonify(_public_session(session))


@app.get("/api/game/<sid>")
def get_game(sid: str):
    s = SESSIONS.get(sid)
    if not s:
        return jsonify({"error": "会话不存在"}), 404
    return jsonify(_public_session(s))


@app.get("/api/game/<sid>/puzzle/<int:level>")
def get_puzzle(sid: str, level: int):
    s = SESSIONS.get(sid)
    if not s:
        return jsonify({"error": "会话不存在"}), 404
    if level < 1 or level > TOTAL_LEVELS:
        return jsonify({"error": f"关卡范围 1-{TOTAL_LEVELS}"}), 400
    if level > s["current_level"]:
        return jsonify({"error": f"请先通过第 {level - 1} 关"}), 403

    puzzle = s["final_puzzle"] if level == FINAL_LEVEL else s["puzzles"].get(level)
    if puzzle is None:
        return jsonify({"error": "该关尚未生成"}), 409
    safe = {k: v for k, v in puzzle.items() if k != "answer"}
    return jsonify({
        "level": level,
        "level_name": LEVEL_NAMES[level],
        "puzzle": safe,
    })


@app.post("/api/game/<sid>/hint")
def get_hint(sid: str):
    s = SESSIONS.get(sid)
    if not s:
        return jsonify({"error": "会话不存在"}), 404
    level = int((request.json or {}).get("level", s["current_level"]))
    puzzle = s["final_puzzle"] if level == FINAL_LEVEL else s["puzzles"].get(level)
    if not puzzle:
        return jsonify({"error": "该关不存在"}), 404
    s["hints"][level] = 1
    _save_sessions()
    return jsonify({"hint": puzzle["answer_hint"], "note": "随时可以再问。"})


@app.post("/api/game/<sid>/submit")
def submit_answer(sid: str):
    s = SESSIONS.get(sid)
    if not s:
        return jsonify({"error": "会话不存在"}), 404

    data = request.json or {}
    level = int(data.get("level", s["current_level"]))
    answer = str(data.get("answer", "")).strip()

    if level != s["current_level"]:
        return jsonify({"error": f"当前应提交第 {s['current_level']} 关答案"}), 400

    puzzle = s["final_puzzle"] if level == FINAL_LEVEL else s["puzzles"].get(level)
    if puzzle is None:
        return jsonify({"error": "该关尚未生成"}), 409
    s["answers"][level] = answer

    if _normalize(answer) == _normalize(puzzle["answer"]):
        if level == FINAL_LEVEL:
            s["solved"] = True
            _save_sessions()
            return jsonify({
                "ok": True,
                "message": "🎉 六道封印全部解开，时间线复原！",
                "session": _public_session(s),
            })
        s["current_level"] += 1
        if s["current_level"] == 4:
            s["puzzles"][4] = _generate_vigenere_puzzle([
                s["puzzles"][1]["answer"],
                s["puzzles"][2]["answer"],
                s["puzzles"][3]["answer"],
            ])
        if s["current_level"] == FINAL_LEVEL:
            s["final_puzzle"] = _generate_otp_puzzle(
                [s["puzzles"][i]["answer"] for i in (1, 2, 3, 4, 5)]
            )
        _save_sessions()
        return jsonify({
            "ok": True,
            "message": f"✅ 第 {level} 关通过！已解锁第 {s['current_level']} 关。",
            "session": _public_session(s),
        })

    s["mistakes"] += 1
    _save_sessions()
    return jsonify({
        "ok": False,
        "message": "❌ 还不对，再想想。卡住了可以找我要提示。",
        "session": _public_session(s),
    })


@app.post("/api/game/<sid>/restart")
def restart_game(sid: str):
    s = SESSIONS.get(sid)
    if not s:
        return jsonify({"error": "会话不存在"}), 404
    SESSIONS[sid] = _new_session(s["player"])
    _save_sessions()
    return jsonify(_public_session(SESSIONS[sid]))


@app.get("/api/game/<sid>/leaderboard")
def leaderboard(sid: str):
    board = [
        {
            "player": s["player"],
            "current_level": s["current_level"],
            "solved": s["solved"],
            "mistakes": s["mistakes"],
            "created_at": s["created_at"],
        }
        for s in SESSIONS.values()
    ]
    board.sort(key=lambda x: (-x["current_level"], not x["solved"], x["mistakes"]))
    return jsonify({"board": board[:50]})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
