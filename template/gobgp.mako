[global.config]
  as = 1
  router-id = "${my_loopback_address}"
% for peer_loopback_address in peer_loopback_addresses:
[[neighbors]]
  [neighbors.config]
    neighbor-address = "${peer_loopback_address}"
    peer-as = 1
    [neighbors.transport.config]
    local-address = "${my_loopback_address}"

[[neighbors.afi-safis]]
  [neighbors.afi-safis.config]
  afi-safi-name = "l2vpn-evpn"
% endfor

