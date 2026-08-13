# E1608 frozen contract

Construct the exact signed Page 32 displacement sequence in generator order. For each of fifteen transitions calculate `(d[i+1]-d[i]) mod 29`; compare it positionwise with `(first rune of next block - last rune of current block) mod 29`. Under a Binomial(n=15,p=1/29) null, pass requires upper-tail p no greater than 0.01. No cyclic shift, sign flip, reverse order, alternate register, or neighboring rune is allowed.
