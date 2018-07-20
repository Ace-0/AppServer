# coding=utf-8
"""The entrance of the whole project."""

import sys
import getopt
from app import create_app

if __name__ == '__main__':
    config_name = 'development'
    port = 10086
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'm:p:')
    except getopt.GetoptError:
        print('Usage: python run.py -m <mode> -p <port>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-m':
            config_name = arg
        elif opt == '-p':
            port = int(arg)

    app = create_app(config_name)

    app.run(host=app.config.get('HOST'), port=port)
