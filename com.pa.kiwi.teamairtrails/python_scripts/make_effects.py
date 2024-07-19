import os
import json
import utils

import copy

pa_path = utils.pa_dir()

mod_path = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))

unit_list_path = "/pa_ex1/units/unit_list.json"

unit_list = utils.load_base_json(unit_list_path)

air_trail_path = '/pa/effects/specs/rainbow_trail.pfx'
space_trail_path = '/pa/effects/specs/orbital_trail.pfx'

# special orbital fighter json
orbital_fighter_path = '/pa/units/orbital/orbital_fighter/orbital_fighter.json'

# above water trail
air_trail = utils.load_mod_json(air_trail_path)
space_trail = utils.load_mod_json(space_trail_path)

base_air = copy.deepcopy(air_trail)
base_space = copy.deepcopy(space_trail)

# base offset entry
fx_offset = {
    'type':'idle',
    'bone': 'bone_root',
    'filename':'',
    'offset':[0, 0, 0],
    'orientation': [0, 0, 0]
}

# toggle this if you want duplicate trails for craft that have multiple engines
duplicate_trails = False

for unit in unit_list['units']:
    # skip the units which are not air or orbital fighter

    # change our trail effect filename
    # assume orbital fighter
    fx_offset['filename'] = space_trail_path
    base_trail = copy.deepcopy(space_trail)

    # if not orbital fighter, must check to make sure its an aircraft
    if orbital_fighter_path not in unit:
        if '/pa/units/air/' not in unit: continue
        # must be an aircraft
        fx_offset['filename'] = air_trail_path
        base_trail = copy.deepcopy(air_trail)
    
    mod_air_unit = os.path.join(mod_path, unit[1:])
    pa_air_unit = os.path.join(pa_path, unit[1:])

    pa_air_unit = pa_air_unit.replace("pa", "pa_ex1")
    # if /pa_ex1 path doesn't exist, fallback to use the /pa path
    # some titan units don't shadow the base pa units... such as air scout
    if not os.path.exists(pa_air_unit):
        pa_air_unit = pa_air_unit.replace("pa_ex1", "pa")

    # check if we have a air_unit in the listed location
    if os.path.exists(pa_air_unit):
        # check if the current unit has base spec of a flying air unit
        # pa/units/air/base_flyer
        # load air_unit json for manipulation
        air_unit = json.load(open(pa_air_unit))

        # once again refine filter to only orbital fighter and mobile aircraft
        if orbital_fighter_path not in unit:
            if '/pa/units/air/base_flyer/' not in air_unit.get('base_spec',''): continue
        
        print('Updating: ', os.path.basename(pa_air_unit))
        
        # create mod folder if it does not exist
        if not os.path.exists(os.path.dirname(mod_air_unit)):
           os.makedirs(os.path.dirname(mod_air_unit))

        # get offset list from the actual air_unit json
        #    if it doesn't exist already, return empty array to append to
        fx_offsets = air_unit.get('fx_offsets', [])

        if duplicate_trails:
            new_offsets = []
            # the craft has only rocket offset, lets use it!
            for offset in fx_offsets:

                if 'jets' not in offset['filename']: continue
                
                # now we need to get a list of thruster effects
                effect_file = utils.load_base_json(offset['filename'])
                
                for emitter in effect_file['emitters']:
                    new_offset = copy.deepcopy(offset)
                    # make this offset a rainbow trail
                    new_offset['filename'] = fx_offset['filename']
                    
                    if 'jet' in emitter['spec'].get('baseTexture', ''):
                        # accumulate offsets unless the effect is on a rotating bone
                        if offset.get('bone', 'ignore') not in ['bone_leftWing', 'bone_rightWing']:
                            new_offset['offset'][0] += emitter.get('offsetX', 0)
                            new_offset['offset'][1] += emitter.get('offsetY', 0)
                            new_offset['offset'][2] += emitter.get('offsetZ', 0)
                        
                        new_offsets.append(copy.deepcopy(new_offset))
                        
            if len(new_offsets) == 0:
                new_offsets = [fx_offset]

            # add our custom offsets
            fx_offsets.extend(new_offsets)
        else:
            if len(fx_offsets) == 1:
                new_offset = copy.deepcopy(fx_offsets[0])
                new_offset['filename'] = fx_offset['filename']
                fx_offset = new_offset
            fx_offsets.append(fx_offset)
            
        # override air_unit fx_offsets array
        air_unit['fx_offsets'] = fx_offsets

        # write changes to file
        json.dump(air_unit, open(mod_air_unit, 'w'), indent=4)
