from tree import E
import traceback


def gt():
    q = traceback.format_stack()  # get trace
    q = q[:-2]  # remove repeated theme
    r = []
    for e in q:
        e = e.split('\n')
        e[0] = e[0].strip()
        e[1] = e[1].strip()
        line = e[0].split('line ')[1].split(',')[0]
        func = e[0].split('in ')[1]
        r = ['%4s:%15s > %s' % (
            line,
            func,
            e[1]
        )] + r
    return '\n'.join(r)


class AE:
    # e -- порождающий элемент дерева
    # value -- рабочее значение / лямбда для функций
    # t -- тип для анализа
    # type -- тип данных / возвращаемого значения
    # isConst* -- значение константно в данном узле (3 + 5 * 6)
    # args* -- имена аргументов функции
    # typeargs* -- типы аргументов функций или None до первого вызова
    # called* -- статистика вызовов функции по узлам, из которых она вызвана
    # n* -- имя переменной
    # typeret* -- тип возвращенного функцией значения

    # created -- все объекты, созданные через create()

    # ДВ -- дерево вызовов

    def __init__(self):
        self.created = []

    # Поиск полей по ДВ
    def __copyfind_one(self, f):
        if f in self.__dict__:
            return self.__dict__[f]
        if 'cpd' not in self.__dict__:
            return None
        return self.cpd[0].__copyfind_one(f)

    def __copyfind_all(self):
        for k in ['e', 'value', 'type', 'n']:
            v = self.__copyfind_one(k)
            if v is not None:
                self.__dict__[k] = v

    def copyfind(self):
        for e in self.created:
            e.__copyfind_all()

    # Присвоение узлам синтаксического дерева узлы ДВ
    def __walk_2e(self):
        if 'e' not in self.__dict__:
            raise AError('Cannot find tree element for that', self)
        if 'AE' not in self.e.__dict__:
            self.e.AE = []
        self.e.AE.append(self)
        if 'cpd' not in self.__dict__:
            return
        [v.__walk_2e() for v in self.cpd]

    def walk_2e(self):
        [v.__walk_2e() for v in self.created]

    # Создать новый узел ДВ (в "3 + 4" это будут "3" и "4")
    def create(self):
        v = AE()
        v.created = self.created
        v.trace = gt()
        # Отладка (здесь будет пауза в исполнении)
        # pdb.set_trace()
        self.created.append(v)
        return v

    # Создает производный узел ДВ (в "3 + 4" это будет значение "7")
    def copy(self, el=None):
        v = AE()
        for k in self.__dict__:
            if k == 'cpd':
                continue
            v.__dict__[k] = self.__dict__[k]
        if el is None:
            if 'cpd' not in self.__dict__:
                self.cpd = []
            self.cpd.append(v)
        else:
            v.e = el
            self.created.append(v)
        v.trace = gt()
        return v

    # Создать узел ДВ по определенному типу данных
    def gettype(t):
        v = AE()
        v.type = t
        v.t = 'const'
        v.value = None
        return v

    # Создает копию с указанным типом. Проверки нет
    def cast(self, t):
        v = self.copy()
        v.type = t.type
        if v.type == 'bool':
            v.value = bool(self.value)
        if v.type == 'int':
            v.value = int(self.value)
        return v

    # Парсит value, определяя, int это или float
    def floint(self, el):
        v = self.copy()
        try:
            v.value = float(v.value)
        except ValueError:
            raise AError('Cannot parse number', el)
        if v.value == int(v.value):
            v.value = int(v.value)
            v.type = 'int'
        else:
            v.type = 'float'
        return v

    # Строковое представление типа
    def strtype(v):
        if v is None:
            return '?'
        res = ''
        if v.t == 'func':
            res += 'function<'
            res += AE.strtype(v.typeret)
            res += '('
            args = []
            for i in range(len(v.args)):
                args.append(
                    '¿' if v.typeargs is None else AE.strtype(v.typeargs[i])
                )
            res += ','.join(args)
            res += ')>'
        else:
            res += (v.type if 'type' in v.__dict__ else '?')
        return res

    # Для логирования
    def __str__(self):
        if 'cpd' in self.__dict__:
            s = ', '.join(str(e) for e in self.cpd)
            s = '=> (%s)' % s
            s = '%d copies' % len(self.cpd)
        else:
            s = '0 copies'
        return '%s %s = %s\n%s\n%s\n%s' % (
            self.type if 'type' in self.__dict__ else '?',
            repr(self.n) if 'n' in self.__dict__ else '?',
            str(self.value) if 'value' in self.__dict__ else '?',
            s,
            str(self.e) if 'e' in self.__dict__ else '?',
            self.trace if 'trace' in self.__dict__ else '?'
        )


