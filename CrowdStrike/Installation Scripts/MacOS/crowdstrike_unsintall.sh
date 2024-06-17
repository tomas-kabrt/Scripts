#!/bin/bash

INPUT_YOUR_TOKEN=''

if [ ! -x "/Applications/Falcon.app/Contents/Resources/falconctl" ] || [ -z "$(/Applications/Falcon.app/Contents/Resources/falconctl stats | grep 'Sensor operational: true')" ]; then
	# Uninstall Falcon Agent

	if [ -z "$INPUT_YOUR_TOKEN" ]; then
		echo "Uninstalling without security token"
	  sudo /Applications/Falcon.app/Contents/Resources/falconctl uninstall || exit 1
	else
		echo "Uninstalling with security token"
		sudo /Applications/Falcon.app/Contents/Resources/falconctl uninstall --maintenance-token ${INPUT_YOUR_TOKEN} || exit 1
	fi
	echo "Crowdstrike Falcon is uninstalled"
else
  echo "Crowdstrike Falcon is not on the endpoint"
fi
