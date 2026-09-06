# -*- coding: utf-8 -*-
"""PLANET GENESIS QQ/PB｜作者：剩菜｜v1.4.8｜竞速榜计时修复+致谢前辈｜无随机/无概率"""
import ast
import base64
import difflib
import gzip
import json
import math
import re
import time
import zlib

APP_NAME, APP_VERSION = "PLANET GENESIS QQ/PB", "1.4.8"
STATE_SCHEMA, GLOBAL_SCHEMA, SAVE_PREFIX = 4, 2, "json:"
MAX_SAVE, MAX_DECOMP, MAX_PROTOCOL, MAX_CMD, MAX_GLOBAL_USERS, MAX_BUILD, MAX_NUM = 8 * 1024 * 1024, 8 * 1024 * 1024, 20 * 1024 * 1024, 4096, 5000, 1000, 1e300
BASE_OFFLINE, OFFLINE_PER_TECH, MAX_OFFLINE = 8, 4, 72

RM = {"energy": ("☀️", "恒星能"), "mineral": ("🪨", "矿物"), "water": ("💧", "水"), "air": ("🌫️", "大气"), "biomass": ("🌱", "生物量"), "civilization": ("🏙️", "文明")}
RSRC_HINT = {"energy": "##planet tap 1 或 ##planet build 日照阵列", "mineral": "##planet build 地壳钻机", "water": "##planet build 融冰塔", "air": "##planet build 大气工厂", "biomass": "##planet build 生态穹顶", "civilization": "##planet build 城市节点"}

B = {
    "solar": {"name": "日照阵列", "icon": "☀️", "slots": 1, "bc": {"energy": 10}, "scale": 1.17, "rate": {"energy": 1}, "desc": "收集恒星辐射。每座 +1 恒星能/秒。"},
    "mine": {"name": "地壳钻机", "icon": "⛏️", "slots": 2, "bc": {"energy": 60}, "scale": 1.18, "rate": {"mineral": 0.35}, "desc": "开采地壳。每座 +0.35 矿物/秒。"},
    "melt": {"name": "融冰塔", "icon": "🧊", "slots": 3, "bc": {"energy": 150, "mineral": 25}, "scale": 1.19, "rate": {"water": 0.12}, "desc": "融化极地与地下冰。每座 +0.12 水/秒。"},
    "atmo": {"name": "大气工厂", "icon": "🌫️", "slots": 4, "bc": {"mineral": 80, "water": 40}, "scale": 1.20, "rate": {"air": 0.05}, "desc": "制造并稳定行星大气。每座 +0.05 大气/秒。"},
    "bio": {"name": "生态穹顶", "icon": "🌿", "slots": 6, "bc": {"water": 80, "air": 60}, "scale": 1.21, "rate": {"biomass": 0.018}, "desc": "让生命进入稳定循环。每座 +0.018 生物量/秒。"},
    "city": {"name": "城市节点", "icon": "🏙️", "slots": 8, "bc": {"energy": 100, "biomass": 80}, "scale": 1.22, "rate": {"civilization": 0.004}, "desc": "把生态转化为文明。每座 +0.004 文明/秒。"},
    "ring": {"name": "轨道环", "icon": "🛰️", "slots": 12, "bc": {"mineral": 200, "air": 150, "civilization": 50}, "scale": 1.23, "rate": {}, "desc": "每座使全部被动产出 ×1.12。"},
    "transmission": {"name": "快速传动装置", "icon": "⚙️", "slots": 2, "bc": {"mineral": 50, "energy": 30}, "scale": 1.25, "rate": {}, "desc": "每座使手摇加速 +0.2分钟（12秒），冷却 -0.15秒（最低3秒）。"},
}
BA = {"solar": "solar", "日照阵列": "solar", "日照": "solar", "太阳能": "solar", "mine": "mine", "地壳钻机": "mine", "钻机": "mine", "矿机": "mine", "melt": "melt", "融冰塔": "melt", "融冰": "melt", "冰塔": "melt", "atmo": "atmo", "大气工厂": "atmo", "大气": "atmo", "bio": "bio", "生态穹顶": "bio", "生态": "bio", "穹顶": "bio", "city": "city", "城市节点": "city", "城市": "city", "ring": "ring", "轨道环": "ring", "环": "ring", "中继环": "ring", "transmission": "transmission", "快速传动装置": "transmission", "传动": "transmission", "传动装置": "transmission", "变速": "transmission"}

OM = {"star": ("恒星轨道", "恒星能 ×2.00"), "geology": ("地质轨道", "矿物 ×2.00"), "ocean": ("海洋轨道", "水 ×2.00"), "climate": ("气候轨道", "大气 ×2.00"), "biosphere": ("生态轨道", "生物量 ×2.00"), "city": ("文明轨道", "文明 ×2.00"), "balance": ("平衡轨道", "全部资源 ×1.18")}
OA = {"star": "star", "恒星": "star", "恒星轨道": "star", "能量": "star", "geology": "geology", "地质": "geology", "矿物": "geology", "ocean": "ocean", "海洋": "ocean", "水": "ocean", "climate": "climate", "气候": "climate", "大气": "climate", "biosphere": "biosphere", "生态": "biosphere", "生物": "biosphere", "city": "city", "文明": "city", "balance": "balance", "平衡": "balance", "均衡": "balance"}

T = {
    "fusion": {"name": "恒星聚变", "max": 20, "desc": "每级使全部产出 ×1.20。"},
    "automation": {"name": "建造自动化", "max": 10, "desc": "每级使建筑价格 ×0.95。"},
    "cryosleep": {"name": "深空休眠", "max": 16, "desc": "每级使离线结算上限 +4小时，最高72小时。"},
    "tectonics": {"name": "板块工程", "max": 10, "desc": "每级永久增加 6 地表槽位。"},
    "archive": {"name": "文明档案", "max": 10, "desc": "每级使新行星开局额外获得 50 恒星能。"},
}
TA = {"fusion": "fusion", "恒星聚变": "fusion", "聚变": "fusion", "automation": "automation", "建造自动化": "automation", "自动化": "automation", "cryosleep": "cryosleep", "深空休眠": "cryosleep", "休眠": "cryosleep", "离线": "cryosleep", "tectonics": "tectonics", "板块工程": "tectonics", "板块": "tectonics", "槽位": "tectonics", "archive": "archive", "文明档案": "archive", "档案": "archive", "开局": "archive"}

PS = (("裸岩星", "🪨", None, 0, "一颗只有岩石与恒星照明的荒芜行星。"), ("觉醒地核", "🌋", "mineral", 100, "稳定采矿开始，地壳不再只是背景。"), ("原始海洋", "🌊", "water", 100, "液态水形成持续循环，星球第一次有了海。"), ("稠密大气", "🌫️", "air", 100, "大气层稳定下来，天空真正出现。"), ("生命摇篮", "🌱", "biomass", 100, "生命不再依赖单个穹顶，生态开始自我延续。"), ("城市行星", "🌍", "civilization", 100, "文明网络覆盖地表，夜面开始发光。"), ("星际母星", "🪐", "civilization", 1000, "文明拥有离开母星的能力，可以执行星际启航。"))
RA = {"energy": "energy", "恒星能": "energy", "能量": "energy", "光": "energy", "mineral": "mineral", "矿物": "mineral", "矿": "mineral", "water": "water", "水": "water", "air": "air", "大气": "air", "空气": "air", "biomass": "biomass", "生物量": "biomass", "生物": "biomass", "civilization": "civilization", "文明": "civilization", "城市": "civilization"}

SR = {
    "thermocrystal": {"name": "热电晶格", "pair": ("energy", "mineral"), "min_stage": 1, "cost": {"energy": 220, "mineral": 55}, "effect": "恒星能被动产出 ×1.15", "boost": ("energy", 1.15), "clue": "高温恒星能照射某种地壳矿物时，会出现规则晶格。"},
    "aquaceramic": {"name": "导流陶瓷", "pair": ("mineral", "water"), "min_stage": 2, "cost": {"mineral": 75, "water": 45}, "effect": "水被动产出 ×1.15", "boost": ("water", 1.15), "clue": "海盆边缘的湿润矿层，似乎能烧结成一种会主动引水的材料。"},
    "cloudgel": {"name": "云核凝胶", "pair": ("water", "air"), "min_stage": 3, "cost": {"water": 65, "air": 45}, "effect": "大气被动产出 ×1.15", "boost": ("air", 1.15), "clue": "水滴悬浮在新生大气里时，扫描器检测到稳定的凝结核心。"},
    "nitromembrane": {"name": "固氮膜", "pair": ("air", "biomass"), "min_stage": 4, "cost": {"air": 60, "biomass": 40}, "effect": "生物量被动产出 ×1.15", "boost": ("biomass", 1.15), "clue": "某些生物膜正在从大气里固定成分；也许可以人工复制。"},
    "biosilicon": {"name": "生物硅网络", "pair": ("biomass", "civilization"), "min_stage": 5, "cost": {"biomass": 55, "civilization": 28}, "effect": "文明被动产出 ×1.15", "boost": ("civilization", 1.15), "clue": "城市信号穿过活体组织时，出现了比普通线路更稳定的反馈。"},
    "orbitalcomposite": {"name": "轨道复材", "pair": ("mineral", "civilization"), "min_stage": 5, "cost": {"mineral": 140, "civilization": 55}, "effect": "全部被动产出 ×1.08", "boost": ("all", 1.08), "clue": "轨道工程报告反复提到：成熟文明的结构设计与高纯矿物之间还有一种组合。"},
}

