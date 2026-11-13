"""
时间错位解密游戏 API
====================
时间线被撕开了裂缝，事件被挪到了错误的位置、顺序被打乱、同一天开始循环重演。
你是时间特工，要在三个事故现场把时间掰回原位，最后解开时间锁。

游戏流程:
    关卡1 → 错位的时间戳（找出被挪位的日志，算出它应有的时间）
    关卡2 → 倒错的时间线（排除乱流，把碎片按真实先后重排）
    关卡3 → 循环的同一天（判断自己困在第几次循环）
    关卡4 → 时间锁（综合前三关答案解锁）
"""

import random
import re
import uuid
from datetime import datetime
from flask import Flask, jsonify, request

app = Flask(__name__)

# ---------------------------------------------------------------------------
# 内存存储（demo 用；生产请换 Redis / DB）
# ---------------------------------------------------------------------------
SESSIONS: dict[str, dict] = {}


# ---------------------------------------------------------------------------
# 关卡 1：错位的时间戳
# ---------------------------------------------------------------------------
# (编号, 事件, 相对上一条事件的分钟数)
LOG_CHAIN = [
    ("A", "主电源跳闸", 0),
    ("B", "备用电源启动", 2),
    ("C", "值班员抵达配电室", 8),
    ("D", "冷却系统重启", 5),
    ("E", "系统全面恢复", 12),
]


def _fmt(minutes: int) -> str:
    minutes %= 24 * 60
    return f"{minutes // 60:02d}{minutes % 60:02d}"


def _generate_timestamp_puzzle() -> dict:
    """一条断电事故日志链，其中一条的时间被时间乱流挪走了。
    玩家要按给出的间隔重算，找出错位的那条及其正确时间。"""
    base_h, base_m = random.randint(0, 23), random.choice([0, 15, 30, 45])
    base = base_h * 60 + base_m

    # 真实时间
    true_times, cursor = [], base
    for _, _, gap in LOG_CHAIN:
        cursor += gap
        true_times.append(cursor % (24 * 60))

    # 只挪动 B/C/D 三条中间日志，偏移量必须大于它到下一条的间隔才能露出矛盾
    idx = random.choice([1, 2, 3])
    gap_after = true_times[idx + 1] - true_times[idx]
    delta = gap_after + random.randint(1, 10)

    shown = list(true_times)
    shown[idx] = (shown[idx] + delta) % (24 * 60)
    while shown[idx] in [shown[i] for i in range(len(shown)) if i != idx]:
        shown[idx] = (shown[idx] + 1) % (24 * 60)

    letter, name, _ = LOG_CHAIN[idx]
    return {
        "type": "displaced_timestamp",
        "story": "地下实验室在深夜断电，应急日志被时间乱流撕开——其中一条记录的时间被挪走了。",
        "clues": [
            "备用电源在主电源跳闸后 2 分钟启动；",
            "值班员在备用电源启动后 8 分钟抵达配电室；",
            "冷却系统在值班员抵达后 5 分钟重启；",
            "系统在冷却系统重启后 12 分钟全面恢复。",
        ],
        "logs": [
            {"id": lid, "time": _fmt(shown[i]), "event": name_}
            for i, (lid, name_, _) in enumerate(LOG_CHAIN)
        ],
        "question": "哪一条日志的时间被挪走了？给出它的编号和正确时间（HHMM），格式如 C2135。",
        "answer": letter + _fmt(true_times[idx]),
        "answer_hint": "从 A 的时间开始，按每条规则给出的分钟数依次往后加，得到一条完整时间链；再看哪一条日志的现场时间偏离了链条。",
    }


# ---------------------------------------------------------------------------
# 关卡 2：倒错的时间线
# ---------------------------------------------------------------------------
FRAGMENTS = [
    "时间裂缝在机库中央张开",
    "观测仪的警报响彻整层",
    "值班员冲进控制室",
    "时间锚点被启动",
    "裂缝彻底闭合",
]


