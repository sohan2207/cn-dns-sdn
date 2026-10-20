
from mininet.net import Mininet
from mininet.cli import CLI
import sys
import time


def main():
    net = Mininet(controller=None)

    net.addHost('h1', ip='10.0.0.1')
    net.addHost('h2', ip='10.0.0.2')
    net.addHost(
        'h3',
        ip='10.0.0.3',
        mac='00:00:00:00:00:03'
    )

    s1 = net.addSwitch(
        's1',
        failMode='standalone'
    )

    net.addLink('h1', s1)
    net.addLink('h2', s1)
    net.addLink('h3', s1)

    net.start()

    try:
        if '--no-cli' in sys.argv:
            print('Mininet topology is running.', flush=True)
            while True:
                time.sleep(1)
        else:
            CLI(net)
    finally:
        net.stop()


if __name__ == '__main__':
    main()
