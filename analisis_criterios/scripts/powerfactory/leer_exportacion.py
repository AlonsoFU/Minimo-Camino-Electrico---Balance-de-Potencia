import pandas as pd, sys
U = '/root/.claude/uploads/aef6561c-d05e-5d6f-b069-1de59162b42e/'
def leer(f):
    raw = open(U + f, 'rb').read().decode('utf-8', errors='replace').replace('\r\n', '\n').split('\n')
    h = raw[0].split('\t'); u = raw[1].split('\t')
    # nombres únicos: si se repite, agrega la unidad/clase o un sufijo
    cols, vistos = [], {}
    for i, c in enumerate(h):
        k = c if c not in vistos else f'{c} [{i}]'
        vistos[c] = 1; cols.append(k)
    rows = [r.split('\t') for r in raw[2:] if r.strip()]
    df = pd.DataFrame([r + [''] * (len(cols) - len(r)) for r in rows], columns=cols)
    return df.apply(lambda s: s.str.strip())
num = lambda s: pd.to_numeric(s.str.replace(',', '.', regex=False), errors='coerce')
