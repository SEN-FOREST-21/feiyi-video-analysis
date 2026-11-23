# -*- coding: utf-8 -*-
import re

src = '/workspace/概率论-详细版.html'
s = open(src, encoding='utf-8').read()

start = s.find('<!-- ================= M4-01 ================= -->')
end = s.find('<!-- ================= M5-01 ================= -->')
assert start != -1 and end != -1 and start < end

block = s[start:end]
# 只转义“非 HTML 标签”的 < ：< 后面不是 / 也不是已知标签名时，转成 &lt;
KNOWN = ['h2','h3','div','p','b','small','ul','li','br']
pat = re.compile(r'<(?!/' + '|' + '|'.join(KNOWN) + r')')
new_block = pat.sub('&lt;', block)

print('转义替换次数:', block.count('<') - new_block.count('<'))

s2 = s[:start] + new_block + s[end:]
open(src, 'w', encoding='utf-8').write(s2)
print('已写回')