class AError(Exception):
    # Поддержка трейса по синтаксическому дереву
    def __init__(self, s, el, stack=None):
        self.s = s
        self.el = el
        if stack is None:
            self.stack = [el]
        else:
            self.stack = stack

    def __str__(self):
        s = []
        for e in self.stack:
            se = str(e)
            if len(se) > 150:
                se = se[:150] + '...'
            s.append(se)
        return '!!!!!\n%s\nE >\n%s\nStacktrace >\n%s' % (
            self.s,
            str(self.el),
            '\n---\n'.join(s)
        )


# Проверяет, можно ли узел t1 прикастовать к типу узла t2
def casteable(t1, t2):
    if t1.type == 'int' and t2.type == 'float':
        return True
    return False


# Подгон t2 под тип t1
# При неудаче -- ошибка по el
def match_cast(t1, t2, el):
    if t1 is None:
        return (t2, t2)
    if not isinstance(t1, AE):
        raise Exception('What is t1? > %s' % str(t1))
    if not isinstance(t2, AE):
        raise Exception('What is t2? > %s' % str(t2))
    if t1.type == t2.type:
        return (t1, t2)
    if casteable(t2, t1):
        return (t1, t2.cast(t1))
    if casteable(t1, t2):
        return (t1.cast(t2), t2)
    raise AError("Cannot cast %s (%s) to %s (%s)" % (
        t2.strtype(), str(t2.value),
        t1.strtype(), str(t2.value)
    ))


# Вывод статистики в отдельном окне
def tree_stat(stat, el):
    from tkinter import Tk, ttk
    app = Tk()
    app.title('Stat tree')
    tree = ttk.Treeview(app, height=30)
    style = ttk.Style()
    style.configure('Treeview', font='TkFixedFont')
    tree['columns'] = ('#0')
    tree.column('#0', width=1000, minwidth=1000)
    mv = tree.insert('', 1, text='Stat trace')
    me = tree.insert('', 2, text='Syntax tree')

    def add_v(p, v):
        txt = str(v).split('\n')
        e = tree.insert(p, 'end', text=txt[0])
        d = tree.insert(e, 'end', text='Full')
        for txtl in txt:
            tree.insert(d, 'end', text=txtl)
        if 'cpd' in v.__dict__:
            cpd = tree.insert(e, 'end', text='Copies')
            for cpdl in v.cpd:
                add_v(cpd, cpdl)
        if v.t == 'func':
            fs = tree.insert(e, 'end', text='Func stat')
            fsargs = tree.insert(fs, 'end', text='Args')
            for i in range(len(v.args)):
                fsarg = tree.insert(fsargs, 'end', text=(
                    '?' if v.args[i] is None else str(v.args[i])
                ))
                if v.typeargs is not None and v.typeargs[i] is not None:
                    add_v(fsarg, v.typeargs[i])
            if v.typeret is not None:
                fsret = tree.insert(fs, 'end', text='Ret type')
                add_v(fsret, v.typeret)

    def add_e(p, el):
        txt = str(el).split('\n')
        txtl = repr(el)
        if len(txtl) > 50:
            txtl = txtl[:50] + '...'
        e = tree.insert(p, 'end', text=txtl)
        d = tree.insert(e, 'end', text='Full')
        for txtl in txt:
            tree.insert(d, 'end', text=txtl)
        if not isinstance(el, E):
            return
        if 'AE' in el.__dict__:
            vt = el.AE[0].strtype()
            print('Find type >', vt)
            tree.insert(e, 'end', text=vt)
            vs = tree.insert(e, 'end', text='Stat')
            [add_v(vs, v) for v in el.AE]
        if 'args' in el.__dict__:
            es = tree.insert(e, 'end', text='Args')
            [add_e(es, e) for e in el.args]

    for v in stat.created:
        add_v(mv, v)
    add_e(me, el)
    tree.pack()
    app.mainloop()


