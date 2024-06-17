#!/bin/bash
expect <<- DONE
spawn /Applications/Falcon.app/Contents/Resources/falconctl uninstall -t
expect "Falcon Maintenance Token:"
send -- $1
send -- "\r"
expect eof
DONE
