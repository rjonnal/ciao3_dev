import numpy as np
from matplotlib import pyplot as plt

cats = np.arange(10).astype(int)
vals = np.random.rand(len(cats))

bh = plt.bar(cats,vals)
print(dir(bh))