def _generate_timeline_puzzle() -> dict:
    """五块时间碎片，时间戳全部丢失，只剩彼此的先后来往。
    玩家要按从早到晚排出字母顺序。"""
    # 真实顺序就是 FRAGMENTS 的叙事顺序，随机分配字母
    letters = list("ABCDE")
    random.shuffle(letters)

    # 相邻间隔（小时）
    gaps = [random.randint(1, 4) for _ in range(len(FRAGMENTS) - 1)]
    base_hour = random.randint(2, 10)
    hours, cur = [], base_hour
    hours.append(cur)
    for g in gaps:
        cur += g
        hours.append(cur)

    # 线索：相邻两条的间隔 + 两条跨位线索
    clues = [
        f"{letters[i]} 比 {letters[i + 1]} 早 {gaps[i]} 小时"
        for i in range(len(FRAGMENTS) - 1)
    ]
    extra_pairs = [(0, 2), (1, 3), (2, 4)]
    random.shuffle(extra_pairs)
    for i, j in extra_pairs[:2]:
        clues.append(f"{letters[i]} 比 {letters[j]} 早 {hours[j] - hours[i]} 小时")
    random.shuffle(clues)

    return {
        "type": "scrambled_timeline",
        "story": "时间裂缝闭合时留下了五块碎片，每块的时间戳都被抹掉了，只剩下它们彼此的先后关系。",
        "fragments": [
            {"id": letters[i], "event": FRAGMENTS[i]} for i in range(len(FRAGMENTS))
        ],
        "clues": clues,
        "question": "把五块碎片按时间从早到晚排列，填出字母序列（如 B,D,A,C,E）。",
        "answer": ",".join(letters),
        "answer_hint": "先找线索里只出现一次的“最早”那块，然后顺着间隔链条往下接。",
    }


# ---------------------------------------------------------------------------
# 关卡 3：循环的同一天
# ---------------------------------------------------------------------------
def _generate_loop_puzzle() -> dict:
    """你被困在同一天里反复循环，墙上的编号每轮 +1。
    玩家要根据起点编号和现在的编号算出轮次。"""
    start_no = random.randint(1, 40)
    loops = random.randint(4, 9)
    now_no = start_no + loops - 1

    return {
        "type": "time_loop",
        "story": "你被时间乱流困在了同一个 24 小时里。每天结束时你都会回到清晨，只有墙上那行字会变大一点。",
        "clues": [
            f"第一次循环时，你在墙上写下编号 {start_no:02d}；",
            "此后每完整经历一次循环，编号就加 1；",
            f"现在墙上写着编号 {now_no:02d}。",
        ],
        "question": "这是你的第几次循环？只填数字。",
        "answer": str(loops),
        "answer_hint": f"用现在的编号减去起点编号再加 1：{now_no} - {start_no} + 1。",
    }


# ---------------------------------------------------------------------------
# 关卡 4：时间锁
# ---------------------------------------------------------------------------
def _generate_final_puzzle(level_answers: list[str]) -> dict:
    """把三关答案拼起来，隔一个取一位，组成 6 位时间锁密码。"""
    combined = re.sub(r"[^A-Za-z0-9]", "", "".join(level_answers))
    picked = combined[::2]
    if len(picked) < 6:
        picked = (picked + combined[1::2])[:6]
    final = picked[:6]
    return {
        "type": "time_lock",
        "story": "三处错位都被你掰回了原位，时间锁浮现在裂缝中央，等待最后一道密码。",
        "clues": [
            f"第一关答案：{level_answers[0]}",
            f"第二关答案：{level_answers[1]}",
            f"第三关答案：{level_answers[2]}",
        ],
        "question": "把三个答案首尾相接，从第 1 个字符起每隔一个取一位，剩下的 6 位就是密码。",
        "answer": final,
        "answer_hint": "拼接 → 取第 1、3、5、7、9、11 个字符。",
    }