SC = (
    {"name": "长夜供能", "story": "裸岩星的夜面太长，第一批设备频繁停机。", "goal": "把恒星能被动产出提高到 2.50/s。", "reward": {"energy": 50}},
    {"name": "地壳过热", "story": "钻探层温度升高，地质设备需要更稳定的供能余量。", "goal": "矿物产出达到 0.75/s，并持有至少80恒星能。", "reward": {"mineral": 30}},
    {"name": "海盆亏水", "story": "第一片海盆蒸发得比预期快，水循环必须先站稳。", "goal": "水产出达到 0.25/s，并持有至少40水。", "reward": {"water": 30}},
    {"name": "大气逃逸", "story": "轻薄大气正不断逃逸，必须提高补充速度。", "goal": "大气产出达到 0.10/s，并持有至少30大气。", "reward": {"air": 25}},
    {"name": "生态失衡", "story": "生态穹顶出现物种比例失衡，需要更高的生物量缓冲。", "goal": "生物量产出达到 0.030/s，并持有至少25生物量。", "reward": {"biomass": 20}},
    {"name": "城市峰值", "story": "夜面城市同时进入高负载，文明网络出现短时拥塞。", "goal": "文明产出达到 0.008/s，同时恒星能产出达到3.00/s。", "reward": {"civilization": 15}},
    {"name": "母星窗口", "story": "星际发射窗口很短，轨道工业必须先证明自己。", "goal": "拥有至少1座轨道环，并把文明产出提高到0.015/s。", "reward": {"civilization": 25}},
)

SET = (
    "☀️【行星事件｜第一束晨光】恒星越过没有名字的地平线。岩层第一次留下清晰的明暗边界，漫长的夜仍伏在另一面。",
    "🌋【行星事件｜地核回声】深处传来迟缓而沉重的震动，像一颗尚未学会呼吸的心。裂隙里有微红的光，短暂照亮钻孔。",
    "🌊【行星事件｜第一片海】水沿最低的地方汇聚，起初只是薄薄一层。数个昼夜之后，地平线第一次被另一种颜色截断。",
    "🌫️【行星事件｜天空诞生】晨昏线不再锋利。光在高处散开，遥远山脊被一层淡色吞没——这颗星球终于有了天空。",
    "🌱【行星事件｜绿色边界】穹顶外侧出现一小片无人栽种的绿色。它贴着岩缝生长，风经过时，叶面轻轻翻了一次。",
    "🌍【行星事件｜夜面灯火】黑暗的一侧开始出现细碎光点。它们沿海岸、河谷与旧矿带相连，像另一幅缓慢形成的星图。",
    "🪐【行星事件｜远方坐标】轨道之外出现了一组稳定坐标。没有声音从那里传来，只有漫长距离本身，安静地等待被跨越。",
)

SE = {
    "double_shadow": {"name": "双影凌日", "clue_recipe": "thermocrystal", "reward": {"energy": 80}, "text": "两道阵列阴影在正午短暂重合。阴影退去后，浅层矿脉仍残留一线温差，像岩石记住了刚才的光。"},
    "black_beach": {"name": "黑色沙滩", "clue_recipe": "aquaceramic", "reward": {"water": 20}, "text": "新海岸留下了一条黑色细线。潮水退去时，某些矿砂仍挂着薄薄水膜，比周围更晚干去。"},
    "charged_cloud": {"name": "云海放电", "clue_recipe": "cloudgel", "reward": {"air": 18}, "text": "云层深处闪过一次没有雷声的白光。很久以后，那片天空仍比别处更容易聚起细小水滴。"},
    "green_frontier": {"name": "绿色边界", "clue_recipe": "nitromembrane", "reward": {"biomass": 12}, "text": "穹顶外缘的岩面蒙上一层极薄的绿色。清晨时，它周围的雾总比别处早一些散开。"},
    "night_sync": {"name": "夜面同步", "clue_recipe": "biosilicon", "reward": {"civilization": 10}, "text": "夜面灯火在某一秒几乎同时暗下，又同时亮起。城市边缘的一片生物组织，留下了同样整齐的微弱脉冲。"},
    "ring_eclipse": {"name": "环影日蚀", "clue_recipe": "orbitalcomposite", "reward": {"civilization": 12}, "text": "轨道环的影子缓慢掠过大陆。日蚀结束后，一段承力构件仍保持着近乎不自然的平直，像从未承受过重量。"},
}

MILESTONES = [
    {"id": "launch_1", "name": "🚀 启航新手", "reward": {"global_prod": 0.02}, "desc": "累计启航 1 次"},
    {"id": "launch_5", "name": "🚀 启航老手", "reward": {"global_prod": 0.05}, "desc": "累计启航 5 次"},
    {"id": "launch_10", "name": "🚀 启航大师", "reward": {"global_prod": 0.10}, "desc": "累计启航 10 次"},
    {"id": "civ_10k", "name": "🏛️ 文明先驱", "reward": {"cores": 1}, "desc": "历史文明总产出 ≥ 1万"},
    {"id": "civ_100k", "name": "🏛️ 文明领袖", "reward": {"cores": 3}, "desc": "历史文明总产出 ≥ 10万"},
    {"id": "civ_1m", "name": "🏛️ 文明传奇", "reward": {"cores": 5}, "desc": "历史文明总产出 ≥ 100万"},
    {"id": "crank_100", "name": "🔄 手摇达人", "reward": {"crank_cooldown": -0.5}, "desc": "累计手摇 100 次"},
    {"id": "crank_1000", "name": "🔄 手摇狂人", "reward": {"crank_cooldown": -1.0}, "desc": "累计手摇 1000 次"},
]

AURAS = [
    {"id": "geo", "name": "🌍 地核光环", "cost": 3, "effect": {"mineral": 1.5}, "desc": "矿物产出 ×1.5"},
    {"id": "ocean", "name": "🌊 海洋光环", "cost": 3, "effect": {"water": 1.5}, "desc": "水产出 ×1.5"},
    {"id": "atmo", "name": "🌤️ 大气光环", "cost": 3, "effect": {"air": 1.5}, "desc": "大气产出 ×1.5"},
    {"id": "bio", "name": "🌿 生命光环", "cost": 5, "effect": {"biomass": 1.5}, "desc": "生物量产出 ×1.5"},
    {"id": "civ", "name": "🏙️ 文明光环", "cost": 5, "effect": {"civilization": 1.5}, "desc": "文明产出 ×1.5"},
    {"id": "star", "name": "⭐ 恒星光环", "cost": 10, "effect": {"all": 1.3}, "desc": "全部产出 ×1.3"},
]

def _now(fn=None):
    try:
        v = float((fn if fn else time.time)())
    except:
        v = time.time()
    return v if (math.isfinite(v) and v >= 0) else time.time()

def cl(v, d=0):
    try:
        v = float(v)
    except:
        v = float(d)
    return max(0, min(v, MAX_NUM)) if math.isfinite(v) else float(d)

def si(v, d=0, lo=None, hi=None):
    try:
        v = int(v)
    except:
        v = int(d)
    if lo is not None:
        v = max(lo, v)
    if hi is not None:
        v = min(hi, v)
    return v

def st(v, d="", mx=100):
    return str(v).strip()[:mx] if v is not None else d

def fm(v):
    v = cl(v)
    if v < 1000:
        if abs(v - round(v)) < 1e-9:
            return f"{int(round(v)):,}"
        if v >= 100:
            return f"{v:,.1f}"
        if v >= 10:
            return f"{v:,.2f}"
        return f"{v:,.3f}"
    for t, s in [(1e30, "Qn"), (1e27, "Oc"), (1e24, "Sp"), (1e21, "Sx"), (1e18, "Qi"), (1e15, "Qa"), (1e12, "T"), (1e9, "B"), (1e6, "M"), (1e3, "K")]:
        if v >= t:
            return f"{v/t:.3f}{s}"
    return f"{v:,.0f}"

def fs(s):
    s = max(0, int(s))
    h, r = divmod(s, 3600)
    m, s = divmod(r, 60)
    if h:
        return f"{h}小时{m}分"
    if m:
        return f"{m}分{s}秒"
    return f"{s}秒"

def rt(c):
    return " + ".join([f"{fm(a)}{RM[k][0]}{RM[k][1]}" for k, a in c.items() if a]) or "0"

def _b64_encode(data):
    return base64.b64encode(data).decode('ascii')

def _b64_decode(text):
    try:
        return base64.b64decode(text.encode('ascii'))
    except:
        return None

def gzip_text(text):
    data = text.encode('utf-8')
    cdata = gzip.compress(data, compresslevel=6)
    return _b64_encode(cdata)

def ungzip_text(btext):
    cdata = _b64_decode(btext)
    if cdata is None:
        raise ValueError("Base64解码失败")
    data = gzip.decompress(cdata)
    return data.decode('utf-8')

def enc(v):
    return json.dumps(v, ensure_ascii=False, separators=(",", ":"))

def dec(v):
    if not isinstance(v, str):
        raise ValueError("save must be text")
    if v.startswith("gz:"):
        try:
            encoded = v[3:]
            compressed = base64.b64decode(encoded.encode("ascii"), validate=True)
            inflater = zlib.decompressobj(16 + zlib.MAX_WBITS)
            raw = inflater.decompress(compressed, MAX_DECOMP + 1)
            raw += inflater.flush()
            loaded = json.loads(raw.decode("utf-8"))
            if isinstance(loaded, dict):
                return loaded
        except:
            pass
        return {}
    try:
        loaded = json.loads(v)
        if isinstance(loaded, dict):
            return loaded
    except:
        pass
    try:
        loaded = ast.literal_eval(v)
        if isinstance(loaded, dict):
            return loaded
    except:
        pass
    return {}

def ld(v, d):
    if v in (None, ""):
        return d
    if isinstance(v, dict):
        return v
    if not isinstance(v, str) or len(v) > MAX_SAVE:
        return d
    try:
        loaded = dec(v)
        if isinstance(loaded, dict):
            return loaded
    except:
        pass
    return d

def st_energy(t):
    return 25 + 50 * si(t.get("archive"), 0, 0, T["archive"]["max"])

def fresh_state(now=None):
    now = _now() if now is None else now
    t = {k: 0 for k in T}
    r = {k: 0 for k in RM}
    r["energy"] = st_energy(t)
    return {"schema": STATE_SCHEMA, "created_at": now, "last_tick": now, "resources": r, "cycle_generated": {k: 0 for k in RM}, "lifetime_generated": {k: 0 for k in RM}, "buildings": {k: 0 for k in B}, "orbit": "balance", "expansions": 0, "cores": 0, "cores_total": 0, "launches": 0, "techs": t, "taps": 0, "known_recipes": [], "clues_seen": [], "discoveries": [], "crafted_recipes": [], "challenge_claimed": [], "stage_seen": 0, "scan_count": 0, "last_crank": 0, "crank_count": 0, "milestones_claimed": [], "auras": [], "event_cooldown": 0, "crank_time_bonus": 0, "speedrun_record": 0}

