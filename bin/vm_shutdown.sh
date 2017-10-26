#!/usr/bin/expect -f
spawn ssh kevin@192.168.86.210
expect "assword:"
send "BHt2incottwo\r"
interact