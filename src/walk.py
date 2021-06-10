import random
from scipy.special import comb, perm

def walk():
    n=5
    time = int(2.4**n)
    start = 0
    for i in range(time):
        if start==n:
            continue
        target = random.randint(0,2)
        if start>=0:
            if target==0:
                start+=1
            else:
                start-=1
        else:
            if target==0:
                start-=1
            else:
                start+=1
    print(start)

def foo(t, n):
    k=int((t-n)/2)
    c=comb(t,k)
    return c / 3**t * 2**k

def cal(t,n):
    a = comb(t,(t+n)/2)/ 3**t * 2**((t-n)/2)
    b = 2**(-n)
    return a,b,a/b

n=10
print(cal(100,20))