def fresh_global():
    return {"schema": GLOBAL_SCHEMA, "users": {}, "speedrun": {}}

def _check_milestone_cond(s, mid):
    if mid == "launch_1":
        return s.get("launches", 0) >= 1
    if mid == "launch_5":
        return s.get("launches", 0) >= 5
    if mid == "launch_10":
        return s.get("launches", 0) >= 10
    if mid == "civ_10k":
        return s.get("lifetime_generated", {}).get("civilization", 0) >= 10000
    if mid == "civ_100k":
        return s.get("lifetime_generated", {}).get("civilization", 0) >= 100000
    if mid == "civ_1m":
        return s.get("lifetime_generated", {}).get("civilization", 0) >= 1000000
    if mid == "crank_100":
        return s.get("crank_count", 0) >= 100
    if mid == "crank_1000":
        return s.get("crank_count", 0) >= 1000
    return False

def migrate_state(s, now=None):
    now = _now() if now is None else now
    base = fresh_state(now)
    if not isinstance(s, dict):
        return base
    base["created_at"] = min(cl(s.get("created_at"), now), now)
    base["last_tick"] = min(cl(s.get("last_tick"), now), now)
    for b in ("resources", "cycle_generated", "lifetime_generated"):
        src = s.get(b)
        if isinstance(src, dict):
            for k in RM:
                base[b][k] = cl(src.get(k), base[b][k])
    bd = s.get("buildings")
    if isinstance(bd, dict):
        for k in B:
            base["buildings"][k] = si(bd.get(k), 0, 0, 10**9)
    tch = s.get("techs")
    if isinstance(tch, dict):
        for k, v in T.items():
            base["techs"][k] = si(tch.get(k), 0, 0, v["max"])
    for k in ("expansions", "cores", "cores_total", "launches", "taps", "scan_count", "crank_count"):
        base[k] = si(s.get(k), base[k], 0, 10**12)
    base["cores_total"] = max(base["cores_total"], base["cores"])
    base["last_crank"] = cl(s.get("last_crank"), 0)
    base["event_cooldown"] = cl(s.get("event_cooldown", 0))
    base["stage_seen"] = si(s.get("stage_seen"), 0, 0, len(PS) - 1)
    base["crank_time_bonus"] = cl(s.get("crank_time_bonus", 0))
    base["speedrun_record"] = cl(s.get("speedrun_record", 0))
    for k, allowed in (("known_recipes", set(SR)), ("clues_seen", set(SR)), ("crafted_recipes", set(SR)), ("discoveries", set(SE)), ("milestones_claimed", set([m["id"] for m in MILESTONES])), ("auras", set([a["id"] for a in AURAS]))):
        v = s.get(k)
        if isinstance(v, list):
            base[k] = [x for x in v if x in allowed]
    claimed = s.get("challenge_claimed")
    if isinstance(claimed, list):
        base["challenge_claimed"] = sorted({si(x, -1) for x in claimed if 0 <= si(x, -1) < len(SC)})
    orb = OA.get(st(s.get("orbit"), "balance", 40).lower())
    if orb:
        base["orbit"] = orb
    base["schema"] = STATE_SCHEMA
    return base

def migrate_global(s):
    base = fresh_global()
    if not isinstance(s, dict):
        return base
    u = s.get("users")
    if isinstance(u, dict):
        clean = {}
        for uid, item in list(u.items())[:MAX_GLOBAL_USERS]:
            if not isinstance(item, dict):
                continue
            uid = st(uid, "", 80)
            if not uid:
                continue
            clean[uid] = {"nickname": st(item.get("nickname"), "玩家", 80), "cores_total": si(item.get("cores_total"), 0, 0, 10**12), "launches": si(item.get("launches"), 0, 0, 10**12), "lifetime_civilization": cl(item.get("lifetime_civilization"), 0), "updated_at": cl(item.get("updated_at"), 0)}
        base["users"] = clean
    sr = s.get("speedrun")
    if isinstance(sr, dict):
        base["speedrun"] = {uid: cl(t) for uid, t in sr.items() if isinstance(t, (int, float)) and t > 0}
    return base

def off_cap(s):
    return min(MAX_OFFLINE, BASE_OFFLINE + s["techs"]["cryosleep"] * OFFLINE_PER_TECH) * 3600

def slot_cap(s):
    return 24 + s["expansions"] * 12 + s["techs"]["tectonics"] * 6

def slots_used(s):
    return sum(s["buildings"][k] * B[k]["slots"] for k in B)

def global_mult(s):
    mult = (1.12**s["buildings"]["ring"]) * (1.20**s["techs"]["fusion"]) * (1 + 0.04 * s["cores_total"])
    for mid in s.get("milestones_claimed", []):
        for ms in MILESTONES:
            if ms["id"] == mid and "global_prod" in ms["reward"]:
                mult *= (1 + ms["reward"]["global_prod"])
    for aid in s.get("auras", []):
        for aura in AURAS:
            if aura["id"] == aid and "all" in aura["effect"]:
                mult *= aura["effect"]["all"]
    return mult

def aura_resource_mult(s, res):
    mult = 1.0
    for aid in s.get("auras", []):
        for aura in AURAS:
            if aura["id"] == aid:
                eff = aura.get("effect", {})
                if res in eff:
                    mult *= eff[res]
                if "all" in eff:
                    mult *= eff["all"]
    return mult

def prod_rates(s):
    rates = {k: 0.0 for k in RM}
    for k, info in B.items():
        cnt = s["buildings"][k]
        for r, rate in info["rate"].items():
            rates[r] += cnt * rate
    mult = global_mult(s) * (1 + 0.03 * len(set(s.get("challenge_claimed", []))))
    synth_all = 1.0
    synth_r = {k: 1.0 for k in RM}
    for rk in set(s.get("crafted_recipes", [])):
        recipe = SR.get(rk)
        if not recipe:
            continue
        target, factor = recipe["boost"]
        if target == "all":
            synth_all *= factor
        elif target in synth_r:
            synth_r[target] *= factor
    for k in rates:
        rates[k] *= mult * synth_all * synth_r[k] * aura_resource_mult(s, k)
    orb = s["orbit"]
    if orb == "star":
        rates["energy"] *= 2
    elif orb == "geology":
        rates["mineral"] *= 2
    elif orb == "ocean":
        rates["water"] *= 2
    elif orb == "climate":
        rates["air"] *= 2
    elif orb == "biosphere":
        rates["biomass"] *= 2
    elif orb == "city":
        rates["civilization"] *= 2
    else:
        for k in rates:
            rates[k] *= 1.18
    return rates

def settle(s, now):
    elapsed = max(0, now - s["last_tick"])
    applied = min(elapsed, off_cap(s))
    rates = prod_rates(s)
    gains = {k: rates[k] * applied for k in RM}
    for k, a in gains.items():
        s["resources"][k] = cl(s["resources"][k] + a)
        s["cycle_generated"][k] = cl(s["cycle_generated"][k] + a)
        s["lifetime_generated"][k] = cl(s["lifetime_generated"][k] + a)
    s["last_tick"] = now
    return elapsed, applied, gains

def b_discount(s):
    return 0.95**s["techs"]["automation"]

def b_cost(s, k, idx=None):
    info = B[k]
    cnt = s["buildings"][k] if idx is None else idx
    factor = (info["scale"]**cnt) * b_discount(s)
    return {r: base * factor for r, base in info["bc"].items()}

def can_afford(s, c):
    return all(s["resources"][k] + 1e-6 >= a for k, a in c.items())

def spend(s, c):
    for k, a in c.items():
        if s["resources"][k] < a:
            s["resources"][k] = 0
        else:
            s["resources"][k] = cl(s["resources"][k] - a)

def expand_cost(s):
    n = s["expansions"]
    return {"mineral": 120 * (1.80**n), "water": 60 * (1.55**n)}

def tech_cost(s, k):
    return s["techs"][k] + 1

def launch_gain(s):
    civ = s["cycle_generated"]["civilization"]
    return 0 if civ < 1000 else max(1, int(math.floor(math.sqrt(civ / 1000))))

def planet_stage(s):
    cur = PS[0]
    nxt = None
    for stg in PS[1:]:
        _, _, res, thr, _ = stg
        if s["cycle_generated"][res] >= thr:
            cur = stg
        else:
            nxt = stg
            break
    return cur, nxt

def stage_idx(s):
    cur, _ = planet_stage(s)
    for i, stg in enumerate(PS):
        if stg[0] == cur[0]:
            return i
    return 0

def recipe_pair(f, snd):
    w = frozenset((f, snd))
    if len(w) != 2:
        return None
    for k, recipe in SR.items():
        if frozenset(recipe["pair"]) == w:
            return k
    return None

def challenge_progress(s, idx):
    rates = prod_rates(s)
    r = s["resources"]
    if idx == 0:
        ok = rates["energy"] >= 2.5
        detail = f"恒星能 {fm(rates['energy'])}/2.50 每秒"
    elif idx == 1:
        ok = rates["mineral"] >= 0.75 and r["energy"] >= 80
        detail = f"矿物 {fm(rates['mineral'])}/0.75 每秒｜恒星能 {fm(r['energy'])}/80"
    elif idx == 2:
        ok = rates["water"] >= 0.25 and r["water"] >= 40
        detail = f"水 {fm(rates['water'])}/0.25 每秒｜持有水 {fm(r['water'])}/40"
    elif idx == 3:
        ok = rates["air"] >= 0.10 and r["air"] >= 30
        detail = f"大气 {fm(rates['air'])}/0.10 每秒｜持有大气 {fm(r['air'])}/30"
    elif idx == 4:
        ok = rates["biomass"] >= 0.030 and r["biomass"] >= 25
        detail = f"生物量 {fm(rates['biomass'])}/0.030 每秒｜持有生物量 {fm(r['biomass'])}/25"
    elif idx == 5:
        ok = rates["civilization"] >= 0.008 and rates["energy"] >= 3
        detail = f"文明 {fm(rates['civilization'])}/0.008 每秒｜恒星能 {fm(rates['energy'])}/3.00 每秒"
    else:
        ok = s["buildings"]["ring"] >= 1 and rates["civilization"] >= 0.015
        detail = f"轨道环 {s['buildings']['ring']}/1｜文明 {fm(rates['civilization'])}/0.015 每秒"
    return ok, detail

