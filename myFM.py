# ipython3
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction import DictVectorizer

FEATS = [
    'user',
    'item',
    # 'timestamp',
    # 'age',
    # 'gender',
    # 'occupation',
    # 'release_date',
    'Action',
    'Adventure',
    'Animation',
    'Childrens',
    'Comedy',
    'Crime',
    'Documentary',
    'Drama',
    'Fantasy',
    'Film_Noir',
    'Horror',
    'Musical',
    'Mystery',
    'Romance',
    'Sci_Fi',
    'Thriller',
    'War',
    'Western',
    ]

# FEATS = [
#     'a',
#     'b',
#     'c',
#     ]

LABEL = 'rating'

df = pd.read_csv('./data/input/train.csv')[4000:4200]
# df = pd.read_csv('./data/input/train_small.csv')
dv = DictVectorizer()
X = dv.fit_transform(df[FEATS].to_dict(orient='record')).toarray()
y = np.array(df[LABEL], dtype=np.float64)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.5, random_state=42)

def fm(x, w_0, w, v):
    n = len(FEATS)
    k = v.shape[1]
    w_1 = (x * w).sum()
    w_2 = 0
    for i in range(0, n):
        for j in range(i + 1, n):
            w_2 += v[i].dot(v[j]) * x[i] * x[j]
    return w_0 + w_1 + w_2

def model(X, w_0, w, v):
    y = []
    for x in X:
        y = fm(x, w_0, w, v)
    return np.array(y)

def fm_grad_w_0(x, w_0, w, v):
    return 1

def fm_grad_w_i(x, w_0, w, v, i):
    return x[i]

def fm_grad_v_i_f(x, w_0, w, v, i, f):
    n = len(FEATS)
    a = 0
    for j in range(n):
        a += v[j][f] * x[j]
    return x[i] * a - v[i][f] * x[i] ** 2

def Loss(X, y, w_0, w, v, reg_w_0, reg_w, reg_v):
    return np.mean(
        (model(X, w_0, w, v) - y) ** 2 
        # normlization
        # + w_0 * reg_w_0 ** 2 
        # + np.sum(w * reg_w ** 2) 
        # + np.sum(v * reg_v ** 2)
        )

def loss(x, y, w_0, w, v, reg_w_0, reg_w, reg_v):
    return (fm(x, w_0, w, v) - y) ** 2 
        # normlization
        # + w_0 * reg_w_0 ** 2 
        # + np.sum(w * reg_w ** 2) 
        # + np.sum(v * reg_v ** 2)
        

DELTA = 0.0001
def loss_grad_w_0(x, y, w_0, w, v, reg_w_0, reg_w, reg_v):
    return (2 * (fm(x, w_0, w, v) - y)) * fm_grad_w_0(x, w_0, w, v) + 2 * reg_w_0 * w_0
    # calc by delta
    # return (loss(x, y, w_0 + DELTA, w, v, reg_w_0, reg_w, reg_v) - loss(x, y, w_0 - DELTA, w, v, reg_w_0, reg_w, reg_v)) / (DELTA * 2)

def loss_grad_w_i(x, y, w_0, w, v, i, reg_w_0, reg_w, reg_v):
    return (2 * (fm(x, w_0, w, v) - y)) * fm_grad_w_i(x, w_0, w, v, i) + 2 * reg_w[i] * w[i]
    # calc by delta
    # dw1 = w.copy()
    # dw1[i] += DELTA
    # dw2 = w.copy()
    # dw2[i] -= DELTA
    # return (loss(x, y, w_0, dw1, v, reg_w_0, reg_w, reg_v) - loss(x, y, w_0, dw2, v, reg_w_0, reg_w, reg_v)) / (DELTA * 2)

def loss_grad_v_i_f(x, y, w_0, w, v, i, f, reg_w_0, reg_w, reg_v):
    return (2 * (fm(x, w_0, w, v) - y)) * fm_grad_v_i_f(x, w_0, w, v, i, f) + 2 * reg_v[i][f] * v[i][f]
    # calc by delta
    # dv1 = v.copy()
    # dv1[i][f] += DELTA
    # dv2 = v.copy()
    # dv2[i][f] -= DELTA
    # return (loss(x, y, w_0, w, dv1, reg_w_0, reg_w, reg_v) - loss(x, y, w_0, w, dv2, reg_w_0, reg_w, reg_v)) / (DELTA * 2)

def eval(epoch, batch, X_train, y_train, X_test, y_test, model, params):
    def mse(a, b):
        return np.mean((a - b) ** 2)
    w_0, w, v = params
    mse_train = mse(y_train, model(X_train, w_0, w, v))
    mse_test  = mse(y_test,  model(X_test,  w_0, w, v))
    loss_train = Loss(X_train,  y_train, w_0, w, v, reg_w_0, reg_w, reg_v)
    print('epoch:%d batch:%d train loss:%.4f train mse:%.4f test mse:%.4f' % (epoch, batch, loss_train, mse_train, mse_test))

num_epochs = 100
batch_size = 100
eta = 1e-3 # learning rate
k = 1 # dim of factorization
sigma = 1 # regulization
n = len(FEATS)
w_0 = 0
w = np.zeros((n))
v = np.zeros((n, k))

reg_w_0 = np.abs(np.random.normal(0, sigma, 1))
reg_w   = np.abs(np.random.normal(0, sigma, n))
reg_v   = np.abs(np.random.normal(0, sigma, (n, k)))

for epoch in range(num_epochs):
    for batch in range(int(X_train.shape[0]/batch_size)):

        eval(epoch, batch, X_train, y_train, X_test, y_test, model, params=[w_0, w, v])

        delta_w_0 = np.zeros(batch_size)
        delta_w   = np.zeros((n, batch_size))
        delta_v   = np.zeros((n, k, batch_size))
        for it in range(batch_size):
            x = X_train[batch * batch_size + it]
            y = y_train[batch * batch_size + it]
            # w_0
            delta_w_0[batch] = loss_grad_w_0(x, y, w_0, w, v, reg_w_0, reg_w, reg_v)

            # w_i
            for i in range(w.shape[0]):
                if x[i] != 0:
                    delta_w[i][batch] = loss_grad_w_i(x, y, w_0, w, v, i, reg_w_0, reg_w, reg_v)

                    # v_{i,f}
                    for j in range(v.shape[1]):
                        delta_v[i][j][batch] = loss_grad_v_i_f(x, y, w_0, w, v, i, j, reg_w_0, reg_w, reg_v)
            
        VERBOSE = False
        if VERBOSE:
            print('')
            print('y', y, 'x', x)
            print('d_w0', delta_w_0)
            print('w0', w_0)
            print('d_w\n', delta_w)
            print('w\n', w)
            print('d_v\n', delta_v)
            print('v\n', v)
            print('')

        w -= eta * np.mean(delta_w_0)
        for i in range(w.shape[0]):
            w[i] -= eta * np.mean(delta_w[i])
            pass
            for j in range(v.shape[1]):
                v[i][j] -= eta * np.mean(delta_v[i][j])
                pass

print('train:%d test:%d' % (len(y_train), len(y_test)))
