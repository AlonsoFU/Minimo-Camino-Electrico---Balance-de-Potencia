import pandas as pd, numpy as np, networkx as nx, sys, pickle
src0=open('banco.py').read().split("grafos = {k")[0]
exec(src0)
grafos={k:grafo(v) for k,v in esc.items()}
pickle.dump(grafos,open('grafos.pkl','wb'))
