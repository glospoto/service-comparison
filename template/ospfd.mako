!
hostname ospfd
password zebra
enable password zebra
!
router ospf
! Speak OSPF on all interfaces falling in the listed subnets
% for subnet in subnets:
network ${subnet} area 0.0.0.0
% endfor

% if loopback is not None:
network ${loopback} area 0.0.0.0
% endif

redistribute connected
!
!log file /var/log/zebra/ospfd.log
!
