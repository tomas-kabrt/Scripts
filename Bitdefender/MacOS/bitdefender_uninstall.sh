#!/bin/bash

BITDEFENDER_PW='FILL_THE_UNINSTALL_PW'

if [ -e /Library/Bitdefender/AVP/product/bin/BDLDaemon ]; then
	sudo /Library/Bitdefender/AVP/product/bin/UninstallTool --password=${BITDEFENDER_PW}
	if [ $? -ne 0 ] ; then
		echo "Problem during uninstallation of Bitdefender"
		exit 1
	else
		echo "Bitdefender succesfully uninstalled"
	fi
else
    echo "Bitdender is not on the endpoint."
fi