def planet_code(s):
    return f"P-{s['launches']+1:03d}"

def get_crank_duration(s):
    """计算单次手摇加速时长（秒），基础2分钟，每座传动装置+12秒（0.2分钟）"""
    base = 120
    trans = s["buildings"]["transmission"]
    return base + trans * 12

def get_crank_cooldown(s):
    """计算手摇冷却（秒），基础10秒，每座传动装置-0.15秒"""
    base = 10
    trans = s["buildings"]["transmission"]
    cd = base - trans * 0.15
    for mid in s.get("milestones_claimed", []):
        for ms in MILESTONES:
            if ms["id"] == mid and "crank_cooldown" in ms["reward"]:
                cd += ms["reward"]["crank_cooldown"]
    return max(3, cd)

def sync_global(g, s, nick, uid, now):
    users = g.setdefault("users", {})
    users[uid] = {"nickname": nick, "cores_total": s["cores_total"], "launches": s["launches"], "lifetime_civilization": s["lifetime_generated"]["civilization"], "updated_at": now}
    if len(users) > MAX_GLOBAL_USERS:
        ordered = sorted(users.items(), key=lambda kv: kv[1].get("updated_at", 0), reverse=True)
        g["users"] = dict(ordered[:MAX_GLOBAL_USERS])
    
    sr = g.setdefault("speedrun", {})
    if s.get("speedrun_record", 0) > 0:
        old = sr.get(uid, 0)
        if old == 0 or s["speedrun_record"] < old:
            sr[uid] = s["speedrun_record"]

def strip_prefix(cmd):
    cmd = st(cmd, "", MAX_CMD).strip()
    if not cmd:
        return ""
    parts = cmd.split()
    if parts and re.fullmatch(r"##[^\s]+", parts[0]):
        parts = parts[1:]
    return " ".join(parts).strip()

def parse_amt(v, d=1, mx=MAX_BUILD):
    if v is None:
        return d
    v = str(v).strip().lower()
    return "max" if v == "max" else si(v, d, 1, mx)

def phase_progress(s):
    cur, nxt = planet_stage(s)
    if nxt is None:
        return f"{cur[1]} {cur[0]}｜已达到本轮最高阶段"
    _, _, res, thr, _ = nxt
    icon, name = RM[res]
    val = s["cycle_generated"][res]
    return f"{cur[1]} {cur[0]}｜下一阶段：{nxt[0]}｜累计生成 {fm(val)}/{fm(thr)} {icon}{name}"

def formula_text():
    return """PLANET GENESIS｜精确公式
【1 建筑价格】第n座价格=基础价×scale^n×0.95^(自动化等级)。日照1.17/钻机1.18/融冰1.19/大气1.20/生态1.21/城市1.22/轨道环1.23/传动1.25。
【2 被动倍率】总倍率=1.12^(轨道环)×1.20^(聚变)×(1+0.04×累计星核)×里程碑×光环。单项轨道×2，平衡×1.18。
【3 TAP】每次=5恒星能×1.20^(聚变)×(1+0.04×累计星核)。
【4 槽位】上限=24+12×扩建+6×板块工程等级。
【5 扩建】第n次=120×1.80^n矿物+60×1.55^n水。
【6 启航】要求文明≥1000，收益=floor(sqrt(文明/1000))，至少1。
【7 科技】Lv=L时下一级需L+1星核。
【8 离线】默认8小时，休眠每级+4小时，最高72小时。
【9 挑战】每领取1个挑战，全产出×(1+0.03×已领数)。启航重置。
【10 合成】单资源×1.15，全资源×1.08。每行星最多造1次，配方永久保留。
【11 手摇】基础加速2分钟，冷却10秒。传动装置+0.2分钟（12秒）/座，-0.15秒/座冷却。最低3秒。手摇加速游戏内计时，影响竞速榜！
【12 里程碑】永久加成，跨启航保留。查看：##planet milestone (m)
【13 光环】星核购买，永久生效。查看：##planet aura (au)
无抽奖无概率，一切确定。"""

def version_text():
    return f"""{APP_NAME} v{APP_VERSION}
维护：剩菜
schema {STATE_SCHEMA}｜全局 {GLOBAL_SCHEMA}
无抽奖/无随机/纯确定增量

🙏 特别感谢：
• @日月终风 前辈 - 提供了本游戏的基础框架与核心玩法设计
• @秘银（Mithril） - 对整个游戏进行的局外操作优化与修改
• @三月七（十星三月七） - 早期版本玩家测试与反馈"""

def play_text():
    return """🎮 PLANET GENESIS｜新手快速上手

【第一步：采光起步】
输入：##planet tap 5 (或 ##planet ta 5)
效果：手动获得恒星能，用于建造第一座建筑。

【第二步：自动产出】
输入：##planet build 日照阵列 (或 ##planet b 日照阵列)
效果：每秒自动 +1 恒星能，挂机开始！

【第三步：解锁资源链】
攒够60恒星能后：
输入：##planet build 地壳钻机 (或 ##planet b 钻机)
效果：开始产出矿物。

【第四步：顺着资源链往上造】
矿物 → 融冰塔 (水) → 大气工厂 (大气) → 生态穹顶 (生物量) → 城市节点 (文明)
每个阶段都有挑战，达成后输入 ##planet challenge claim (或 ##planet ch claim) 领取奖励！

【第五步：手摇加速，资源暴涨 + 刷新竞速榜！】
输入：##planet crank (或 ##planet cr)
效果：立即获得当前产率 ×2分钟 的额外资源（冷却10秒）。
注意：每次手摇都会加速游戏内计时，让你在竞速榜上更快！快速传动装置可以强化手摇效果！

【第六步：星际启航，获得永久星核 & 上榜！】
文明累计达到1000后：
输入：##planet launch (或 ##planet l) 查看收益
确认启航：##planet launch confirm
你的启航用时（实际时间+手摇加速时间）将记录到竞速榜！

【常用缩写】
st = state      (状态)    s 也支持
ta = tap        (采光)
pl = planet     (星球阶段)
b  = build      (建造)
d  = dismantle  (拆除)
o  = orbit      (轨道)
e  = expand     (扩建)
ch = challenge  (挑战)
ev = events     (事件)
sc = scan       (扫描)
sy = synth      (合成)
te = tech       (科技)
l  = launch     (启航)
r  = rank       (排行)
cr = crank      (手摇)
m  = milestone  (里程碑)
au = aura       (光环)
sp = speedrun   (竞速榜)

【随时查看状态】
##planet state (或 ##planet st 或 ##planet s)

【获取帮助】
##planet help (或 ##planet h)"""

def tutorial_text():
    return """🚀 新手路线：##planet tap 2 → ##planet build 日照阵列 → 等能/s到2.5 → ##planet challenge claim → ##planet build 钻机 → ##planet orbit 地质 → 矿物够造融冰 → ##planet orbit 海洋 → 水够造大气 → ##planet orbit 气候 → 大气够造生态 → ##planet orbit 生态 → 生物够造城市 → ##planet orbit 文明 → 文明到1000 → ##planet launch → confirm"""

def atlas_text():
    lines = ["🪐 行星图鉴", "资源链：☀️→🪨→💧→🌫️→🌱→🏙️", "", "【阶段】"]
    for name, icon, res, thr, desc in PS:
        if res is None:
            cond = "初始"
        else:
            ico, n = RM[res]
            cond = f"累计{fm(thr)}{ico}{n}"
        lines.append(f"{icon}{name}｜{cond}｜{desc}")
    lines.append("")
    lines.append("【建筑】")
    for info in B.values():
        lines.append(f"{info['icon']}{info['name']}｜占{info['slots']}槽｜{info['desc']}")
    return "\n".join(lines)

def rules_text():
    return "\n\n".join(HP)

