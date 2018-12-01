import discord, gunsmith, json, re

print('Bot starting...')
print('Loading configuration file...')
with open('gunsmith-config.json', 'r') as config_file:
    config = json.load(config_file)

discord_config = config['discord']

client = discord.Client()

print('Initializing bot...')
gunsmith_definitions = gunsmith.initialize()

@client.event
async def on_ready():
    print('Bot is ready...')


@client.event
async def on_message (message):

    global gunsmith_definitions

    if message.content.startswith('!gunsmith'):
        input_string = message.content
        input_string = input_string.replace('!gunsmith ', '').strip()

        if input_string == 'reload':
            print('Gunsmith is reloading...')
            author_name = str(message.author)
            print(author_name)
            # ignore requests not delivered from the webhook
            # following criteria needs to be moved to config file
            if 'gunsmith' in author_name or 'dad2cl3' in author_name:
                gunsmith_definitions = gunsmith.initialize()
                # following message body needs to be moved to config file
                await client.send_message(message.channel, 'Careful where you point that thing!')
            else:
                # following message body needs to be moved to config file
                await client.send_message(message.channel, 'First time was incompetence, this time it\'s sabotage. <@297694001874731008> get to the bottom of this.')

        else:
            discord_id = message.author.id
            server_id = message.server.id
            # testing override
            # should prolly move these overrides to config and enable a test mode for the bot.
            #server_id = 141176119813603328
            #discord_id = 312310965033238528
            #discord_id = 141625016193253377 # GreatDaemon
            #discord_id = 102806583133605888
            #discord_id = 347395856393043990 # mr_rots

            print('Server ID: {0} - Discord ID: {1}'.format(server_id, discord_id))

            input_string = message.content
            input_string = input_string.replace('!gunsmith', '').strip()
            print('Input string: {0}'.format(input_string))

            if input_string == 'help':
                sender_id = message.author.id
                user = await client.get_user_info(sender_id)

                help_details = config['help']
                help_embed = discord.Embed(
                    title=help_details['title'],
                    description=help_details['description']
                )

                help_embed.set_footer(
                    icon_url=help_details['footer']['icon_url'],
                    text=help_details['footer']['text']
                )

                for field in help_details['fields']:
                    help_embed.add_field(
                        name=field['name'],
                        value=field['value'],
                        inline=False
                    )

                await client.send_message(user, embed=help_embed)
            else:
                # add ability to override server and discord
                # search for server_id: and override local variable
                if 'server_id' in input_string:
                    server_id_pattern = re.compile('.*server_id:([0-9]+)\s?')

                    matches = re.match(server_id_pattern, input_string)

                    if len(matches.regs) == 2:
                        server_id = str(matches.group(1))
                        print('Override server_id: {0}'.format(server_id))

                # search for discord_id: and override local variable
                if 'discord_id' in input_string:
                    discord_id_pattern = re.compile('.*discord_id:([0-9]+)\s?')

                    matches = re.match(discord_id_pattern, input_string)
                    if len(matches.regs) == 2:
                        discord_id = str(matches.group(1))
                        print('Override discord_id: {0}'.format(discord_id))


                # strip out the overrides from the input string
                server_id_pattern = re.compile('(.*)(server_id:[0-9]+)(\s?)')
                input_string = server_id_pattern.sub('\\1\\3', input_string)

                discord_id_pattern = re.compile('(.*)(discord_id:[0-9]+)(\s?)')
                input_string = discord_id_pattern.sub('\\1\\3', input_string)

                # clean up any extra spaces
                input_string = input_string.strip()

                weapon_details = gunsmith.main(server_id, discord_id, input_string, gunsmith_definitions)
                #print(json.dumps(weapon_details)) # debugging

                if 'error' in weapon_details:
                    await client.send_message(message.channel, weapon_details['error'])
                else:
                    for weapon_detail in weapon_details['weapon_details']:
                        if len(input_string) > 0:
                            content = '<@{0}>: `{1}`'.format(discord_id, input_string)
                        else:
                            content = '<@{0}>'.format(discord_id)

                        #print(json.dumps(weapon_detail)) # debugging

                        weapon_embed = discord.Embed(
                            title=weapon_detail['details']['name'],
                            description=weapon_detail['details']['description']
                        )

                        if len(weapon_detail['details']['screenshot']) > 0:
                            weapon_embed.set_image(
                                url=weapon_detail['details']['screenshot']
                            )

                        weapon_embed.set_thumbnail(
                            url=weapon_detail['details']['icon']
                        )

                        if len(weapon_detail['source']) > 0:
                            weapon_embed.add_field(
                                name='Source(s)',
                                value=weapon_detail['source'],
                                inline=False
                            )

                        '''weapon_embed.add_field(
                            name='Stats',
                            value=weapon_detail['stat_names'],
                            inline=True
                        )

                        weapon_embed.add_field(
                            name='Values',
                            value=weapon_detail['stat_values'],
                            inline=True
                        )'''

                        weapon_embed.add_field(
                            name='Stats',
                            value=weapon_detail['stats']
                        )

                        weapon_embed.add_field(
                            name='Perks',
                            value=weapon_detail['perks'],
                            inline=False
                        )

                        weapon_embed.set_footer(
                            text='API Time: {0} - Elapsed Time: {1}'.format(weapon_details['api_time'], weapon_details['elapsed_time'])
                        )

                        print(json.dumps(weapon_embed.to_dict())) # debugging

                        await client.send_message(message.channel, content=content, embed=weapon_embed)

client.run(discord_config['token'])