# Точка входа в синтаксическое дерево
def walk(el, is_GUI=True):
    stat = AE()  # Создаем ДВ
    walk_exc(el, [], stat)  # Начинаем обходить
    stat.copyfind()
    stat.walk_2e()
    if is_GUI:
        tree_stat(stat, el)


# Обход узла ДВ с перехватом ошибки (для заполнения трейса)
def walk_exc(el, vars, stat):
    try:
        v = walk_noexc(el, vars, stat)
    except AError as e:
        e.stack.append(el)
        raise
    except Exception as e:
        raise AError(str(e), el)
    if isinstance(v, AE):
        return v
    raise AError('Unknown return ' + str(v), el)


# Обход узла apply
def walk_t_apply(el, vars, stat):
    if isinstance(el[0], E) and el[0].v in E.OPERATORS:
        if el[0].v == '⊧':
            if len(el.args) != 2:
                raise AError('Wrong count of args', el)
            v = walk_exc(el[1], vars, stat)
            v = match_cast(AE.gettype('bool'), v, el)[1]
            if not v.value:
                raise AError('Assert error', v.e)
            return v
        raise AError('Unsupported operator', el)
    if isinstance(el[0], AE):
        varsf = [el[0]]
    else:
        # Поиск в объявленных
        varsf = [v for v in vars if v.n == el[0]]
    if len(varsf) == 0:  # Не нашли
        raise AError('No find function for call', el)
    f = varsf[-1]  # Последняя в стеке
    # Количество ожидаемых аргументов
    fvc = len(f.args) if f.t == 'func' else 0
    elvc = len(el) - 1  # Количество поданных аргументов
    if elvc == 0:  # Функция как переменная
        return f
    elif elvc > 0 and fvc == 0:  # Переменная как функция
        raise AError('Call zero-args function', el)
    elif elvc != fvc:  # Количество аргументов не совпало
        raise AError('Wrong count of parameters', el)
    vs = [walk_exc(e, vars, stat) for e in el[1:]]  # Идем по аргументам
    if f.typeargs is None:  # Еще не определили типы
        f.typeargs = vs[:]  # Определяем
    # Ищем индексы неприкастованных аргументов
    for i in range(len(vs)):
        try:
            (f.typeargs[i], vs[i]) = match_cast(f.typeargs[i], vs[i], el)
        except AError as e:
            e.s += ' (for arg %d)' % (i + 1)
            raise
    # Запоминаем вызвавший узел и количество вызовов с этого узла
    ci = [i for i in range(len(f.called[0])) if f.called[0][i] is el]
    if len(ci) == 0:
        f.called[0].append(el)
        f.called[1].append(1)
    else:
        f.called[1][ci[0]] += 1
    # Выставляем аргументы
    for i in range(len(vs)):
        vs[i] = vs[i].copy()
        vs[i].n = f.args[i]
    v = f.value(vars + vs, stat)  # Идем в функцию
    # Обрабатываем возвращенный тип
    try:
        (f.typeret, v) = match_cast(f.typeret, v, el)
    except AError as e:
        e.s += ' (in return)'
        raise
    return v.copy(el)  # Возвращаем результат


