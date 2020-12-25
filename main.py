import sys


def main():
    if len(sys.argv) < 3:
        print('usage:\npython3 main.py filer <dir>\n')
        return
    if sys.argv[1] == 'filer':
        import filer
        filer.walk(sys.argv[2])
        return
    print('wrong args, run without args for help')


main()
