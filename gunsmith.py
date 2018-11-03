import json, pg8000, requests, time

with open ('gunsmith-config.json') as config_file:
    config = json.load(config_file)

db_config = config['database']

gunsmith_definitions = {}

def execute_sql(conn, sql):

    results = {}

    pg_cursor = conn.cursor()
    pg_cursor.execute(sql)
    query_results = pg_cursor.fetchall()

    for record in query_results:
        results[record[0]] = record[1]

    return results


def initialize ():

    definitions = {}

    pg = pg8000.connect(
        host=db_config['database_host'],
        port=db_config['database_port'],
        database=db_config['database_name'],
        user=db_config['database_user'],
        password=db_config['database_password']
    )

    definitions_sql = db_config['sql']

    start = time.time()
    for target_sql in definitions_sql:
        target_definitions = execute_sql(pg, target_sql['sql'])
        definitions[target_sql['target']] = target_definitions
        print('{0}: {1} definitions loaded...'.format(target_sql['target'], len(target_definitions)))

    duration = time.time() - start
    pg.close()

    # add static values
    # move to config file
    definitions['platforms'] = ['ps', 'xb', 'pc']
    print('{0}: {1} definitions loaded...'.format('platforms', len(definitions['platforms'])))

    definitions['subclasses'] = ['hunter', 'titan', 'warlock']
    print('{0}: {1} definitions loaded...'.format('subclasses', len(definitions['subclasses'])))

    definitions['weaponSlots'] = ['kinetic', 'energy', 'power']
    print('{0}: {1} definitions loaded...'.format('weaponSlots', len(definitions['weaponSlots'])))

    #print(json.dumps(definitions)) # debugging
    print('Database execution time: {0:.2f}s'.format(duration))
    print('Initialized the bot...')

    return definitions


def parse_input_string (input_string):
    print('Parsing input string...')

    targets = {}

    # identify target platform
    target_platform = 'none'
    for platform in gunsmith_definitions['platforms']:
        print('Checking input string for platform {0}...'.format(platform))
        if platform in input_string:
            target_platform = platform
            print('Platform {0} found...'.format(target_platform))

    targets['target_platform'] = target_platform

    # identify target subclass
    target_subclass = 'none'
    for subclass in gunsmith_definitions['subclasses']:
        print('Checking input string for subclass {0}...'.format(subclass))
        if subclass in input_string:
            print('Subclass {0} found...'.format(subclass))
            target_subclass = subclass

    targets['target_subclass'] = target_subclass

    # identify target weapon
    target_weapon_slot = 'none'
    for weapon_slot in gunsmith_definitions['weaponSlots']:
        print('Checking input string for weapon slot...')
        if weapon_slot in input_string:
            print('Weapon slot {0} found...'.format(weapon_slot))
            target_weapon_slot = weapon_slot

    targets['target_weapon_slot'] = target_weapon_slot

    print('Target platform: {0}'.format(target_platform))
    print('Target subclass: {0}'.format(target_subclass))
    print('Target weapon slot: {0}'.format(target_weapon_slot))

    return targets


def get_definition(type, hash):
    definition = {}

    if hash in gunsmith_definitions[type]:
        definition = gunsmith_definitions[type][hash]

    return definition


