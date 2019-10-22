# encoding: utf-8
import optparse

# 命令行参数定义
descriptions = {
    # option name: [help msg, type, default value]
    'cell-phone': ['cell phone to login greek time', str, None],
    'password': ['password to login greek time', str, None],
    'save-dir': ['directory to save pdf', str, None],
    'download-interval': ['interval of every request', int, 0]
}

# init options
parser = optparse.OptionParser()
for k, v in descriptions.items():
    default = v[2] if v[2] is not None else optparse.NO_DEFAULT
    parser.add_option('--{}'.format(k),
                      dest=k.replace('-', '_'),
                      default=default,
                      help=v[0],
                      type=v[1])
options, _ = parser.parse_args()
