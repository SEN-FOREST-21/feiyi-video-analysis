"""
时间错位解密游戏 API
====================
你是一名时间特工，时间线出现裂痕，历史事件的时间顺序被打乱。
穿越四个时间节点，解开谜题，修复时间线。

游戏流程:
    关卡1 → 破碎的时钟（读出时钟时间组成密码）
    关卡2 → 混乱的编年史（按时间排序历史事件）
    关卡3 → 时空坐标（根据时区线索计算目标时间）
    关卡4 → 终极时间锁（综合前三关答案解锁）
"""

import random
import uuid
import json
from datetime import datetime, timedelta, timezone
from flask import Flask, jsonify, request

app = Flask(__name__)

# ---------------------------------------------------------------------------
# 内存存储（简单 demo 用，生产环境请换 Redis / DB）
# ---------------------------------------------------------------------------
SESSIONS: dict[str, dict] = {}

# ---------------------------------------------------------------------------
# 关卡 1：破碎的时钟
# ---------------------------------------------------------------------------
def _generate_clock_puzzle() -> dict:
    """生成 3 个时钟，每个时钟显示一个两位数时间（时或分）。
    玩家需要读出每个时钟的数字，按顺序拼成 6 位密码。"""
    clocks = []
    answer_digits = ""
    for i in range(3):
        hour = random.randint(1, 12)
        minute = random.choice([0, 15, 30, 45])
        # 时钟指针角度（12 点方向为 0°，顺时针）
        hour_angle = (hour % 12) * 30 + minute * 0.5    # 时针
        minute_angle = minute * 6                         # 分针
        clocks.append({
            "label": f"时钟 #{i+1}",
            "hour_hand": round(hour_angle, 1),
            "minute_hand": round(minute_angle, 1),
            "hint": "分针指向刻度位置，时针指向大致方向",
        })
        # 密码取 2 位：小时 + 分钟的十位数（简化）
        answer_digits += f"{hour % 12 or 12:02d}"
    return {
        "type": "broken_clock",
        "story": "你找到了一台古老的时间机器，面板上三个时钟的指针在微微颤动……",
        "clocks": clocks,
        "question": "读出每个时钟对应的小时数（1-12），按顺序拼成一串数字作为密码。",
        "answer": answer_digits,
        "answer_hint": f"答案是一个 6 位数字（每个时钟 2 位，共 3 个时钟）",
    }


# ---------------------------------------------------------------------------
# 关卡 2：混乱的编年史
# ---------------------------------------------------------------------------
HISTORY_EVENTS_POOL = [
    {"event": "长城开始修建", "year": -221},
    {"event": "蔡伦改进造纸术", "year": 105},
    {"event": "哥仑布发现新大陆", "year": 1492},
    {"event": "达·伽马到达印度", "year": 1498},
    {"event": "麦哲伦完成环球航行", "year": 1522},
    {"event": "牛顿发表《自然哲学的数学原理》", "year": 1687},
    {"event": "第一次工业革命开始", "year": 1760},
    {"event": "美国独立宣言签署", "year": 1776},
    {"event": "法国大革命爆发", "year": 1789},
    {"event": "达尔文出版《物种起源》", "year": 1859},
    {"event": "爱迪生发明实用电灯", "year": 1879},
    {"event": "莱特兄弟首次动力飞行", "year": 1903},
    {"event": "第一次世界大战爆发", "year": 1914},
    {"event": "爱因斯坦提出相对论", "year": 1905},
    {"event": "阿波罗 11 号登月", "year": 1969},
    {"event": "互联网 TCP/IP 协议标准化", "year": 1983},
    {"event": "万维网向公众开放", "year": 1991},
    {"event": "Google 公司成立", "year": 1998},
    {"event": "iPhone 发布", "year": 2007},
    {"event": "新冠疫情全球大流行", "year": 2020},
]

def _generate_timeline_puzzle() -> dict:
    events = random.sample(HISTORY_EVENTS_POOL, 5)
    correct_order = sorted(events, key=lambda e: e["year"])
    shuffled = events[:]
    random.shuffle(shuffled)
    # 给打乱后的事件编号
    labeled = [{"id": chr(65 + i), "event": e["event"]} for i, e in enumerate(shuffled)]
    # 正确答案是字母序列
    id_to_year = {chr(65 + i): e["year"] for i, e in enumerate(shuffled)}
    correct_ids = sorted(id_to_year.keys(), key=lambda k: id_to_year[k])
    return {
        "type": "timeline",
        "story": "时间碎片四散飘落，你需要把它们按正确的先后顺序重新排列。",
        "events": labeled,
        "question": "按时间先后顺序排列下列事件，依次填入对应的字母（如 A,D,B,E,C）。",
        "answer": ",".join(correct_ids),
        "answer_hint": "答案格式：5 个字母用逗号分隔，最早的在前。",
    }


# ---------------------------------------------------------------------------
# 关卡 3：时空坐标
# ---------------------------------------------------------------------------
TIMEZONES = [
    {"name": "纽约", "offset": -5},
    {"name": "伦敦", "offset": 0},
    {"name": "巴黎", "offset": 1},
    {"name": "莫斯科", "offset": 3},
    {"name": "迪拜", "offset": 4},
    {"name": "东京", "offset": 9},
    {"name": "悉尼", "offset": 10},
    {"name": "洛杉矶", "offset": -8},
    {"name": "北京", "offset": 8},
]

