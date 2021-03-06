#!/bin/sh
cd ..
mkdir -p build
cd build
# cmake ..
# make -j8
objcopy -O binary --only-section=.rodata pilorastubbed pilorastubbed.rodata
rm -f spawner
ln -s _deps/logless-build/spawner .
mkdir -p rx
cd rx
rm log.bin
touch log.bin
pkill -9 binstub
pkill -9 spawner
../pilorastubbed --channel=1 --cx=127.0.0.1:2000 --rx=127.0.0.1:3000 --carrier=433000000 --bandwidth=500 --coding-rate=4/5 --spreading-factor=SF7 --reset-pin=33 --txrx-done-pin=32 &
../spawner ../pilorastubbed.rodata log.bin noexiteof