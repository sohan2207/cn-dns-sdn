from mininet.net import Mininet
from mininet.cli import CLI
from mininet.node import Controller

net = Mininet()
net.addController('c0')


net.addHost('h1',ip = '10.0.0.1')
net.addHost('h2',ip = '10.0.0.2')
net.addHost('h3', ip='10.0.0.3', mac='00:00:00:00:00:03')
s1 = net.addSwitch('s1')
net.addLink('h1','s1')
net.addLink('h2','s1')
net.addLink('h3','s1')

net.start()
CLI(net)
net.stop()