# Обход узла series
def walk_t_series(el, vars, stat):
    v = stat.create()
    v.e = el
    v.t = 'func'
    v.typeargs = None
    v.typeret = None
    v.type = 'func'
    v.args = [None]
    v.called = [[], []]
    if el[0] == 'recN':
        v.dict = [
            (
                [walk_exc(di, vars, stat) for di in d[0]],
                walk_exc(d[1], vars, stat)
            ) for d in el[1]
        ]
        v.args = el[2]
        v.stacksize = 0
        OVERREC = 100

        def vl(lvars, lstat):
            lv = lvars[-len(v.args):]
            ld = [d for d in v.dict if len([
                i for i in range(len(v.args)) if lv[i].value == d[0][i].value
            ]) == len(v.args)]
            if len(ld) > 1:
                raise AError('Multiple rec variants', el)
            if len(ld) == 1:
                return ld[0][1]
            v.stacksize += 1
            if v.stacksize > OVERREC:
                raise AError('Recursion over %d times\n%s' % (
                    OVERREC,
                    '\n'.join(str(e).split('\n')[0] for e in lvars)
                 ), el)
            nv = walk_exc(el[3], lvars, lstat)
            v.stacksize -= 1
            v.dict.append((lv, nv))
            return nv

        v.value = vl
        return v
    if el[0] == 'mapN':
        if len(el[2]) != len(el[4]):
            raise AError('Broken map', el)
        v.dict = [
            walk_exc(d, vars, stat)
            for d in el[4]
        ]
        cnt = -1
        for f in v.dict:
            if cnt < 0:
                cnt = len(f.args)
            else:
                if cnt != len(f.args):
                    raise AError('Diff count of args in mapped funcs', el)
        v.args = [None for i in range(cnt)]

        def vl(lvars, lstat):
            lv = lvars[-len(v.args):]
            lf = [
                walk_t_apply(E.func('`apply', [f] + lv), lvars, lstat).copy()
                for f in v.dict
            ]
            for i in range(len(lf)):
                lf[i].n = el[2][i]
            return walk_exc(el[3], lvars + lf, lstat)

        v.value = vl
        return v
    if el[0] == 'genN':
        v.dict = {}
        v.typeargs = [AE.gettype('int')]
        v.dictm = [0, 0, -1, 1]
        v.dictm[0] = stat.create()
        v.dictm[0].e = el
        v.dictm[0].value = 0
        v.dictm[0].t = 'const'
        v.dictm[0].type = 'int'
        v.dictm[1] = v.dictm[0].copy()
        if el[4] is None:
            v.dictf = None
        else:
            v.dictf = walk_exc(el[4], vars, stat)
        OVERITER = 1000

        def findnext(lvars, lstat, d):
            i = 0
            lv = v.dictm[1 if d else 0]
            while True:
                if v.dictf is None:
                    fv = lv
                else:
                    fv = walk_t_apply(
                        E.func('`apply', [v.dictf, lv]),
                        lvars,
                        lstat
                    )
                # TODO handle None?
                fv = fv.copy()
                fv.n = el[2]
                rv = walk_exc(el[3], lvars + [fv], lstat)
                rv = match_cast(AE.gettype('bool'), rv, el)[1]
                lv.value += 1 if d else -1
                if rv.value:
                    v.dict[v.dictm[3 if d else 2]] = fv
                    v.dictm[3 if d else 2] += 1 if d else -1
                    return
                i += 1
                if i > OVERITER:
                    raise AError('Over %d iterations for %s duration' % (
                        OVERITER,
                        'right' if d else 'left'
                     ), el)

        def vl(lvars, lstat):
            lv = match_cast(AE.gettype('int'), lvars[-1], el)[1].value
            if lv == 0:
                lv = 1
            while lv not in v.dict:
                findnext(lvars, lstat, 1 if lv > 0 else -1)
            return v.dict[lv]

        v.value = vl
        return v
    if el[0] == 'arrN':
        v.typeargs = [AE.gettype('int')]
        v.dict = [
            walk_exc(e, vars, stat)
            for e in el[3]
        ]

        def vl(lvars, lstat):
            lv = match_cast(AE.gettype('int'), lvars[-1], el)[1].value
            if lv < 0 or lv >= len(v.dict):
                raise AError(
                    'Overflow arr[%d] index %d' % (len(v.dict), lv),
                    el
                )
            return v.dict[lv]

        v.value = vl
        return v
    raise AError('Unsupported `series', el)


