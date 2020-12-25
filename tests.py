from tree import create
from translator import cody, execute, Unclosure
from templator import apply
from filer import walk
from analyze import walk as anal_walk
# from view import latex2png


def fastExec(s):
    s = create(s)
    s = Unclosure.bind(s)
    # print(s)
    s = cody(s, 'py', 'generators/py.py')
    print('-' * 20)
    print(s)
    s = execute(s)
    s = s()
    print('-' * 20)
    print(s)
    return s


def run_jsserver():
    import jsserver
    jsserver.run()


def pb_py_test(cfn=None):
    import os
    [(_, _, fns)] = [i for i in os.walk('pbtests')]
    ignored = ['consty.pb', 'json.pb']
    for fn in fns:
        if cfn is not None and cfn != fn:
            continue
        if fn in ignored:
            continue
        with open(os.path.join('pbtests', fn), 'r', encoding='utf8') as f:
            s = f.read()
        print('Test file <%s>' % fn)
        try:
            fastExec(s)
        except Exception:
            raise Exception('Error with file <%s>' % fn)


def test_all():
    pb_py_test()
    test_templator()
    test_code_injects()
    test_filer()
    test_js_oneline_func()
    test_types_classic()
    test_types_series()
    print('>>> ALL TESTS PASSED <<<')


def test_templator():
    src = create(r"?(\text{a}) + ?(\text{b})")[0]
    dst = create(r"?(\text{a}) * 2 - ?(\text{b})")[0]
    eqn1 = create(r"""
    f(x) = x * (3 + \text{hello world}) - (6+(3*x)^2);
    f(10)
    """)
    eqn2 = create(r"""
    f(x) = x * (3 * 2 - \text{hello world}) - (6 * 2 - (3*x)^2);
    f(10)
    """)
    eqn1 = apply(eqn1, src, dst)
    assert eqn1 == eqn2
    [eqn1, eqn2] = [cody(s, 'py', 'generators/latex.py') for s in [eqn1, eqn2]]
    assert eqn1 == eqn2


def test_code_injects():
    s = r"""
    \sin = \inject(\text{__import__('math').sin});
    v = \inject(\text{3}) + 1;
    \begin{cases}
        n_i = i
    \end{cases};
    n_3 = m_3;
    m_5 = \sin(10);
    m_3 + m_5 + v
    """
    s = fastExec(s)
    assert s == __import__('math').sin(10) + 3 + 3 + 1


def test_filer():
    import os
    import shutil
    fld = 'filer_tests'
    os.mkdir(fld)
    try:
        s = '1+2+3\n'
        fs = ['f.py.pb', 'f.js.pb']
        for f in fs:
            with open(os.path.sep.join((fld, f)), 'w', encoding='utf8') as f:
                f.write(s)
        walk(fld)
        for f in fs:
            f = '.'.join(f.split('.')[:-1])
            assert os.path.isfile(os.path.sep.join((fld, f)))
        err = None
    except Exception as e:
        err = e
    shutil.rmtree(fld)
    if err is not None:
        raise err


def test_js_oneline_func():
    s = r"""
    f(x,y,z) = \left\{ x, y, z \right\};
    g = \left\{ 1, 2, 3 \right\};
    f
    """
    s = create(s)
    s = cody(s, 'py', 'generators/js.py')
    print(s)
    assert s.find('(x,y,z){') >= 0


def test_types_classic():
    s = r"""
    f(a) = {
        b = a + 3;
        b - 4
    };
    a = 4 + 1.5;
    b = f(4);
    c = b + a + 0.5;
    b * 3
    """
    s = create(s)
    anal_walk(s, False)
    # all
    assert s.AE[0].strtype() == 'int'
    # f(a)
    assert s[0].AE[0].strtype() == 'function<int(int)>'
    # a
    assert s[1].AE[0].strtype() == 'float'
    # b
    assert s[2].AE[0].strtype() == 'int'
    # c
    assert s[3].AE[0].strtype() == 'float'


def test_types_series():
    s = r"""
    \begin{cases}
        f_0 = 2 \\
        f_1 = 3 \\
        f_n = f_{n-1} + f_{n-2}
    \end{cases};
    g = \left\{ e + 1 \mid e \in f \right\};
    h = \left\{ i \mid g(i) > 100 \right\};
    * = \models(g_{h_1} \equiv 145);
    q(a, b) = a + b;
    r(a, b) = a - b;
    w = \left\{ e + f + 0.5 \mid e \in q, f \in r \right\};
    * = \models(w(2,3) \equiv 4.5);
    0
    """
    s = create(s)
    anal_walk(s, False)
    assert s.AE[0].strtype() == 'int'
    # f
    assert s[0].AE[0].strtype() == 'function<int(int)>'
    # g
    assert s[1].AE[0].strtype() == 'function<int(int)>'
    # h
    assert s[2].AE[0].strtype() == 'function<int(int)>'
    # q
    assert s[4].AE[0].strtype() == 'function<int(int,int)>'
    # r
    assert s[5].AE[0].strtype() == 'function<int(int,int)>'
    # w
    assert s[6].AE[0].strtype() == 'function<float(int,int)>'


def test_consty():
    import os
    with open(os.path.join('pbtests', 'consty.pb'), 'r', encoding='utf8') as f:
        fd = f.read()
    s = create(fd)
    from consty import consty
    s = consty(s)
    print('-' * 10, 'CONSTY', '-' * 10)
    print(s)
    s = Unclosure.bind(s)
    s = cody(s, 'py', 'generators/py.py')
    s = execute(s)
    s = s()
    print(s)
    assert [s(i) for i in range(4)] == [6, 6, 11, 46]
    assert s(4)(4) == 7


# run_jsserver()
test_all()
