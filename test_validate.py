"""校验器的回归测试
跑法（在仓库根目录）：python test_validate.py
"""

import copy
import json

import extract

with open("sample_response.json", encoding="utf-8") as f:
    GOOD = json.load(f)

SOURCE = " ".join(extract.TEXT.split())

def fresh():
    """每次从干净样本复制一份，免得上一个用例改脏了下一个。"""
    return copy.deepcopy(GOOD)

# ---------- 形状层 ----------

bad = fresh()
del bad["takeaways"]
assert extract.check_structure(bad) == ["MISSING FIELD: takeaways"], bad

bad = fresh()
bad["difficulty"] = "easyyy"
assert "WRONG VALUE" in extract.check_structure(bad)[0], bad

bad = fresh()
bad["key_sentences"] = bad["key_sentences"][:2]
assert "WRONG COUNT" in extract.check_structure(bad)[0], bad

bad = fresh()
bad["vocabulary"] = bad["vocabulary"] * 2
assert "WRONG COUNT" in extract.check_structure(bad)[0], bad

bad = fresh()
del bad["vocabulary"][0]["pos"]
assert extract.check_structure(bad) == ["MISSING FIELD: vocabulary[0].pos"], bad

bad = fresh()
bad["key_sentences"] = "nope"
assert "WRONG TYPE" in extract.check_structure(bad)[0], bad

assert extract.check_structure(GOOD) == []

# ---------- 顺序：形状不对时 validate 挡住 ----------

bad = fresh()
del bad["key_sentences"]
assert extract.validate(bad, SOURCE) == ["MISSING FIELD: key_sentences"], bad

# ---------- 内容层 ----------

# sample_response.json 里冻结着一个已知的中英串味（"how软件 engineers"）。
# 哪天重新生成这份样本，这条断言可能要跟着改。
problems = extract.check_content(GOOD, SOURCE)
assert any("CHINESE LEAK in note" in p for p in problems), problems

bad = fresh()
bad["key_sentences"][0]["text"] = "This sentence does not appear in the passage."
assert any("MISMATCH" in p for p in extract.check_content(bad, SOURCE)), bad


print("all passed")