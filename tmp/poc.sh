#! /bin/bash

westpe_pid=`sudo docker inspect -f '{{.State.Pid}}' WestP`
west_pid=`sudo docker inspect -f '{{.State.Pid}}' West`
north_pid=`sudo docker inspect -f '{{.State.Pid}}' North`
east_pid=`sudo docker inspect -f '{{.State.Pid}}' East`
south_pid=`sudo docker inspect -f '{{.State.Pid}}' South`
eastpe_pid=`sudo docker inspect -f '{{.State.Pid}}' EastP`

# All nodes in the network
westpe=$westpe_pid
west=$west_pid
north=$north_pid
east=$east_pid
eastpe=$eastpe_pid
south=$south_pid

sudo mkdir -p /var/run/netns
sudo ln -s /proc/$westpe/ns/net /var/run/netns/$westpe
sudo ln -s /proc/$west/ns/net /var/run/netns/$west
sudo ln -s /proc/$north/ns/net /var/run/netns/$north
sudo ln -s /proc/$east/ns/net /var/run/netns/$east
sudo ln -s /proc/$eastpe/ns/net /var/run/netns/$eastpe
sudo ln -s /proc/$south/ns/net /var/run/netns/$south

### Bridges
echo 'Configuring bridges...'
sudo brctl addbr ww
sudo brctl addbr wn
sudo brctl addbr we
sudo brctl addbr ws
sudo brctl addbr ne
sudo brctl addbr ns
sudo brctl addbr ee
sudo brctl addbr es

sudo ip link set dev ww up
sudo ip link set dev wn up
sudo ip link set dev we up
sudo ip link set dev ws up
sudo ip link set dev ne up
sudo ip link set dev ns up
sudo ip link set dev ee up
sudo ip link set dev es up

echo 'Bridges have been configured!'

### WestPE
echo 'Configuring WestPE...'

## Loopback
sudo ip link add hwestpelo type veth peer name wpelo
sudo ip link set hwestpelo up

sudo ip link set wpelo netns $westpe
sudo ip netns exec $westpe ip link set wpelo up
sudo ip netns exec $westpe ip addr add 192.168.0.1/32 dev wpelo

## Customer's prefixes
sudo ip link add hwestpecustomer type veth peer name westpe-eth2
sudo ip link set hwestpecustomer up

sudo ip link set westpe-eth2 netns $westpe
sudo ip netns exec $westpe ip link set westpe-eth2 up
sudo ip netns exec $westpe ip addr add 192.168.10.0/24 dev westpe-eth2

## eth1
sudo ip link add hwestpe-eth1 type veth peer name westpe-eth1
sudo brctl addif ww hwestpe-eth1
sudo ip link set hwestpe-eth1 up

sudo ip link set westpe-eth1 netns $westpe
sudo ip netns exec $westpe ip link set westpe-eth1 up
sudo ip netns exec $westpe ip addr add 10.10.10.30/30 dev westpe-eth1

echo 'West PE has been configured!'

### West
echo 'Configuring West...'

## eth1
sudo ip link add hwest-eth1 type veth peer name west-eth1
sudo brctl addif ws hwest-eth1
sudo ip link set hwest-eth1 up

sudo ip link set west-eth1 netns $west
sudo ip netns exec $west ip link set west-eth1 up
sudo ip netns exec $west ip addr add 10.10.10.26/30 dev west-eth1

## eth2
sudo ip link add hwest-eth2 type veth peer name west-eth2
sudo brctl addif we hwest-eth2
sudo ip link set hwest-eth2 up

sudo ip link set west-eth2 netns $west
sudo ip netns exec $west ip link set west-eth2 up
sudo ip netns exec $west ip addr add 10.10.10.14/30 dev west-eth2

## eth3
sudo ip link add hwest-eth3 type veth peer name west-eth3
sudo brctl addif wn hwest-eth3
sudo ip link set hwest-eth3 up

sudo ip link set west-eth3 netns $west
sudo ip netns exec $west ip link set west-eth3 up
sudo ip netns exec $west ip addr add 10.10.10.2/30 dev west-eth3

## eth4
sudo ip link add hwest-eth4 type veth peer name west-eth4
sudo brctl addif ww hwest-eth4
sudo ip link set hwest-eth4 up

sudo ip link set west-eth4 netns $west
sudo ip netns exec $west ip link set west-eth4 up
sudo ip netns exec $west ip addr add 10.10.10.29/30 dev west-eth4

echo 'West has been configured!'

### North
echo 'Configuring North...'

## eth1
sudo ip link add hnorth-eth1 type veth peer name north-eth1
sudo brctl addif wn hnorth-eth1
sudo ip link set hnorth-eth1 up

