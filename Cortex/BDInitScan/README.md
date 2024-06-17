# Bitdefender Initiate Endpoint Scan

This responder allows you to initiate a scan task on an endpoint via Bitdefender API. This is handy when you are dealing with alerts from Bitdefender and you want to validate that the endpoint doesn't contain any other malicious files.

## Pre-requisites

To initiate a scan via API, you need to have a unique identification of an endpoint. This responder relies on The Hive custom string field named `bitdefender-computer-id`, which contains `computer-id`. The `bitdefender-computer-id` must be filled either automatically when an event is forwarded or manually later.

## Initial Setup

Setup the responder in Cortex

1. `Organization->Responders->Search for Bitdefender_Init_Scan` and click `Enable`
2. Setup `Bitdefender_API_Key` which you can get from your GravityZone. The scope has to be `Network API`.
3. Setup `Bitdefender_Url` to the network endpoint, e.g. `https://cloudgz.gravityzone.bitdefender.com/api/v1.0/jsonrpc/network`

## Usage

Open a The Hive event with the `bitdefender-computer-id` custom field, open the responders and Lunch responder `Bitdefender_Init_Scan`.

![alt text](data/responder_use.gif?raw=true)

You should see if the responder was successfully executed within a few seconds. Afterwards, the scan task is queued by the Bitdefender GravityZone and executed when the endpoint in question connects back.

![alt text](data/the_hive_bd_scan_init.png?raw=true)

The results can be later checked in the Bitdefender GravityZone Network->Tasks or if detected is forwarded to The Hive as a security event.

# Testing of the responder

The responder can be locally tested by running it with python with input.json.

```
tomaskabrt@SUMUP-C02DW82YML85 bd % cat data/input.json | python3 BDInitScan.py
{"success": true, "full": {"message": "Scan task was successfully requested!"}, "operations": []}%
```

# References
[How to create custom field](https://docs.thehive-project.org/thehive/user-guides/administrators/custom-fields/)
[How to create a responder](https://github.com/TheHive-Project/CortexDocs/blob/master/api/how-to-create-a-responder.md)
[How to run a responder](https://docs.thehive-project.org/cortex/installation-and-configuration/analyzers-responders/#run-you-own-analyzers-responders)
[Bitdefender Create Scan Task API call](https://www.bitdefender.com/business/support/en/77209-128495-createscantask.html)
