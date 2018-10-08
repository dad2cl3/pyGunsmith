# pyGunsmith
Discord bot written in Python. Allows users to show off **equipped** guns acquired while playing Destiny 2.
# Introduction
The bot is split into two separate files. The first, [pyGunsmith.py](https://github.com/dad2cl3/pyGunsmith/blob/master/pyGunsmith.py), contains the basic code the bot needs to function.

The second, [gunsmith.py](https://github.com/dad2cl3/pyGunsmith/), contains the processing logic necessary to support the various commands available except the *help* option.

The main processing logic relies upon two functions: *initialize()* and *main()*.

*initialize()* loads all possible definitions from the manifest into memory within the bot in order to greatly minimize the number of calls needed to the Bungie.net API. The bot utilizes the following manifest tables:
* DestinyCollectibleDefinition 
* DestinyInventoryBucketDefinition
* DestinyInventoryItemDefinition
* DestinyStatDefinition

*main()* is where a fully validated request to the bot is turned into a response back to the requestor. The function is written to minimize the number of Bungie.net API calls due to the overhead incurred for each call.

# Dependencies
The gunsmith bot relies on the following repositories (which may or may not be up to date :-) I swear it is on my list of todos):

[destiny-clan-member-manager](https://github.com/dad2cl3/destiny-clan-member-manager): Daily process to refresh clan member data.

[destiny-manifest-manager](https://github.com/dad2cl3/destiny-manifest-manager): Daily process to keep manifest data up to date.

[pyWelcomeBot](https://github.com/dad2cl3/pyWelcomeBot): Discord bot that supports several administrative functions including maintaining a cross-reference of Discord accounts to Destiny accounts.

**Note:** The dependency on converting a Discord user to a Destiny account can be removed if an additional parameter is added that represents the Bungie.net account name. An additional API call would be necessary to resolve the Bungie.net account name to one or more Destiny account profiles. Another option would be to require a Destiny gamertag and make the platform option required. The two values could then be used to resolve to a single Destiny account profile through a call to the Bungie.net API.

Also, the dependency on pulling the manifest data from a database can be easily replaced with code that will pull the most recent manifest file into memory and load the definitions from the file held in memory. Such a solution would also need a background task built into the bot to monitor for new versions of the manifest published by Bungie.net.
# Supported Commands

## !gunsmith help
The *help* command generates a direct message to the sender. The contents of the direct message are contained within the configuration file used by the bot.

The *help* message is as follows:
```Add screenshot
Gunsmith Help

Command syntax:

!gunsmith [platform] [subclass] [weapon]
where platform, subclass, and weapon are optional and order does not matter.

Platform Options
pc
ps
xb

Subclass Options
hunter
titan
warlock

Weapon Options
kinetic
energy
power

Syntax Examples:
!gunsmith
!gunsmith hunter
!gunsmith power
!gunsmith xb
!gunsmith hunter power xb

Processing Rules:

If *platform* is not supplied, the most recent platform played will be identified.

If *subclass* is not supplied, the most recent character played will be used.

If *weapon* is not supplied, all equipped weapons will be returned.

If no options are supplied, all equipped weapons for the most recently played character on the most recently played platform will be returned.
```
**Note:** The bot will ignore options it doesn't recognize based on the valid options and rules above.

## !gunsmith reload
The *reload* command forces the bot to reload manifest definitions and the Discord user to Destiny account(s) cross-reference utilized by the bot. It can only be run by a specified list of users including the gunsmith.

An optional webhook was also be created to support reloading of all in-memory data as part of automated processing. The webhook is called following the daily refresh of clan member data and after a refresh of manifest data from Bungie.net. The payload of the webhook is simply *!gunsmith reload*.

## !gunsmith [platform] [subclass] [weapon]
The main option for showing off guns in Discord.

Sample response in Discord:
![Sample response](https://github.com/dad2cl3/pyGunsmith/blob/master/doc/gunsmith-response.png)

# Process Flows

![!gunsmith help](https://github.com/dad2cl3/pyGunsmith/blob/master/doc/gunsmith-help.png)

![!gunsmith reload](https://github.com/dad2cl3/pyGunsmith/blob/master/doc/gunsmith-reload.png)

![!gunsmith [platform] [subclass] [weapon]](https://github.com/dad2cl3/pyGunsmith/blob/master/doc/gunsmith.png)
