exec(open('zonas_exh_prep.py').read().split("for z, k in semillas.items():")[0])
c = pd.read_pickle(OUT + 'cadena.pkl'); dec = c['dec']
Gt = nx.Graph()
for (u, v), x in pesos(o0)[1].items(): Gt.add_edge(nm[u], nm[v])
comb = set(x for s_ in F['Combinación'] for x in s_.split(' + '))
semilla = set(dec) | comb
H = nx.Graph(); H.add_nodes_from(semilla)
def entorno(b):
    n1 = ends[b]; return n1 | {w for n in n1 if n in Gt for w in Gt[n]}
zona_de = {b: entorno(b) for b in semilla}
vec = {b: {x for x in bloques if ends[x] & zona_de[b]} for b in semilla}
for b in semilla:
    for x in vec[b]: H.add_edge(b, x)
Z = sorted(nx.connected_components(H), key=len, reverse=True)
tot = set().union(*Z)
print('zonas:', len(Z), ' tramos en zonas:', len(tot), ' (decisivos:', len(set(dec) & tot), ', vecinos que difieren:', len(tot - set(dec)), ')')
print('tamaños:', [len(z) for z in Z])
pd.to_pickle(Z, OUT + 'zonas_def.pkl')
