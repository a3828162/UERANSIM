#/bin/sh

xhost +SI:localuser:ubuntu

# 開啟chrome 
DISPLAY=:0 google-chrome --new-window http://192.168.56.50:18080 > /dev/null 2>&1 &

# 模擬手動關閉連線來觸發送出close訊號
xdotool search --name "WebRTC Video Stream" windowactivate --sync key Alt+F4

# 強制刪除chrome進程
pkill chrome