# ---------------------------------------------------------------------------
# 关卡工厂
# ---------------------------------------------------------------------------
PUZZLE_GENERATORS = {
    1: _generate_timestamp_puzzle,
    2: _generate_timeline_puzzle,
    3: _generate_loop_puzzle,
}

LEVEL_NAMES = {
    1: "第一关 · 错位的时间戳",
    2: "第二关 · 倒错的时间线",
    3: "第三关 · 循环的同一天",
    4: "终极关 · 时间锁",
}

TOTAL_LEVELS = 4


# ---------------------------------------------------------------------------
# 辅助
# ---------------------------------------------------------------------------
def _new_session(player_name: str = "匿名特工") -> dict:
    pid = str(uuid.uuid4())[:8]
    return {
        "session_id": pid,
        "player": player_name,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "current_level": 1,
        "puzzles": {i: PUZZLE_GENERATORS[i]() for i in range(1, 4)},
        "answers": {},
        "final_puzzle": None,
        "solved": False,
    }


def _normalize(s: str) -> str:
    """忽略空格、标点、大小写的差异。"""
    return re.sub(r"[\s,，、:：\-—/|]", "", str(s)).upper()


def _public_session(s: dict) -> dict:
    return {
        "session_id": s["session_id"],
        "player": s["player"],
        "created_at": s["created_at"],
        "current_level": s["current_level"],
        "solved": s["solved"],
        "total_levels": TOTAL_LEVELS,
        "level_names": LEVEL_NAMES,
    }


# ---------------------------------------------------------------------------
# API 路由
# ---------------------------------------------------------------------------
@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "service": "time-rift-game-api"})


@app.post("/api/game/create")
def create_game():
    player = (request.json or {}).get("player", "匿名特工")
    session = _new_session(player)
    SESSIONS[session["session_id"]] = session
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

    puzzle = s["final_puzzle"] if level == 4 else s["puzzles"][level]
    if puzzle is None:
        return jsonify({"error": "该关尚未生成"}), 409
    safe = {k: v for k, v in puzzle.items() if k != "answer"}
    return jsonify({"level": level, "level_name": LEVEL_NAMES[level], "puzzle": safe})


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

    puzzle = s["final_puzzle"] if level == 4 else s["puzzles"][level]
    s["answers"][level] = answer

    if _normalize(answer) == _normalize(puzzle["answer"]):
        if level == TOTAL_LEVELS:
            s["solved"] = True
            return jsonify({
                "ok": True,
                "message": "🎉 时间线修复完成！你是真正的时间特工！",
                "session": _public_session(s),
            })
        s["current_level"] += 1
        if s["current_level"] == 4:
            s["final_puzzle"] = _generate_final_puzzle([
                s["puzzles"][1]["answer"],
                s["puzzles"][2]["answer"],
                s["puzzles"][3]["answer"],
            ])
        return jsonify({
            "ok": True,
            "message": f"✅ 第 {level} 关通过！已解锁第 {s['current_level']} 关。",
            "session": _public_session(s),
        })

    return jsonify({
        "ok": False,
        "message": "❌ 答案不对，时间线还在抖。",
        "answer_hint": puzzle.get("answer_hint"),
    })


@app.post("/api/game/<sid>/restart")
def restart_game(sid: str):
    s = SESSIONS.get(sid)
    if not s:
        return jsonify({"error": "会话不存在"}), 404
    SESSIONS[sid] = _new_session(s["player"])
    return jsonify(_public_session(SESSIONS[sid]))


@app.get("/api/game/<sid>/leaderboard")
def leaderboard(sid: str):
    board = [
        {
            "player": s["player"],
            "current_level": s["current_level"],
            "solved": s["solved"],
            "created_at": s["created_at"],
        }
        for s in SESSIONS.values()
    ]
    board.sort(key=lambda x: (-x["current_level"], x["created_at"]))
    return jsonify({"board": board[:50]})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