HP = (
    """【1/7｜目标/格式/起步】从裸岩星开始，把辐射转化为文明。无随机无抽奖。
格式：##planet <命令> <参数> (支持缩写)
开局：##planet tap 2 → ##planet build 日照阵列 → 等资源增长
常用缩写：st(状态) b(建造) cr(手摇) pl(星球) h(帮助)""",
    """【2/7｜资源与阶段】链：☀️恒星能→🪨矿物→💧水→🌫️大气→🌱生物量→🏙️文明
阶段：裸岩星→觉醒地核(矿物100)→原始海洋(水100)→稠密大气(大气100)→生命摇篮(生物100)→城市行星(文明100)→星际母星(文明1000)
查看：##planet planet (pl)""",
    """【3/7｜建筑】日照阵列(1槽+1能/s) 钻机(2槽+0.35矿/s) 融冰塔(3槽+0.12水/s) 大气工厂(4槽+0.05大气/s) 生态穹顶(6槽+0.018生物/s) 城市节点(8槽+0.004文明/s) 轨道环(12槽全产×1.12) 传动装置(2槽手摇强化：+0.2分钟/座，-0.15秒冷却/座)
购买：##planet build (b) <建筑> [数量|max]  拆除：##planet dismantle (d)
扩建：##planet expand (e) (+12槽)""",
    """【4/7｜轨道/离线】##planet orbit (o) 恒星|地质|海洋|气候|生态|文明|平衡
单项×2，平衡×1.18。离线默认8小时，休眠每级+4h，最高72h。建筑不消耗上游资源。""",
    """【5/7｜启航/星核/科技】文明≥1000可启航：##planet launch (l) → confirm
收益=floor(sqrt(文明/1000))，至少1星核。
永久科技：##planet tech (te) <恒星聚变|自动化|休眠|板块|档案> 下级需L+1星核。""",
    """【6/7｜排行/资料】##planet rank (r) 全服榜  ##planet speedrun (sp) 竞速榜(手摇加速计时)  ##planet atlas 图鉴  ##planet formula 公式  ##planet rules 规则  ##planet tutorial 教程  ##planet version 版本  ##planet reset (无缩写) 清档""",
    """【7/7｜手摇/里程碑/光环】##planet crank (cr) 手摇加速2分钟(10秒冷却)。传动装置强化手摇，同时加速游戏内计时。
##planet milestone (m) 查看永久里程碑。##planet aura (au) [buy] 查看或购买光环。"""
)
HP_TOPIC = {"资源": 2, "resource": 2, "阶段": 2, "建筑": 3, "build": 3, "槽位": 3, "扩建": 3, "轨道": 4, "orbit": 4, "离线": 4, "启航": 5, "launch": 5, "星核": 5, "科技": 5, "tech": 5, "排行": 6, "rank": 6, "竞速": 6, "speedrun": 6, "公式": 6, "formula": 6, "挑战": 6, "手摇": 7, "crank": 7, "里程碑": 7, "milestone": 7, "光环": 7, "aura": 7}
HC = {
    "help": {"aliases": ("h", "帮助"), "title": "HELP", "body": "##planet help (h) [命令|页码] 例：##planet help build"},
    "status": {"aliases": ("st", "s", "状态", "me"), "title": "STATUS", "body": "##planet state (st/s) 查看资源/产出/槽位/星核"},
    "tap": {"aliases": ("ta", "点", "采光"), "title": "TAP", "body": "##planet tap (ta) [次数] 每次5恒星能×聚变×星核，上限100次"},
    "planet": {"aliases": ("pl", "星球", "行星", "p"), "title": "PLANET", "body": "##planet planet (pl) 查看阶段/进度/启航状态"},
    "build": {"aliases": ("b", "建筑", "建造"), "title": "BUILD", "body": "##planet build (b) [建筑] [数量|max] 查看或购买"},
    "dismantle": {"aliases": ("d", "拆", "拆除"), "title": "DISMANTLE", "body": "##planet dismantle (d) <建筑> [数量|max] 返还50%"},
    "orbit": {"aliases": ("o", "轨道", "策略"), "title": "ORBIT", "body": "##planet orbit (o) [恒星|地质|海洋|气候|生态|文明|平衡]"},
    "expand": {"aliases": ("e", "扩建", "扩"), "title": "EXPAND", "body": "##planet expand (e) +12槽，价格随次数递增"},
    "tech": {"aliases": ("te", "科技", "研究"), "title": "TECH", "body": "##planet tech (te) [科技名] 查看或升级永久科技"},
    "launch": {"aliases": ("l", "启航", "跃迁"), "title": "LAUNCH", "body": "##planet launch (l) 查看收益，##planet launch confirm 执行"},
    "rank": {"aliases": ("r", "排行", "排行榜"), "title": "RANK", "body": "##planet rank (r) 全服排行"},
    "speedrun": {"aliases": ("sp", "竞速", "速通", "speed"), "title": "SPEEDRUN", "body": "##planet speedrun (sp) 查看/清空竞速榜。清空仅作者(剩菜)可用：##planet speedrun clear"},
    "atlas": {"aliases": ("图鉴", "星图"), "title": "ATLAS", "body": "##planet atlas 阶段与建筑图鉴"},
    "formula": {"aliases": ("公式", "math"), "title": "FORMULA", "body": "##planet formula 全部精确公式"},
    "rules": {"aliases": ("规则", "rule"), "title": "RULES", "body": "##planet rules 完整规则"},
    "tutorial": {"aliases": ("教程", "新手"), "title": "TUTORIAL", "body": "##planet tutorial 新手路线"},
    "version": {"aliases": ("版本", "ver", "v"), "title": "VERSION", "body": "##planet version"},
    "reset": {"aliases": ("清档", "清除", "clear"), "title": "RESET", "body": "##planet reset (无缩写) 警告，##planet reset CONFIRM 永久清档"},
    "challenge": {"aliases": ("ch", "挑战", "任务"), "title": "CHALLENGE", "body": "##planet challenge (ch) 查看，##planet challenge claim 领取"},
    "events": {"aliases": ("ev", "event", "事件", "事件簿"), "title": "EVENTS", "body": "##planet events (ev) 查看已发现隐藏事件"},
    "scan": {"aliases": ("sc", "扫描", "探索", "探测"), "title": "SCAN", "body": "##planet scan (sc) 消耗恒星能寻找合成线索"},
    "synth": {"aliases": ("sy", "合成", "合成器", "mix"), "title": "SYNTH", "body": "##planet synth (sy) [资源A] [资源B] 试配或制造；错误不扣资源"},
    "crank": {"aliases": ("cr", "摇", "手摇", "转"), "title": "CRANK", "body": "##planet crank (cr) 手摇加速2分钟（10秒冷却）。传动装置强化效果，同时加速游戏内计时！"},
    "milestone": {"aliases": ("m", "里程碑", "成就", "achieve"), "title": "MILESTONE", "body": "##planet milestone (m) 查看永久里程碑进度与奖励。"},
    "aura": {"aliases": ("au", "光环", "星核光环", "buff"), "title": "AURA", "body": "##planet aura (au) 查看光环列表；##planet aura buy <名称> 购买。"},
    "play": {"aliases": ("新手", "开始"), "title": "PLAY", "body": "##planet play 查看完整新手引导与缩写列表。"},
}
HC_ALIAS = {}
for c, item in HC.items():
    for k in (c,) + tuple(item.get("aliases", ())):
        n = " ".join(str(k).strip().lower().split())
        if n:
            HC_ALIAS[n] = c

HELP_INDEX = """PLANET GENESIS｜帮助目录 (支持缩写)
分页：##planet help 1-7
1目标/格式 2资源/阶段 3建筑 4轨道/离线 5启航/科技 6排行/资料 7手摇/里程碑/光环
命令索引(缩写)：st/s(状态) pl(星球) b(建造) d(拆除) o(轨道) e(扩建) ch(挑战) ev(事件) sc(扫描) sy(合成) te(科技) l(启航) r(排行) sp(竞速榜) cr(手摇) m(里程碑) au(光环) | reset(无缩写) | play(新手引导)"""

def help_page(page=None):
    t = " ".join(str(page or "").strip().lower().split())
    if not t:
        return HELP_INDEX
    if re.fullmatch(r"[1-7]", t):
        n = int(t)
        nav = []
        if n > 1:
            nav.append(f"上一页：##planet help {n-1}")
        if n < len(HP):
            nav.append(f"下一页：##planet help {n+1}")
        nav.append("目录：##planet help")
        return f"PLANET GENESIS｜帮助 {n}/{len(HP)}\n{HP[n-1]}\n\n" + "｜".join(nav)
    if t in HP_TOPIC:
        return help_page(str(HP_TOPIC[t]))
    c = HC_ALIAS.get(t)
    if c:
        item = HC[c]
        al = " / ".join([str(x) for x in item.get("aliases", ()) if str(x).strip()])
        return f"PLANET GENESIS｜{item['title']}\n" + (f"别名：{al}\n" if al else "") + item["body"] + "\n目录：##planet help"
    matches = difflib.get_close_matches(t, sorted(HC_ALIAS), n=3, cutoff=0.45)
    if matches:
        return f"⚠ 未找到命令：{t}\n你可能想查：{' / '.join(set([HC_ALIAS.get(m, m) for m in matches]))}"
    return f"⚠ 未找到命令帮助：{t}\n格式：##planet help <命令>｜目录：##planet help"

class ProtocolInputError(Exception):
    pass

