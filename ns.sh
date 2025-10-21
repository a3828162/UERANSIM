# 建立名為 ue0 的 netns
sudo ip netns add ue0

# 把 tun interface 移進 netns
sudo ip link set uesimtun0 netns ue0

# 在 netns 中設定 IP 與啟用網卡
sudo ip netns exec ue0 ip addr add 10.60.0.3/24 dev uesimtun0
sudo ip netns exec ue0 ip link set uesimtun0 up

# 設定 default route
sudo ip netns exec ue0 ip route add default dev uesimtun0