# pyGunsmith
Discord bot written in Python. Allows users to show off guns acquired while playing Destiny 2.

# Dependencies
The gunsmith bot relies on the following repositories (which may or may not be up to date :-)):

destiny-clan-member-manager: Daily process to refresh clan member data
destiny-manifest-manager: Daily process to keep manifest data up to date
pyWelcomeBot: Discord bot that supports several administrative functions including maintaining a cross-reference of Discord accounts to Destiny accounts

# Supported Commands

## !gunsmith help
The *help* command generates a direct message to the sender. The contents of the direct message are contained within the configuration file used by the bot.

The *help* message is as follows:

**Gunsmith Help**

**Command syntax:**
!gunsmith [platform] [subclass] [weapon]
where platform, subclass, and weapon are optional and order does not matter.

**Platform Options**
pc
ps
xb

**Subclass Options**
hunter
titan
warlock

**Weapon Options**
kinetic
energy
power

**Syntax examples:**
!gunsmith
!gunsmith hunter
!gunsmith power
!gunsmith xb
!gunsmith hunter power xb

# Processing Rules

If platform is not supplied, the most recent platform played will be identified.

If subclass is not supplied, the most recent character played will be used.

If weapon is not supplied, all equipped weapons will be returned.

If no options are supplied, all equipped weapons for the most recently played character on the most recently played platform will be returned.

**Note:** The bot will ignore options it doesn't recognize based on the valid options and rules above.

## !gunsmith reload
The *reload* command forces the bot to reload manifest definitions utilized within the bot.

A webhook can also be created to support reloading of definitions as part of automated processing. Simply create a webhook and send the payload !gunsmith reload after a refresh of manifest data from Bungie, for example.

## !gunsmith [platform] [subclass] [weapon]
The main option for showing off guns in Discord.

Sample response in Discord:
[Insert screenshot]

# Process flows

## !gunsmith help
[Insert screenshot]

## !gunsmith reload
[Insert screenshot]

## !gunsmith [platform] [subclass] [weapon]
[Insert screenshot]