class Game:
    def __init__(self, ctx, now_fn=None):
        if not isinstance(ctx, dict):
            raise ProtocolInputError("PB上下文必须是JSON对象")
        self.now = _now(now_fn)
        self.nick = st(ctx.get("nickname"), "", 80)
        self.uid = st(ctx.get("userID"), "", 80)
        if not self.nick or not self.uid:
            raise ProtocolInputError("缺少nickname或userID")
        self.state = migrate_state(ld(ctx.get("storage", {}), fresh_state(self.now)), self.now)
        self.gstate = migrate_global(ld(ctx.get("global", {}), fresh_global()))
        self.elapsed, self.applied, self.ogains = settle(self.state, self.now)
        sync_global(self.gstate, self.state, self.nick, self.uid, self.now)

    def _check_milestones(self):
        s = self.state
        claimed = set(s.get("milestones_claimed", []))
        new = []
        for ms in MILESTONES:
            if ms["id"] in claimed:
                continue
            if _check_milestone_cond(s, ms["id"]):
                claimed.add(ms["id"])
                new.append(ms)
                for k, v in ms["reward"].items():
                    if k == "global_prod":
                        pass
                    elif k == "cores":
                        s["cores"] = cl(s["cores"] + v)
                    elif k == "crank_cooldown":
                        pass
        if new:
            s["milestones_claimed"] = list(claimed)
            return new
        return []

    def status(self):
        s = self.state
        new_ms = self._check_milestones()
        rates = prod_rates(s)
        lines = [f"🪐 {APP_NAME}｜{self.nick}｜{planet_code(s)}", phase_progress(s)]
        for k, (icon, name) in RM.items():
            line = f"{icon}{name} {fm(s['resources'][k])}｜+{fm(rates[k])}/s"
            if rates[k] <= 1e-12:
                line += f"｜来源：{RSRC_HINT[k]}"
            lines.append(line)
        crank_time = get_crank_duration(s)
        crank_cd = get_crank_cooldown(s)
        lines.append(f"🔄 手摇｜加速{fm(crank_time/60)}分钟｜冷却{fm(crank_cd)}秒｜传动{s['buildings']['transmission']}座")
        lines.append(f"🧱 槽位 {slots_used(s)}/{slot_cap(s)}｜轨道：{OM[s['orbit']][0]}")
        lines.append(f"💠 星核 {s['cores']}可用 / {s['cores_total']}累计｜🚀 启航 {s['launches']}次")
        if self.elapsed >= 60 and self.applied > 0:
            suffix = "（只结算" + fs(self.applied) + "上限）" if self.applied + 1 < self.elapsed else ""
            nz = [f"+{fm(self.ogains[k])}{RM[k][0]}" for k in RM if self.ogains[k] > 0]
            lines.append(f"🌙 离线 {fs(self.elapsed)}{suffix}｜" + (" ".join(nz) if nz else "无被动产出"))
        gain = launch_gain(s)
        lines.append(f"🚀 {'已可启航｜+' + str(gain)+'星核' if gain else '启航进度｜文明 '+fm(s['cycle_generated']['civilization'])+'/1.000K'}")
        if new_ms:
            names = " / ".join([ms["name"] for ms in new_ms])
            lines.append(f"🎉 新里程碑达成：{names}！")
        crank_bonus = s.get("crank_time_bonus", 0)
        if crank_bonus > 0:
            lines.append(f"⏱️ 手摇已加速计时：{fs(crank_bonus)}")
        lines.append("操作｜##planet build (b)｜##planet planet (pl)｜##planet crank (cr)｜##planet milestone (m)｜##planet help (h)")
        return "\n".join(lines)

    def planet(self):
        s = self.state
        cur, nxt = planet_stage(s)
        lines = [f"          ☀️\n     ·     🛰️\n       {cur[1]}\n     {planet_code(s)}\n",
                 f"阶段：{cur[1]}{cur[0]}\n说明：{cur[4]}\n轨道：{OM[s['orbit']][0]}｜{OM[s['orbit']][1]}\n槽位：{slots_used(s)}/{slot_cap(s)}\n挑战：{SC[stage_idx(s)]['name']}｜##planet challenge (ch)",
                 "【本轮累计】"]
        for k, (icon, name) in RM.items():
            lines.append(f"{icon}{name}｜{fm(s['cycle_generated'][k])}")
        if nxt is None:
            lines.append(f"\n🪐 星际母星｜可获得 {launch_gain(s)} 星核\n##planet launch (l)")
        else:
            _, icon, res, thr, desc = nxt
            ico, n = RM[res]
            val = s["cycle_generated"][res]
            lines.append(f"\n下一阶段：{icon}{nxt[0]}\n条件：{fm(val)}/{fm(thr)}{ico}{n}\n变化：{desc}")
        return "\n".join(lines)

    def tap(self, args):
        cnt = parse_amt(args[0] if args else None, 1, 100)
        if cnt == "max":
            cnt = 100
        mult = (1.20**self.state["techs"]["fusion"]) * (1 + 0.04 * self.state["cores_total"])
        gain = 5 * cnt * mult
        old_val = self.state["resources"]["energy"]
        self.state["resources"]["energy"] = cl(old_val + gain)
        self.state["cycle_generated"]["energy"] = cl(self.state["cycle_generated"]["energy"] + gain)
        self.state["lifetime_generated"]["energy"] = cl(self.state["lifetime_generated"]["energy"] + gain)
        self.state["taps"] += cnt
        new_val = self.state["resources"]["energy"]
        return f"☀️ 采光×{cnt}｜+{fm(gain)}恒星能｜{fm(old_val)} → {fm(new_val)}"

    def building_list(self):
        s = self.state
        rates = prod_rates(s)
        lines = [f"🏗️ 建筑｜槽位{slots_used(s)}/{slot_cap(s)}｜倍率×{global_mult(s):.4f}｜轨道{OM[s['orbit']][0]}"]
        for k, info in B.items():
            cost = b_cost(s, k)
            prod = []
            for r, rate in info["rate"].items():
                prod.append(f"+{fm(rate*global_mult(s))}/s{RM[r][1]}")
            if k == "ring":
                prod = ["每座全产×1.12"]
            if k == "transmission":
                prod = [f"加速+0.2分钟/座 冷却-0.15秒/座"]
            lines.append(f"{info['icon']}{info['name']}×{s['buildings'][k]}｜占{info['slots']}槽｜下一座{rt(cost)}｜{';'.join(prod)}")
        return "\n".join(lines)

    def build(self, args):
        if not args:
            return self.building_list()
        k = BA.get(args[0].lower())
        if not k:
            return "⚠ 未知建筑｜日照/钻机/融冰/大气/生态/城市/轨道环/传动"
        amt = parse_amt(args[1] if len(args) > 1 else None, 1)
        limit = MAX_BUILD if amt == "max" else amt
        info = B[k]
        bought = 0
        spent = {r: 0 for r in RM}
        for _ in range(limit):
            if slots_used(self.state) + info["slots"] > slot_cap(self.state):
                break
            cost = b_cost(self.state, k)
            if not can_afford(self.state, cost):
                break
            spend(self.state, cost)
            for r, v in cost.items():
                spent[r] += v
            self.state["buildings"][k] += 1
            bought += 1
        if bought == 0:
            cost = b_cost(self.state, k)
            if slots_used(self.state) + info["slots"] > slot_cap(self.state):
                return f"⚠ 槽位不足｜{info['name']}需{info['slots']}槽｜{slots_used(self.state)}/{slot_cap(self.state)}｜##planet expand (e)"
            return f"⚠ 资源不足｜需要{rt(cost)}"
        return f"{info['icon']} 建造+{bought}｜{info['name']}×{self.state['buildings'][k]}\n消耗{rt({k:v for k,v in spent.items() if v})}｜槽位{slots_used(self.state)}/{slot_cap(self.state)}"

    def dismantle(self, args):
        if not args:
            return "格式：##planet dismantle (d) <建筑> [数量]"
        k = BA.get(args[0].lower())
        if not k:
            return "⚠ 未知建筑"
        amt = parse_amt(args[1] if len(args) > 1 else None, 1)
        if amt == "max":
            amt = self.state["buildings"][k]
        amt = min(amt, self.state["buildings"][k])
        if amt <= 0:
            return f"⚠ 没有{B[k]['name']}"
        refunds = {r: 0 for r in RM}
        for _ in range(amt):
            old = self.state["buildings"][k] - 1
            cost = b_cost(self.state, k, idx=old)
            self.state["buildings"][k] -= 1
            for r, v in cost.items():
                ret = v * 0.5
                self.state["resources"][r] = cl(self.state["resources"][r] + ret)
                refunds[r] += ret
        return f"♻️ 拆除{B[k]['name']}×{amt}｜返还50%{rt({k:v for k,v in refunds.items() if v})}｜槽位{slots_used(self.state)}/{slot_cap(self.state)}"

    def orbit(self, args):
        if not args:
            lines = [f"🛰️ 当前：{OM[self.state['orbit']][0]}｜{OM[self.state['orbit']][1]}", "可选："]
            for k, (n, d) in OM.items():
                lines.append(f"• {n}｜{d}{' ←当前' if k == self.state['orbit'] else ''}")
            lines.append("切换：##planet orbit (o) 恒星|地质|海洋|气候|生态|文明|平衡")
            return "\n".join(lines)
        k = OA.get(args[0].lower())
        if not k:
            return "⚠ 未知轨道"
        self.state["orbit"] = k
        return f"🛰️ 切换为：{OM[k][0]}｜{OM[k][1]}"

    def expand(self):
        cost = expand_cost(self.state)
        if not can_afford(self.state, cost):
            return f"⚠ 资源不足｜需要{rt(cost)}"
        spend(self.state, cost)
        self.state["expansions"] += 1
        return f"🧱 扩建完成｜+12槽｜上限{slot_cap(self.state)}｜消耗{rt(cost)}"

    def challenge(self, args):
        reached = stage_idx(self.state)
        claimed = set(self.state.get("challenge_claimed", []))
        want_claim = bool(args and args[0].lower() in ("claim", "领取", "领", "confirm", "确认"))
        if want_claim:
            newly = []
            reward = {k: 0 for k in RM}
            for idx in range(reached + 1):
                if idx in claimed:
                    continue
                ok, _ = challenge_progress(self.state, idx)
                if not ok:
                    continue
                claimed.add(idx)
                newly.append(idx)
                for r, a in SC[idx]["reward"].items():
                    self.state["resources"][r] = cl(self.state["resources"][r] + a)
                    reward[r] += a
            self.state["challenge_claimed"] = sorted(claimed)
            if not newly:
                return "⚠ 无可领取挑战"
            return f"🏁 领取：{' / '.join(SC[i]['name'] for i in newly)}\n奖励{rt({k:v for k,v in reward.items() if v})}\n全产出×{1+0.03*len(claimed):.2f}"
        lines = [f"🏁 挑战｜当前{PS[reached][1]}{PS[reached][0]}", "非硬门槛，完成+3%全产出", ""]
        for idx in range(reached + 1):
            info = SC[idx]
            ok, detail = challenge_progress(self.state, idx)
            if idx in claimed:
                status = "✅已领取"
            elif ok:
                status = "🎁可领取"
            else:
                status = "⏳进行中"
            lines.append(f"{PS[idx][1]}{info['name']}｜{status}\n  目标：{info['goal']}\n  当前：{detail}\n  奖励{rt(info['reward'])} +3%")
        lines.append("领取：##planet challenge claim")
        return "\n".join(lines)

    def events(self):
        disc = set(self.state.get("discoveries", []))
        lines = [f"🔭 事件簿｜阶段{PS[stage_idx(self.state)][1]}{PS[stage_idx(self.state)][0]}｜发现{len(disc)}/{len(SE)}", ""]
        if disc:
            for k, info in SE.items():
                if k in disc:
                    lines.append(f"✦ {info['name']}｜{info['text']}")
        else:
            lines.append("未发现隐藏事件")
        lines.append(f"\n还有{len(SE)-len(disc)}条未知")
        return "\n".join(lines)

    def scan(self):
        stage = stage_idx(self.state)
        seen = set(self.state.get("clues_seen", []))
        cand = [k for k, recipe in SR.items() if recipe["min_stage"] <= stage and k not in seen]
        if not cand:
            return "🔎 扫描完成｜无新线索（未消耗资源）"
        rk = cand[0]
        recipe = SR[rk]
        cost = 20 + 10 * stage
        if self.state["resources"]["energy"] + 1e-9 < cost:
            return f"⚠ 能量不足｜需要{fm(cost)}☀️"
        self.state["resources"]["energy"] -= cost
        seen.add(rk)
        self.state["clues_seen"] = [k for k in SR if k in seen]
        self.state["scan_count"] += 1
        return f"🔎 扫描｜消耗{fm(cost)}☀️\n「{recipe['clue']}」"

    def synth(self, args):
        known = set(self.state.get("known_recipes", []))
        crafted = set(self.state.get("crafted_recipes", []))
        if len(args) < 2:
            lines = [f"🧪 合成器｜发现{len(known)}/{len(SR)}｜本星制造{len(crafted)}", "输入：##planet synth (sy) <资源A> <资源B>", "错误不扣资源"]
            if known:
                lines.append("【已发现】")
                for k, recipe in SR.items():
                    if k not in known:
                        continue
                    fst, snd = recipe["pair"]
                    lines.append(f"• {recipe['name']}｜{RM[fst][1]}+{RM[snd][1]}｜{rt(recipe['cost'])}｜{recipe['effect']}｜{'✅已造' if k in crafted else '可造'}")
            else:
                lines.append("暂无配方，试试 ##planet scan (sc)")
            if len(SR) - len(known):
                lines.append(f"\n还有{len(SR)-len(known)}个未知")
            return "\n".join(lines)
        f = RA.get(args[0].lower())
        snd = RA.get(args[1].lower())
        if not f or not snd:
            return "⚠ 未知资源"
        if f == snd:
            return "⚠ 需要两种不同资源"
        rk = recipe_pair(f, snd)
        if not rk:
            return f"🧪 {RM[f][1]}+{RM[snd][1]}｜无反应，资源未消耗"
        recipe = SR[rk]
        stage = stage_idx(self.state)
        if stage < recipe["min_stage"]:
            return "🧪 反应不稳定｜需更高阶段"
        first_dis = rk not in known
        if first_dis:
            known.add(rk)
            self.state["known_recipes"] = [k for k in SR if k in known]
        if rk in crafted:
            return f"🧪 {recipe['name']}｜本星已造过"
        if not can_afford(self.state, recipe["cost"]):
            prefix = "✨ 配方发现！" if first_dis else "🧪 已知配方"
            return f"{prefix}｜{recipe['name']}\n组合{RM[f][1]}+{RM[snd][1]}\n需要{rt(recipe['cost'])}\n效果{recipe['effect']}"
        spend(self.state, recipe["cost"])
        crafted.add(rk)
        self.state["crafted_recipes"] = [k for k in SR if k in crafted]
        return f"{'✨发现并' if first_dis else '🧪'}合成{recipe['name']}\n消耗{rt(recipe['cost'])}\n效果{recipe['effect']}"

    def crank(self, args):
        s = self.state
        now = self.now
        last = s.get("last_crank", 0)
        cd = get_crank_cooldown(s)
        if now - last < cd:
            remaining = int(cd - (now - last))
            return f"⏳ 手摇杆冷却中｜剩余 {remaining} 秒"
        duration = get_crank_duration(s)
        rates = prod_rates(s)
        gains = {k: rates[k] * duration for k in RM}
        for k, amt in gains.items():
            s["resources"][k] = cl(s["resources"][k] + amt)
            s["cycle_generated"][k] = cl(s["cycle_generated"][k] + amt)
            s["lifetime_generated"][k] = cl(s["lifetime_generated"][k] + amt)
        s["last_crank"] = now
        s["crank_count"] = s.get("crank_count", 0) + 1
        s["crank_time_bonus"] = s.get("crank_time_bonus", 0) + duration
        
        reward_text = " ".join([f"+{fm(amt)}{RM[k][0]}" for k, amt in gains.items() if amt > 0])
        new_ms = self._check_milestones()
        msg = f"🔄 手摇完成！加速{fm(duration/60)}分钟\n{reward_text}\n⏱️ 累计加速计时：{fs(s['crank_time_bonus'])}"
        if new_ms:
            msg += "\n🎉 新里程碑：" + " / ".join([ms["name"] for ms in new_ms])
        return msg

    def speedrun(self, args):
        if args and args[0].lower() == "clear":
            if self.uid == "3771400817":
                self.gstate["speedrun"] = {}
                return "🏃 竞速榜已清空！所有记录已删除。"
            else:
                return "⚠ 只有作者（剩菜）可以清空竞速榜。"
        
        sr = self.gstate.get("speedrun", {})
        if not sr:
            return "🏃 竞速榜｜暂无记录\n完成首次启航后自动上榜！（手摇加速计时）"
        items = list(sr.items())
        items.sort(key=lambda x: x[1])
        lines = ["🏃 竞速榜｜最快启航记录（手摇加速计时）"]
        for i, (uid, t) in enumerate(items[:10], 1):
            nick = "玩家"
            uinfo = self.gstate.get("users", {}).get(uid, {})
            if uinfo:
                nick = uinfo.get("nickname", "玩家")
            mark = " ←你" if uid == self.uid else ""
            lines.append(f"{i}. {nick}｜{fs(t)}{mark}")
        return "\n".join(lines)

    def rank(self):
        sync_global(self.gstate, self.state, self.nick, self.uid, self.now)
        users = list(self.gstate.get("users", {}).items())
        users.sort(key=lambda kv: (kv[1].get("cores_total", 0), kv[1].get("lifetime_civilization", 0), kv[1].get("launches", 0)), reverse=True)
        lines = ["🏆 全服榜"]
        if not users:
            return "\n".join(lines + ["暂无数据"])
        for i, (uid, item) in enumerate(users[:20], 1):
            mark = " ←你" if uid == self.uid else ""
            lines.append(f"{i}. {item.get('nickname','玩家')}｜星核{item.get('cores_total',0)}｜启航{item.get('launches',0)}｜文明{fm(item.get('lifetime_civilization',0))}{mark}")
        return "\n".join(lines)

    def _secret_ready(self, k):
        s = self.state
        stg = stage_idx(s)
        if k == "double_shadow":
            return stg >= 1 and s["buildings"]["solar"] >= 4 and s["orbit"] == "star"
        if k == "black_beach":
            return stg >= 2 and s["buildings"]["melt"] >= 2
        if k == "charged_cloud":
            return stg >= 3 and s["orbit"] == "climate"
        if k == "green_frontier":
            return stg >= 4 and s["buildings"]["bio"] >= 2
        if k == "night_sync":
            return stg >= 5 and s["orbit"] == "city" and s["buildings"]["city"] >= 2
        if k == "ring_eclipse":
            return stg >= 5 and s["buildings"]["ring"] >= 1
        return False

    def _post_action(self, msg):
        s = self.state
        notices = []
        stg = stage_idx(s)
        seen = s.get("stage_seen", 0)
        if stg > seen:
            crossed = stg - seen
            s["stage_seen"] = stg
            notice = SET[stg]
            if crossed > 1:
                notice += f"\n（跨越{crossed}个阶段）"
            notices.append(notice)
        disc = set(s.get("discoveries", []))
        for k, info in SE.items():
            if k in disc or not self._secret_ready(k):
                continue
            disc.add(k)
            for r, a in info.get("reward", {}).items():
                s["resources"][r] = cl(s["resources"][r] + a)
            notices.append(f"🔭【{info['name']}】{info['text']}\n余波{rt(info.get('reward', {}))}")
        s["discoveries"] = [k for k in SE if k in disc]
        new_ms = self._check_milestones()
        if new_ms:
            notices.append("🎉 新里程碑：" + " / ".join([ms["name"] for ms in new_ms]))
        if notices:
            return msg + "\n\n" + "\n\n".join(notices)
        return msg

    def tech(self, args):
        if not args:
            lines = [f"💠 科技｜星核{self.state['cores']}/{self.state['cores_total']}"]
            for k, info in T.items():
                lv = self.state["techs"][k]
                c = "MAX" if lv >= info["max"] else str(tech_cost(self.state, k))
                lines.append(f"• {info['name']} Lv{lv}/{info['max']}｜下级{c}星核｜{info['desc']}")
            return "\n".join(lines)
        k = TA.get(args[0].lower())
        if not k:
            return "⚠ 未知科技"
        info = T[k]
        lv = self.state["techs"][k]
        if lv >= info["max"]:
            return f"⚠ {info['name']}已满"
        cost = tech_cost(self.state, k)
        if self.state["cores"] < cost:
            return f"⚠ 星核不足｜需{cost}"
        self.state["cores"] -= cost
        self.state["techs"][k] += 1
        return f"💠 {info['name']} Lv{lv}→{lv+1}｜消耗{cost}星核\n{info['desc']}"

    def launch(self, args):
        gain = launch_gain(self.state)
        confirm = bool(args and args[0].lower() in ("confirm", "确认", "yes", "y"))
        if not confirm:
            if gain <= 0:
                civ = self.state["cycle_generated"]["civilization"]
                return f"🚀 未达条件｜文明{fm(civ)}/1.000K"
            return f"🚀 启航｜可获得{gain}星核\n清空：资源/累计/建筑/扩建/轨道/合成/挑战\n保留：星核/科技/配方/事件/历史/启航次数/里程碑/光环\n确认：##planet launch confirm"
        if gain <= 0:
            return "⚠ 文明不足1000"
        old = self.state
        
        # ===== 修复：竞速榜计时改为加法（实际时间 + 手摇加速时间）=====
        actual_elapsed = old.get("last_tick", self.now) - old.get("created_at", self.now)
        crank_bonus = old.get("crank_time_bonus", 0)
        # 总时间 = 实际游玩时间 + 手摇跳过的时间（加法）
        total_elapsed = max(1, actual_elapsed + crank_bonus)  # 至少1秒
        
        # 更新竞速榜（用时越短越好）
        best = old.get("speedrun_record", 0)
        if best == 0 or total_elapsed < best:
            old["speedrun_record"] = total_elapsed
        
        new = fresh_state(self.now)
        new["techs"] = dict(old["techs"])
        new["known_recipes"] = list(old.get("known_recipes", []))
        new["clues_seen"] = list(old.get("clues_seen", []))
        new["discoveries"] = list(old.get("discoveries", []))
        new["scan_count"] = si(old.get("scan_count"), 0, 0, 10**12)
        new["milestones_claimed"] = list(old.get("milestones_claimed", []))
        new["auras"] = list(old.get("auras", []))
        new["cores_total"] = old["cores_total"] + gain
        new["cores"] = old["cores"] + gain
        new["launches"] = old["launches"] + 1
        new["created_at"] = old["created_at"]
        new["lifetime_generated"] = dict(old["lifetime_generated"])
        new["taps"] = old["taps"]
        new["crank_count"] = old.get("crank_count", 0)
        new["last_tick"] = self.now
        self.state = new
        sync_global(self.gstate, self.state, self.nick, self.uid, self.now)
        time_str = fs(total_elapsed)
        return f"🚀 启航完成｜+{gain}星核\n新星{planet_code(self.state)}｜开局{fm(self.state['resources']['energy'])}☀️\n累计{self.state['cores_total']}｜可用{self.state['cores']}｜第{self.state['launches']}次\n⏱️ 本次启航用时：{time_str}（实际时间+手摇加速时间）"

    def milestone(self, args):
        s = self.state
        claimed = set(s.get("milestones_claimed", []))
        lines = ["🏆 永久里程碑", "已达成 " + str(len(claimed)) + "/" + str(len(MILESTONES)), ""]
        for ms in MILESTONES:
            done = ms["id"] in claimed
            status = "✅" if done else "⏳"
            lines.append(f"{status} {ms['name']}｜{ms['desc']}")
            if not done:
                if _check_milestone_cond(s, ms["id"]):
                    lines.append("   🎁 条件已达成！输入 ##planet state 自动领取")
                else:
                    lines.append("   ⏳ 条件未达成")
            else:
                reward_texts = []
                for k, v in ms["reward"].items():
                    if k == "global_prod":
                        reward_texts.append(f"全产出+{v*100:.0f}%")
                    elif k == "cores":
                        reward_texts.append(f"+{v}星核")
                    elif k == "crank_cooldown":
                        reward_texts.append(f"手摇冷却{v}秒")
                lines.append(f"   ✅ 已领取｜奖励：{' '.join(reward_texts)}")
            lines.append("")
        return "\n".join(lines)

    def aura(self, args):
        s = self.state
        owned = set(s.get("auras", []))
        if not args or args[0].lower() not in ("buy", "购买"):
            lines = ["⭐ 星核光环｜已购买 " + str(len(owned)) + "/" + str(len(AURAS)), "光环永久生效，跨启航保留", ""]
            for aura in AURAS:
                status = "✅已拥有" if aura["id"] in owned else f"需{aura['cost']}星核"
                lines.append(f"{aura['name']}｜{status}｜{aura['desc']}")
            lines.append("购买：##planet aura buy <名称> 例：##planet aura buy 地核光环")
            return "\n".join(lines)
        name = " ".join(args[1:]).strip()
        if not name:
            return "⚠ 请指定光环名称，如：##planet aura buy 地核光环"
        target = None
        for aura in AURAS:
            if aura["name"] == name or aura["id"] == name or aura["id"] in name:
                target = aura
                break
        if not target:
            names = " / ".join([a["name"] for a in AURAS])
            return f"⚠ 未找到光环：{name}\n可用：{names}"
        if target["id"] in owned:
            return f"⚠ {target['name']} 已拥有"
        if s["cores"] < target["cost"]:
            return f"⚠ 星核不足｜{target['name']}需要{target['cost']}星核，当前{s['cores']}"
        s["cores"] -= target["cost"]
        owned.add(target["id"])
        s["auras"] = list(owned)
        return f"⭐ 购买成功｜{target['name']}\n效果：{target['desc']}\n剩余星核 {s['cores']}"

    def reset(self, args):
        if not args or args[0] != "CONFIRM":
            return "⚠ 永久清档，确认请输：##planet reset CONFIRM"
        self.state = fresh_state(self.now)
        return "🧹 已清档｜重新开始"
    
    def export(self):
        try:
            data = enc(self.state)
            compressed = gzip_text(data)
            return f"📦 导出存档成功！\n请复制以下内容保存：\n{compressed}"
        except Exception as e:
            return f"⚠ 导出失败：{str(e)}"

    def _import(self, args):
        if not args:
            return "⚠ 用法：##planet import <压缩存档字符串>"
        try:
            raw = args[0]
            decoded = ungzip_text(raw)
            new_state = json.loads(decoded)
            if not isinstance(new_state, dict):
                return "⚠ 导入失败：数据格式错误"
            self.state = migrate_state(new_state, self.now)
            return f"✅ 导入存档成功！\n{self.status()}"
        except json.JSONDecodeError as e:
            return f"⚠ 导入失败：JSON解析错误 - {str(e)}"
        except Exception as e:
            return f"⚠ 导入失败：{str(e)}"

    def run(self, cmd):
        cmd = strip_prefix(cmd)
        c = ""
        if not cmd:
            msg = "📋 请输入命令。查看状态：##planet state (s/st)｜查看帮助：##planet help (h)"
        else:
            parts = cmd.split()
            c = parts[0].lower()
            args = parts[1:]
            hm = re.fullmatch(r"(?:h|help|帮助)(?:\s+(.+))?", cmd, re.I)
            if hm:
                msg = help_page(hm.group(1))
            elif c in ("state", "状态", "me", "status", "s", "st"):
                msg = self.status()
            elif c in ("tap", "点", "采光", "ta"):
                msg = self.tap(args)
            elif c in ("planet", "星球", "行星", "pl", "p"):
                msg = self.planet()
            elif c in ("build", "b", "建筑", "建造"):
                msg = self.build(args)
            elif c in ("dismantle", "d", "拆", "拆除"):
                msg = self.dismantle(args)
            elif c in ("orbit", "o", "轨道", "策略"):
                msg = self.orbit(args)
            elif c in ("expand", "e", "扩建", "扩"):
                msg = self.expand()
            elif c in ("challenge", "ch", "挑战", "任务"):
                msg = self.challenge(args)
            elif c in ("events", "ev", "event", "事件", "事件簿"):
                msg = self.events()
            elif c in ("scan", "sc", "扫描", "探索", "探测"):
                msg = self.scan()
            elif c in ("synth", "sy", "合成", "合成器", "mix"):
                msg = self.synth(args)
            elif c in ("tech", "科技", "研究", "te"):
                msg = self.tech(args)
            elif c in ("launch", "l", "启航", "跃迁"):
                msg = self.launch(args)
            elif c in ("rank", "r", "排行", "排行榜"):
                msg = self.rank()
            elif c in ("speedrun", "sp", "竞速", "速通", "speed"):
                msg = self.speedrun(args)
            elif c in ("crank", "摇", "手摇", "转", "cr"):
                msg = self.crank(args)
            elif c in ("milestone", "m", "里程碑", "成就", "achieve"):
                msg = self.milestone(args)
            elif c in ("aura", "au", "光环", "星核光环", "buff"):
                msg = self.aura(args)
            elif c in ("play", "新手", "开始"):
                msg = play_text()
            elif c in ("atlas", "图鉴", "星图"):
                msg = atlas_text()
            elif c in ("formula", "公式", "math"):
                msg = formula_text()
            elif c in ("rules", "规则", "rule"):
                msg = rules_text()
            elif c in ("tutorial", "教程", "新手路线"):
                msg = tutorial_text()
            elif c in ("version", "版本", "ver", "v"):
                msg = version_text()
            elif c in ("reset", "清档", "清除", "clear"):
                msg = self.reset(args)
            elif c in ("export", "导出", "ex"):
                msg = self.export()
            elif c in ("import", "导入", "im"):
                msg = self._import(args)
            else:
                msg = f"⚠ 未知命令：{parts[0]}\n##planet help 查看目录"
        quiet = {"help", "h", "帮助", "rules", "rule", "formula", "math", "version", "ver", "v", "tutorial", "教程", "atlas", "图鉴", "events", "ev", "event", "事件簿", "state", "status", "s", "st", "状态", "me", "planet", "pl", "星球", "行星", "p", "rank", "r", "排行", "排行榜", "speedrun", "sp", "竞速", "速通", "speed", "milestone", "m", "里程碑", "成就", "achieve", "aura", "au", "光环", "星核光环", "buff", "play", "新手", "开始", "export", "导出", "ex", "import", "导入", "im"}
        if c and c not in quiet:
            msg = self._post_action(msg)
        sync_global(self.gstate, self.state, self.nick, self.uid, self.now)
        return {"content": msg, "storage": enc(self.state), "global": enc(self.gstate)}

