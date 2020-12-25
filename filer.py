import os
from tree import create
from translator import cody, PbTranslatorError, Unclosure


def unclosuring(t, s):
    if t == 'py':
        s = Unclosure.bind(s)
    return s


def trr_typed(t, f):
    return lambda _, s, n: cody(s, t, f, n)


def trr_inbuilt():
    return lambda t, s, n: cody(s, 'py', 'generators/%s.py' % t, n)


def walk(fld, trr=None):
    print('Start translating for <%s>...' % fld)
    if trr is None:
        trr = trr_inbuilt()
    elif type(trr) == tuple:
        trr = trr_typed(trr[0], trr[1])
    cnt = 0
    for (p, _, fs) in os.walk(fld):
        for f in fs:
            fd = f.split('.')
            if fd[-1] != 'pb':
                continue
            fp = p + os.path.sep + f
            try:
                with open(fp, 'r', encoding='utf8') as fs:
                    s = fs.read()
            except UnicodeDecodeError:
                raise PbTranslatorError('File <%s> expected in utf8' % fp)
            s = create(s)
            s = unclosuring(fd[-2], s)
            s = trr(fd[-2], s, '_'.join(fd[:-2]))
            fp = p + os.path.sep + '.'.join(fd[:-1])
            with open(fp, 'w', encoding='utf8') as fs:
                fs.write(s)
                fs.write('\n')
            print('Created %s' % fp)
            cnt += 1
    print('Translate %d files' % cnt)
