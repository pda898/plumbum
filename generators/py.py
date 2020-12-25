def case(el, cody, gen):
    gen('py', './all.py')
    gen('gn', './py.txt')
    if el.v == '`codywrap':
        return (
            'def %s():\n%s\n'
            % (el[1], '\n'.join('\t' + s for s in cody(el[0]).split('\n')))
        )
    if el.v == '`repl':
        cd = cody(el[2]).split('\n')
        if len(cd) > 1 or len(el[1]) > 0:
            if len(cd) == 1:
                cd = ['return %s' % cd[0]]
            cd = ['def %s(%s):' % (
                cody(el[0]),
                ','.join(cody(e) for e in el[1])
            )] + ['\t' + e for e in cd]
            if len(el[1]) == 0:
                cd.append('%s=%s()' % (
                    cody(el[0]),
                    cody(el[0])
                ))
        else:
            cd = ['%s=%s' % (
                cody(el[0]),
                cd[0]
            )]
        return '\n'.join(cd)
    if el.v == ';':
        if len(el.args) == 1:
            return cody(el[0])
        return'\n'.join(
            [cody(e) for e in el[:-1]]
            + ['return %s' % cody(el[-1])]
        )
    if el.v == '`cases':
        return '(%s%s)' % (
            ''.join('%s if %s else ' % (
                cody(e[0]),
                cody(e[1])
            ) for e in el[:-1]),
            cody(el[-1])
        )