def error_packet(msg, ctx=None, now=None):
    now = _now() if now is None else now
    ctx = ctx if isinstance(ctx, dict) else {}
    state_data = migrate_state(ld(ctx.get("storage", {}), fresh_state(now)), now)
    gs = migrate_global(ld(ctx.get("global", {}), fresh_global()))
    return {"content": f"⚠ {msg}\n请通过#pb add添加并由PB运行器调用", "storage": enc(state_data), "global": enc(gs)}

def run_pb_session(ctx, cmd="", now_fn=None):
    try:
        return Game(ctx, now_fn=now_fn).run(cmd)
    except Exception as e:
        return error_packet(f"运行错误：{str(e)[:100]}", ctx, _now(now_fn))

def run_protocol(cline, cmdline="", now_fn=None):
    try:
        if not isinstance(cline, str) or len(cline) > MAX_PROTOCOL:
            raise ValueError
        ctx = json.loads(cline)
        if not isinstance(ctx, dict):
            raise ValueError
    except Exception:
        return json.dumps(error_packet("未收到有效的PB JSON上下文", now=_now(now_fn)))
    return json.dumps(run_pb_session(ctx, cmdline, now_fn=now_fn))

def main():
    try:
        cline = input()
    except:
        cline = ""
    try:
        cmdline = input()
    except:
        cmdline = ""
    print(run_protocol(cline, cmdline))

if __name__ == "__main__":
    main()