def get_account_profile(account_id, membership_type):
    print('Getting account profile...')
    headers = {
        'X-API-Key': config['API']['apiKey']
    }

    profile_url = config['API']['profileURL'].format(membership_type, account_id)

    response = requests.get(profile_url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        #print(data) # debugging
        if 'Response' in data:
            account_profile = data['Response']
        else:
            account_profile = data

        return account_profile
    else:
        return {}


def get_target_gunsmith_profile(gunsmith_profiles):
    print('Getting target gunsmith profile...')
    # need to correct return profile information
    time_format = '%Y-%m-%dT%H:%M:%SZ'
    last_played = time.strptime('2000-01-01T00:00:00Z', time_format)

    target_gunsmith_profile = {}

    for profile in gunsmith_profiles:
        print('Checking profile {0}'.format(profile))
        account_profile = get_account_profile(profile['destiny_id'], profile['destiny_membership_type'])
        if 'dateLastPlayed' in account_profile['profile']['data']:
            date_last_played = time.strptime(account_profile['profile']['data']['dateLastPlayed'], time_format)
            #print(date_last_played) debugging
            if date_last_played > last_played:
                target_gunsmith_profile = account_profile

    #print(json.dumps(target_gunsmith_profile))
    return target_gunsmith_profile


def get_gunsmith_profiles(server_id, discord_id):
    print('Getting gunsmith profile(s)...')

    print('Server ID: {0} - Discord ID: {1}'.format(server_id, discord_id))

    gunsmith_profiles = gunsmith_definitions['profiles']
    #print(gunsmith_profiles) # debugging

    found_profiles = []

    if int(discord_id) in gunsmith_profiles:
        print('Discord ID found')
        gunsmith_profile = gunsmith_profiles[int(discord_id)]
        #print(gunsmith_profile)
        if len(gunsmith_profile) >= 1:
            print('Searching for server...')
            for profile in gunsmith_profile:
                print(profile['server_id'])
                if int(server_id) == profile['server_id']:
                    found_profiles.append(profile)
    else:
        print(discord_id)

    return found_profiles


def get_weapon_detail (item_instance, item_components):
    print('Getting weapon details...')

    start = time.time()

    # get weapon definition
    item_definition = get_definition('items', str(item_instance['itemHash']))

    item_details = {}
    #if 'displayProperties' in item_definition:
    if item_definition != {}:
        item_details = {
            'name': item_definition['item_name'],
            'description': item_definition['item_description'],
            'icon': '{0}{1}'.format('https://www.bungie.net', item_definition['item_icon']),
            'screenshot': '{0}{1}'.format('https://www.bungie.net', item_definition['item_screenshot'])
        }


    # get instance stats
    stats_data = item_components['stats']['data'][item_instance['instanceId']]['stats']
    #print(json.dumps(stats_data)) # debugging

    weapon_stats = []
    for stat in stats_data:
        stat_value = stats_data[stat]['value']
        stat_definition = get_definition('stats', str(stat))
        stat_name = stat_definition['stat_name']
        weapon_stats.append('{0} {1}'.format(stat_name, stat_value))

    #print(json.dumps(weapon_stats)) # debugging
    # get hidden stats
    hidden_stats = []

    if 'stats' in item_definition:
        for stat in item_definition['stats']:
            stat_definition = get_definition('stats', str(stat))
            stat_name = stat_definition['stat_name']
            #print('Stat Name: {0}'.format(stat_name)) # debugger

            if len(stat_name) > 0:
                if stat_name in ['Aim Assistance', 'Recoil Direction', 'Zoom']:
                    stat_value = item_definition['stats'][stat]['value']

                    hidden_stats.append('{0} {1}'.format(stat_name, stat_value))

    hidden_stats = sorted(hidden_stats)

    #print(json.dumps(hidden_stats)) # debugging

    weapon_stats.extend(hidden_stats)

    #print(weapon_stats)

    # parse out the item components
    instance_data = item_components['instances']['data'][item_instance['instanceId']]

    socket_data = item_components['sockets']['data'][item_instance['instanceId']]

    weapon_plugs = []
    for single_socket in socket_data['sockets']:
        reusable_plugs = []
        if 'plugHash' in single_socket:
            plug_hash = single_socket['plugHash']
            plug_definition = get_definition('items', str(plug_hash))
            #print(plug_definition)
            plug_name = plug_definition['item_name']

            if len(plug_name) > 0:
                if 'reusablePlugHashes' in single_socket:
                    if plug_hash in single_socket['reusablePlugHashes']:
                        for reusable_plug_hash in single_socket['reusablePlugHashes']:
                            reusable_plug_definition = get_definition('items', str(reusable_plug_hash))
                            reusable_plug_name = reusable_plug_definition['item_name']

                            if reusable_plug_name == plug_name:
                                reusable_plug_name = '**{0}**'.format(reusable_plug_name)

                            reusable_plugs.append(reusable_plug_name)
                    else:
                        reusable_plugs.append('**{0}**'.format(plug_name))
                else:
                    reusable_plugs.append('**{0}**'.format(plug_name))

            plug_string = ' - '.join(reusable_plugs)
            weapon_plugs.append(plug_string)


    # get weapon source
    source_definition = get_definition('sources', str(item_instance['itemHash']))
    #print(source_definition)
    if source_definition != {}:
        weapon_source = source_definition['source'].replace('Source: ', '')
    else:
        weapon_source = ''

    weapon_details = {
        'details': item_details,
        'source': weapon_source,
        'stats': '\n'.join(weapon_stats),
        'perks': '\n'.join(weapon_plugs)
    }

    print(json.dumps(weapon_details))

    duration = time.time() - start
    print('Weapon Detail Duration: {0:.2f}s'.format(duration))
    return weapon_details


def get_most_recent_character(profile, characters):
    print('Finding most recent character...')
    # get most recent time from profile
    most_recent_time = profile['data']['dateLastPlayed']

    # loop through characters to find match for most_recent_time
    character_id = '0'
    for character in characters['data']:
        if characters['data'][character]['dateLastPlayed'] == most_recent_time:
            character_id = character

    return character_id


def get_character_by_class(characters, target_subclass):

    target_table_name = 'DestinyClassDefinition'
    found_characters = []
    character_id = '0'

    for character in characters['data']:

        class_definition = get_definition('subclass', characters['data'][character]['classHash'])

        #print(class_definition) # debugging
        if class_definition['name'].lower() == target_subclass.lower():
            found_characters.append({
                'character_id': character,
                'minutes_played_total': characters['data'][character]['minutesPlayedTotal']
            })

    if len(found_characters) > 1:
        most_minutes_played = 0
        for found_character in found_characters:
            if found_character['minutes_played_total'] > most_minutes_played:
                most_minutes_played = found_character['minutes_played_total']
                character_id = found_character['character_id']
    elif len(found_characters) == 1:
        character_id = found_characters[0]['character_id']

    return character_id


def main (server_id, discord_id, input_string, definitions):
    start_time = time.time()

    global gunsmith_definitions
    gunsmith_definitions = definitions

    weapon_details = []
    error_message = {}

    # testing override
    # server_id = 141176119813603328
    # discord_id = 297694001874731008
    # discord_id = 144518463883313153
    # discord_id = 348207889728536577

    # get discord profile
    gunsmith_profiles = get_gunsmith_profiles(server_id, discord_id)
    # print(gunsmith_profiles) # debugging

    # add check to make sure a profile exists
    if gunsmith_profiles == []:
        # move to config file
        error_message = {
            'error': 'Gunsmith profile not found. The command !link gamertag:dad2cl3 discord:dad2cl3 where dad2cl3 is replaced with your information should fix the problem.'
        }
    else:
        # get targets from input string
        if input_string != '':
            targets = parse_input_string(input_string)
        else:
            # move to config file
            targets = {
                'target_platform': 'none',
                'target_subclass': 'none',
                'target_weapon_slot': 'none'
            }

        # clean this up. all this could be stored as json in config file.
        if targets['target_platform'] == 'none':
            target_membership_type = 0
        elif targets['target_platform'] == 'pc':
            target_membership_type = 4
        elif targets['target_platform'] == 'ps':
            target_membership_type = 2
        elif targets['target_platform'] == 'xb':
            target_membership_type = 1

        print('Target membership type: {0}'.format(target_membership_type))

        # does platform exist in gunsmith profile
        target_gunsmith_profile = {}
        # refactor if statement. condense elif statements based on platforms requested.
        if target_membership_type > 0 and len(gunsmith_profiles) > 1:
            # specific platform requested and multiple gunsmith profiles found
            for gunsmith_profile in gunsmith_profiles:
                if gunsmith_profile['destiny_membership_type'] == target_membership_type:
                    target_gunsmith_profile = gunsmith_profile
        elif target_membership_type == 0 and len(gunsmith_profiles) > 1:
            # no platform requested and multiple gunsmith profiles found
            # requires API calls
            api_start_time = time.time()
            target_gunsmith_profile = get_target_gunsmith_profile(gunsmith_profiles)
            api_duration = time.time() - api_start_time
            api_time = '{0:.2f}s'.format(api_duration)
            print('API Duration: {0:.2f}s'.format(api_duration))
        elif target_membership_type > 0 and len(gunsmith_profiles) == 1:
            # specific platform requested and single gunsmith profile found
            #print(json.dumps(gunsmith_profiles)) # debugging
            if target_membership_type == gunsmith_profiles[0]['destiny_membership_type']:
                target_gunsmith_profile = gunsmith_profiles[0]
        elif target_membership_type == 0 and len(gunsmith_profiles) == 1:
            # no platform requested and single gunsmith profile found
            target_gunsmith_profile = gunsmith_profiles[0]

        #print(target_gunsmith_profile) # debugging

        if target_gunsmith_profile == {}:
            # move to config file
            error_message = {
                'error': 'Destiny profile not found.'
            }
        else:
            if 'profile' in target_gunsmith_profile:
                # target_gunsmith_profile already contains account profile for requestors who play on multiple platforms
                # no need to look up a second time
                account_profile = target_gunsmith_profile
            else:
                target_account_id = target_gunsmith_profile['destiny_id']
                target_membership_type = target_gunsmith_profile['destiny_membership_type']
                # get account profile
                api_start_time = time.time()
                account_profile = get_account_profile(target_account_id, target_membership_type)
                api_duration = time.time() - api_start_time
                api_time = '{0:.2f}s'.format(api_duration)
                print('API Duration: {0:.2f}s'.format(api_duration))

            if account_profile != {} and 'ErrorCode' not in account_profile:
                # profile found so split in to smaller manageable chunks
                profile_details = account_profile['profile']
                profile_characters = account_profile['characters']
                character_equipment = account_profile['characterEquipment']
                item_components = account_profile['itemComponents']
                profile_plug_sets = account_profile['profilePlugSets']
                character_plug_sets = account_profile['characterPlugSets']

                if targets['target_subclass'] == 'none':
                    # get most recent character
                    target_character = get_most_recent_character(profile_details, profile_characters)
                    #print(target_character) # debugging
                else:
                    # get specified subclass
                    # does subclass exist?
                    target_character = get_character_by_class(profile_characters, targets['target_subclass'])

                print('Target character: {0}'.format(target_character)) # debugging

                # string version of zero used b/c character_id is string in API response
                if target_character != '0':
                    # shrink character equipment
                    character_equipment = character_equipment['data'][target_character]['items']
                    item_instances = []

                    for item in character_equipment:
                        item_hash = item['itemHash']
                        bucket_hash = item['bucketHash']
                        bucket_name = gunsmith_definitions['buckets'][str(bucket_hash)]['bucket_name']

                        if targets['target_weapon_slot'] == 'none':
                            for weapon_slot in config['gunsmith']['weaponSlots']:
                                if weapon_slot in bucket_name.lower():
                                    #print(bucket_name) # debugging
                                    item_instances.append(
                                        {'itemHash': item_hash, 'instanceId': item['itemInstanceId']}
                                    )
                        elif targets['target_weapon_slot'] in bucket_name.lower():
                            item_instances.append({'itemHash': item_hash, 'instanceId': item['itemInstanceId']})

                    for item_instance in item_instances:
                        instance_details = get_weapon_detail(item_instance, item_components)
                        weapon_details.append(instance_details)
                else:
                    # move to config file
                    error_message = {
                        'error': 'Subclass not found for account.'
                    }
            else:
                # move to config file
                error_message = {
                    'error': 'Unable to retrieve account profile.'
                }

    duration = time.time() - start_time
    elapsed_time = '{0:.2f}s'.format(duration)
    print('{0:.2f}s'.format(duration))

    if error_message != {}:
        # error found
        return error_message
    else:
        response = {
            'api_time': api_time,
            'elapsed_time': elapsed_time,
            'weapon_details': weapon_details
        }
        return response

    #return {}
