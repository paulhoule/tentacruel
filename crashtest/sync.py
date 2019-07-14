from sys import argv
from urllib.request import urlopen


def main() -> None:
    """
    Main method of command line-program.  Creates event loop and then runs amain() in it

    :return: nothing
    """
    data = urlopen(argv[1]).read()
    print(data.decode())

if __name__ == '__main__':
    main()