exec(open('cadena.py').read().split("base = estado([])")[0])
c = pd.read_pickle(OUT + 'cadena.pkl'); dec = c['dec']; resto = [b for b in c['bloques'] if b not in dec]
Q = pd.read_pickle(OUT + 'recomendacion.pkl'); A = list(Q[Q.dec.str.startswith('A')].Tramo)
for nom, apl in [('tras aplicar los 12', A), ('tras aplicar los 44', dec)]:
    b0 = estado(apl); n = 0; mm = 0
    for b in resto:
        s = estado(apl + [b]); ch, m = plata(b0, s)
        if len(ch): n += 1; mm += m
    print(f'{nom}: de los 624, ahora decisivos {n} ({mm:.0f} MM$/mes sumando de a uno)')
