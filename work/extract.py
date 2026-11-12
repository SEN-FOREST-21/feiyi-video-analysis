import re, sys, html, os
from html.parser import HTMLParser

BLOCK = {'h1','h2','h3','h4','p','li','div','section','blockquote','tr','td','th'}

class P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out=[]; self.skip=0; self.cur=[]
        self.in_math=0; self.mathbuf=''; self.mathkind=None
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag in ('script','style','aside'):
            self.skip+=1; return
        if tag=='span' and 'math' in a.get('class',''):
            cls=a.get('class','')
            self.in_math+=1
            self.mathkind='display' if 'display' in cls else 'inline'
            self.mathbuf=''
            return
        if tag in ('h1','h2','h3','h4'):
            self.flush(); self.cur.append('\n'+'#'*int(tag[1])+' ')
        elif tag=='li':
            self.flush(); self.cur.append('\n- ')
        elif tag in ('p','div','section','blockquote','tr'):
            self.flush()
        elif tag=='br':
            self.cur.append('\n')
        elif tag=='sup':
            self.cur.append('^')
        elif tag=='sub':
            self.cur.append('_')
        elif tag in ('td','th'):
            self.cur.append(' | ')
    def handle_endtag(self,tag):
        if tag in ('script','style','aside'):
            self.skip-=1; return
        if tag=='span' and self.in_math>0:
            self.in_math-=1
            d=self.mathbuf.strip()
            if self.mathkind=='display':
                self.cur.append('\n$$'+d+'$$\n')
            else:
                self.cur.append('$'+d+'$')
            self.mathbuf=''
            return
        if tag in ('h1','h2','h3','h4','p','li','div','section','blockquote','tr'):
            self.flush()
    def handle_data(self,data):
        if self.skip>0: return
        if self.in_math>0:
            self.mathbuf+=data
        else:
            self.cur.append(data)
    def flush(self):
        s=''.join(self.cur)
        s=re.sub(r'[ \t]+',' ',s)
        s=re.sub(r'\n{3,}','\n\n',s)
        s=s.strip()
        if s: self.out.append(s)
        self.cur=[]

path=sys.argv[1]
s=open(path,encoding='utf-8').read()
i=s.find('<body')
body=s[i:] if i>0 else s
p=P(); p.feed(body)
txt='\n\n'.join(p.out)
txt=re.sub(r'\n{3,}','\n\n',txt)
print(txt)