sudo ip link set north-eth1 netns $north
sudo ip netns exec $north ip link set north-eth1 up
sudo ip netns exec $north ip addr add 10.10.10.1/30 dev north-eth1

## eth2
sudo ip link add hnorth-eth2 type veth peer name north-eth2
sudo brctl addif ns hnorth-eth2
sudo ip link set hnorth-eth2 up

sudo ip link set north-eth2 netns $north
sudo ip netns exec $north ip link set north-eth2 up
sudo ip netns exec $north ip addr add 10.10.10.5/30 dev north-eth2

## eth3
sudo ip link add hnorth-eth3 type veth peer name north-eth3
sudo brctl addif ne hnorth-eth3
sudo ip link set hnorth-eth3 up

sudo ip link set north-eth3 netns $north
sudo ip netns exec $north ip link set north-eth3 up
sudo ip netns exec $north ip addr add 10.10.10.9/30 dev north-eth3

echo 'North has been configured!'

### East
echo 'Configuring East...'

## eth1
sudo ip link add heast-eth1 type veth peer name east-eth1
sudo brctl addif ne heast-eth1
sudo ip link set heast-eth1 up

sudo ip link set east-eth1 netns $east
sudo ip netns exec $east ip link set east-eth1 up
sudo ip netns exec $east ip addr add 10.10.10.10/30 dev east-eth1

## eth2
sudo ip link add heast-eth2 type veth peer name east-eth2
sudo brctl addif we heast-eth2
sudo ip link set heast-eth2 up

sudo ip link set east-eth2 netns $east
sudo ip netns exec $east ip link set east-eth2 up
sudo ip netns exec $east ip addr add 10.10.10.13/30 dev east-eth2

## eth3
sudo ip link add heast-eth3 type veth peer name east-eth3
sudo brctl addif es heast-eth3
sudo ip link set heast-eth3 up

sudo ip link set east-eth3 netns $east
sudo ip netns exec $east ip link set east-eth3 up
sudo ip netns exec $east ip addr add 10.10.10.17/30 dev east-eth3

## eth4
sudo ip link add heast-eth4 type veth peer name east-eth4
sudo brctl addif ee heast-eth4
sudo ip link set heast-eth4 up

sudo ip link set east-eth4 netns $east
sudo ip netns exec $east ip link set east-eth4 up
sudo ip netns exec $east ip addr add 10.10.10.21/30 dev east-eth4

echo 'East has been configured!'

### EastPE
echo 'Configuring EastPE...'

## Loopback
sudo ip link add heeastpelo type veth peer name epelo
sudo ip link set heeastpelo up

sudo ip link set epelo netns $eastpe
sudo ip netns exec $eastpe ip link set epelo up
sudo ip netns exec $eastpe ip addr add 192.168.0.2/32 dev epelo

## Customer's prefixes
sudo ip link add heastpecustomer type veth peer name eastpe-eth2
sudo ip link set heastpecustomer up

sudo ip link set eastpe-eth2 netns $eastpe
sudo ip netns exec $eastpe ip link set eastpe-eth2 up
sudo ip netns exec $eastpe ip addr add 192.168.11.0/24 dev eastpe-eth2

## eth1
sudo ip link add heastpe-eth1 type veth peer name eastpe-eth1
sudo brctl addif ee heastpe-eth1
sudo ip link set heastpe-eth1 up

sudo ip link set eastpe-eth1 netns $eastpe
sudo ip netns exec $eastpe ip link set eastpe-eth1 up
sudo ip netns exec $eastpe ip addr add 10.10.10.22/30 dev eastpe-eth1

echo 'EastPE has been configured!'

### South
echo 'Configuring South...'

## eth1
sudo ip link add hsouth-eth1 type veth peer name south-eth1
sudo brctl addif es hsouth-eth1
sudo ip link set hsouth-eth1 up

sudo ip link set south-eth1 netns $south
sudo ip netns exec $south ip link set south-eth1 up
sudo ip netns exec $south ip addr add 10.10.10.18/30 dev south-eth1

## eth2
sudo ip link add hsouth-eth2 type veth peer name south-eth2
sudo brctl addif ns hsouth-eth2
sudo ip link set hsouth-eth2 up

sudo ip link set south-eth2 netns $south
sudo ip netns exec $south ip link set south-eth2 up
sudo ip netns exec $south ip addr add 10.10.10.6/30 dev south-eth2

## eth3
sudo ip link add hsouth-eth3 type veth peer name south-eth3
sudo brctl addif ws hsouth-eth3
sudo ip link set hsouth-eth3 up

sudo ip link set south-eth3 netns $south
sudo ip netns exec $south ip link set south-eth3 up
sudo ip netns exec $south ip addr add 10.10.10.25/30 dev south-eth3

echo 'South has been configured!'
