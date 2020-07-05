#!/bin/bash

## Restart BMC and then verify that HTTP server is up
export H="${1}"
echo "Hit ctl+c to exit"

bmc-device -u admin -p admin --verbose -h ${H} --cold-reset
echo "Power cycled the BMC, will loop through http checks"
sleep 30
while true; do
  C=$(curl  --connect-timeout 1 -s -o /dev/null -w  "%{http_code}" ${H})
  if [[ ${C} -lt 200 || ${C} -gt 400 ]]; then
    echo -n "."
    sleep 2
  else
    echo
    echo "Got a HTTP code of ${C} to http://${H}, reset is done."
    exit 0
  fi
done