# Обход бинарных функций
def walk_t_biops(el, vars, stat, args=None):
    if args is None:
        if len(el.args) < 2:
            raise AError('Broken biop', el)
        v = walk_t_biops(el, vars, stat, el.args[:])
        return v.copy(el)
    func = {
        '+': lambda a, b: a + b,
        '*': lambda a, b: a * b,
        '^': lambda a, b: pow(a, b),
        '≡': lambda a, b: a == b,
        '>': lambda a, b: a > b,
        '<': lambda a, b: a < b,
        '-': lambda a, b: a - b,
        '∨': lambda a, b: a or b,
        '/': lambda a, b: a / b,
        '≥': lambda a, b: a >= b
    }.get(el.v)
    if func is None:
        return None
    n_args = args[:2]
    n_args = [
        walk_exc(e, vars, stat) if isinstance(e, E) else e
        for e in n_args
    ]
    n_args = match_cast(n_args[0], n_args[1], el)
    v = n_args[0].copy()
    v.value = func(n_args[0].value, n_args[1].value)
    if el.v in ['≡', '>', '<', '∨', '≥']:
        v.type = 'bool'
    if len(args) == 2:
        return v
    return walk_t_biops(el, vars, stat, [v] + args[2:])


# Обход cases
def walk_t_cases(el, vars, stat):
    q = [e[1] for e in el[:-1]]
    id = -1
    for i in range(len(q)):
        v = walk_exc(q[i], vars, stat)
        v = match_cast(AE.gettype('bool'), v, el)[1]
        if v.value:
            id = i
            break
    if id < 0:
        return walk_exc(el[-1], vars, stat)
    else:
        return walk_exc(el[id][0], vars, stat)


# Общий обход узла без перехвата ошибок
def walk_noexc(el, vars, stat):
    if isinstance(el, AE):
        return el
    if type(el) != E:
        raise AError('Not a tree element', el)
    if el.t == 'number':
        v = stat.create()
        v.e = el
        v.t = 'const'
        v.value = el.v
        v.isConst = True
        return v.floint(el)
    if el.t != 'f':
        raise AError('Unexpected type', el)
    if el.v == ';':
        subvars = vars[:]
        for e in el[:-1]:
            walk_exc(e, subvars, stat)
        return walk_exc(el[-1], subvars, stat).copy(el)
    if el.v == '`repl':
        if len(el.args) == 4:
            walk_exc(el[3], vars, stat)
        if len(el[1]) > 0:
            v = stat.create()
            v.e = el
            v.t = 'func'
            v.typeargs = None
            v.typeret = None
            v.type = 'func'
            v.args = el[1]
            v.value = lambda lvars, lstat: walk_exc(el[2], lvars, lstat)
            v.called = [[], []]
        else:
            v = walk_exc(el[2], vars, stat).copy(el)
        v.n = el[0]
        vars.append(v)
        return v
    if el.v == '`apply':  # Вызов функции / обращение к переменной
        return walk_t_apply(el, vars, stat)
    if el.v == '`series':
        return walk_t_series(el, vars, stat)
    if el.v == '`err':
        raise AError('Parse tree error', el)
    if el.v == '`cases':
        return walk_t_cases(el, vars, stat)
    v = walk_t_biops(el, vars, stat)
    if v is not None:
        return v
    if el.v == '‖':
        v = walk_exc(el[0], vars, stat)
        if v.type not in ['float', 'int']:
            raise AError('Unsupported type', el)
        v = v.copy()
        v.value = abs(v.value)
        return v
    raise AError('Unknown function', el)
