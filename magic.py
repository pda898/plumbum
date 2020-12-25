class E:
    def func(v, asd=[]):
        print('funcfunc', asd)
        return asd


a1 = E.func('*')
a1.append('test')
a2 = E.func('*')

assert a1 == a2  # yeah baby
