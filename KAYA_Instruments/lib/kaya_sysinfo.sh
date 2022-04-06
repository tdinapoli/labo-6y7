#!/bin/bash

echo ============ system information: =======================
uname -a
echo =========== kernel driver status: ======================
systemctl -l status kaya_driver -n100
echo =========== system daemon status: ======================
systemctl -l status kaya_daemon -n100
