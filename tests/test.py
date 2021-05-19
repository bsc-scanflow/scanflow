import numpy as np

a = np.load('./test_images.npy')
b = np.load('./train_images.npy')
print(type(a))
print(len(a))
print(len(b))
tmp = []
tmp.append(a)
print(len(tmp))
tmp.append(b)
print(len(tmp))

c = []
c = np.concatenate((tmp), axis=0)
print(len(c))


np.save('merge.npy', c)