def _generate_timezone_puzzle() -> dict:
    src = random.choice(TIMEZONES)
    dst = random.choice([t for t in TIMEZONES if t["name"] != src["name"]])
    hour = random.randint(0, 23)
    minute = random.choice([0, 15, 30, 45])
    src_str = f"{hour:02d}:{minute:02d}"
    # 计算目标时区时间
    offset_diff = dst["offset"] - src["offset"]
    total_minutes = hour * 60 + minute + offset_diff * 60
    total_minutes %= 24 * 60
    dst_h = total_minutes // 60
    dst_m = total_minutes % 60
    dst_str = f"{dst_h:02d}{dst_m:02d}"  # 答案是 4 位数字
    return {
        "type": "timezone",
        "story": "你需要跨越时区传送情报，但时空坐标需要精确到分钟……",
        "clues": [
            f"已知 {src['name']}（UTC{src['offset']:+d}）当前时间为 {src_str}",
            f"目标地点：{dst['name']}（UTC{dst['offset']:+d}）",
        ],
        "question": f"计算 {dst['name']} 当前时间，以 4 位数字格式输入（HHMM，24 小时制）。",
        "answer": dst_str,
        "answer_hint": f"先算出时差 {dst['offset'] - src['offset']:+d} 小时，再加减即可。",
    }


# ---------------------------------------------------------------------------
# 关卡 4：终极时间锁
# ---------------------------------------------------------------------------
def _generate_final_puzzle(level_answers: list[str]) -> dict:
    """综合前三关答案，生成终极谜题。简单起见，把三个答案拼起来取特定位数。"""
    combined = "".join(level_answers)
    # 从拼接串中每隔一个字符取一位
    final = combined[::2][:6]
    return {
        "type": "final_lock",
        "story": "三道谜题全部解开，最终的时间锁浮现在你眼前——三个答案的能量正在汇聚……",
        "clues": [
            f"关卡 1 答案：{level_answers[0]}",
            f"关卡 2 答案：{level_answers[1]}",
            f"关卡 3 答案：{level_answers[2]}",
        ],
        "question": "把三个答案拼接起来，然后从第 1 个字符开始，每隔一个字符取一位，组成 6 位密码。",
        "answer": final,
        "answer_hint": "拼接串 → 取索引 0,2,4,6,8,10 的字符 → 得到 6 位答案",
    }


# ---------------------------------------------------------------------------
# 关卡工厂
# ---------------------------------------------------------------------------
PUZZLE_GENERATORS = {
    1: _generate_clock_puzzle,
    2: _generate_timeline_puzzle,
    3: _generate_timezone_puzzle,
}

LEVEL_NAMES = {
    1: "第一关 · 破碎的时钟",
    2: "第二关 · 混乱的编年史",
    3: "第三关 · 时空坐标",
    4: "终极关 · 时间锁",
}

TOTAL_LEVELS = 4


# ---------------------------------------------------------------------------
# 辅助
# ---------------------------------------------------------------------------
def _new_session(player_name: str = "匿名特工") -> dict:
    pid = str(uuid.uuid4())[:8]
    puzzles = {i: PUZZLE_GENERATORS[i]() for i in range(1, 4)}
    return {
        "session_id": pid,
        "player": player_name,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "current_level": 1,
        "puzzles": puzzles,        # level -> puzzle dict（含 answer）
        "answers": {},             # level -> 玩家提交的答案
        "final_puzzle": None,      # 第 4 关
        "solved": False,
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
    # 返回时不要把 answer 字段泄露给客户端
    visible = _public_session(session)
    return jsonify(visible)


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
        return jsonify({"error": f"请先通过第 {level-1} 关"}), 403

    puzzle = s["final_puzzle"] if level == 4 else s["puzzles"][level]
    # 剔除 answer 后返回
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
    correct = str(puzzle["answer"]).strip()
    is_correct = _normalize(answer) == _normalize(correct)
    s["answers"][level] = answer

    if is_correct:
        if level == TOTAL_LEVELS:
            s["solved"] = True
            return jsonify({
                "ok": True,
                "message": "🎉 时间线修复完成！你是真正的时间特工！",
                "session": _public_session(s),
            })
        # 解锁下一关
        s["current_level"] += 1
        if s["current_level"] == 4:
            # 生成终极谜题
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
    else:
        return jsonify({
            "ok": False,
            "message": f"❌ 答案不对，再想想吧。",
            "hint": puzzle.get("hint"),
            "answer_hint": puzzle.get("answer_hint"),
        })


@app.post("/api/game/<sid>/restart")
def restart_game(sid: str):
    s = SESSIONS.get(sid)
    if not s:
        return jsonify({"error": "会话不存在"}), 404
    new_s = _new_session(s["player"])
    SESSIONS[sid] = new_s
    return jsonify(_public_session(new_s))


@app.get("/api/game/<sid>/leaderboard")
def leaderboard(sid: str):
    """列出所有会话的完成情况（简化版排行榜）。"""
    board = []
    for s in SESSIONS.values():
        board.append({
            "player": s["player"],
            "current_level": s["current_level"],
            "solved": s["solved"],
            "created_at": s["created_at"],
        })
    board.sort(key=lambda x: (-x["current_level"], x["created_at"]))
    return jsonify({"board": board[:50]})


# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------
def _normalize(s: str) -> str:
    """忽略空格、逗号、大小写的差异。"""
    return s.replace(" ", "").replace(",", "").upper()


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
# 入口
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
