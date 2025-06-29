import opentrons.execute # type: ignore
from opentrons import protocol_api # type: ignore
metadata = {"apiLevel": "2.22", "description": '''[D9] (MYT Plate, Slot 2): pMYT045_nan_34_Assembly_Cassette, 
[A5] (MYT Plate, Slot 2): pMYT005_2_pLacFEC, 
[A1] (Temp Module): sgrna-rfp_3_a6+r2+r14_No-self-A, 
[A2] (Temp Module): sgrna-rfp_3_a6+r2+a16_No-other-R, 
[A3] (Temp Module): sgrna-rfp_3_a6+r2_No-fb, 
[A4] (Temp Module): sgrna-rfp_3_a6_Rep-only, 
[E8] (YTK Plate, Slot 3): pYTK056_4_tTDH1, 

[A5] (Temp Module): Master Mix,
[A6] (Temp Module): Molecular Grade Water, 

Constructs will be built in the thermocycler module:

[A1]: pMYT045_nan_34_Assembly_Cassette-pMYT005_2_pLacFEC-sgrna-rfp_3_a6+r2+r14_No-self-A-pYTK056_4_tTDH1, 
[A2]: pMYT045_nan_34_Assembly_Cassette-pMYT005_2_pLacFEC-sgrna-rfp_3_a6+r2+a16_No-other-R-pYTK056_4_tTDH1, 
[A3]: pMYT045_nan_34_Assembly_Cassette-pMYT005_2_pLacFEC-sgrna-rfp_3_a6+r2_No-fb-pYTK056_4_tTDH1, 
[A4]: pMYT045_nan_34_Assembly_Cassette-pMYT005_2_pLacFEC-sgrna-rfp_3_a6_Rep-only-pYTK056_4_tTDH1, 

Toolkit plate locations on deck:
  MYT Plate: Slot 2
  YTK Plate: Slot 3
'''}

# Fragments and constructs
inserts = {'pMYT045_nan_34_Assembly_Cassette': ('MYT', 'D9'), 'pMYT005_2_pLacFEC': ('MYT', 'A5'), 'sgrna-rfp_3_a6+r2+r14_No-self-A': ('tube_rack', 'A1'), 'sgrna-rfp_3_a6+r2+a16_No-other-R': ('tube_rack', 'A2'), 'sgrna-rfp_3_a6+r2_No-fb': ('tube_rack', 'A3'), 'sgrna-rfp_3_a6_Rep-only': ('tube_rack', 'A4'), 'pYTK056_4_tTDH1': ('YTK', 'E8')} # type: ignore
constructs = [['pMYT045_nan_34_Assembly_Cassette', 'pMYT005_2_pLacFEC', 'sgrna-rfp_3_a6+r2+r14_No-self-A', 'pYTK056_4_tTDH1'], ['pMYT045_nan_34_Assembly_Cassette', 'pMYT005_2_pLacFEC', 'sgrna-rfp_3_a6+r2+a16_No-other-R', 'pYTK056_4_tTDH1'], ['pMYT045_nan_34_Assembly_Cassette', 'pMYT005_2_pLacFEC', 'sgrna-rfp_3_a6+r2_No-fb', 'pYTK056_4_tTDH1'], ['pMYT045_nan_34_Assembly_Cassette', 'pMYT005_2_pLacFEC', 'sgrna-rfp_3_a6_Rep-only', 'pYTK056_4_tTDH1']] # type: ignore

# Tube rack locations of reagents
master_mix = f'A5' # type: ignore
reagent_tubes = [master_mix] + list(inserts.values())

# Construct Tube Locations
construct_tubes = ['A1', 'A2', 'A3', 'A4'] # type: ignore

# Define volumes, in uL
vol_master_mix_per_reaction = [6.0, 6.0, 6.0, 6.0] # type: ignore
vol_per_insert_dict = {'pMYT045_nan_34_Assembly_Cassette': 1.0, 'pMYT005_2_pLacFEC': 1.0, 'sgrna-rfp_3_a6+r2+r14_No-self-A': 1.0, 'sgrna-rfp_3_a6+r2+a16_No-other-R': 1.0, 'sgrna-rfp_3_a6+r2_No-fb': 1.0, 'sgrna-rfp_3_a6_Rep-only': 1.0, 'pYTK056_4_tTDH1': 1.0} # type: ignore

# Thermocycler settings
reaction_temp = 37 # type: ignore
ligation_temp = 16.0 # type: ignore
inactivation_temp = 65 # type: ignore
reaction_vol = 15.0 # type: ignore
num_cycles = 25 # type: ignore

def run(protocol: protocol_api.ProtocolContext):
    # --- TIP USAGE CHECK & TIPRACK LOADING ---
    num_master_mix_transfers = len(construct_tubes)
    num_insert_transfers = sum(len(construct) for construct in constructs)
    total_p20_tips = num_insert_transfers + sum(1 for v in vol_master_mix_per_reaction if v < 20)
    total_p300_tips = sum(1 for v in vol_master_mix_per_reaction if v >= 20)

    # Calculate how many tip racks are needed (each rack has 96 tips)
    num_p20_racks = (total_p20_tips - 1) // 96 + 1 if total_p20_tips > 0 else 0
    num_p300_racks = (total_p300_tips - 1) // 96 + 1 if total_p300_tips > 0 else 0

    # Assign deck slots for tip racks and toolkit plates
    available_slots = ["1", "2", "3", "5", "6", "9"]

    p20_slots = available_slots[:num_p20_racks]
    p300_slots = available_slots[num_p20_racks:num_p20_racks+num_p300_racks]
    toolkit_slots = available_slots[num_p20_racks+num_p300_racks:]

    # Load tip racks
    tips20_racks = []
    tips300_racks = []
    if total_p20_tips > 0:
        tips20_racks = [protocol.load_labware("opentrons_96_tiprack_20ul", slot) for slot in p20_slots]
    if total_p300_tips > 0:
        tips300_racks = [protocol.load_labware("opentrons_96_tiprack_300ul", slot) for slot in p300_slots]
    # Load other labware
    use_reservoir_for_mm = sum(vol_master_mix_per_reaction) > 1000
    if use_reservoir_for_mm:
        master_mix_reservoir = protocol.load_labware("nest_12_reservoir_15ml", available_slots[num_p20_racks:num_p20_racks+num_p300_racks:num_p300_racks+1])  # Use slot 5 for master mix
    tc_mod = protocol.load_module(module_name="thermocyclerModuleV2")
    tc_plate = tc_mod.load_labware(name="opentrons_96_wellplate_200ul_pcr_full_skirt")
    temp_mod = protocol.load_module(
        module_name="temperature module gen2", location="4"
    )
    temp_tubes = temp_mod.load_labware(
        "opentrons_24_aluminumblock_nest_1.5ml_snapcap"
    )
    # --- Load all toolkit plates needed ---
    toolkit_plate_types = set()
    for val in inserts.values():
        if isinstance(val, (tuple, list)):
            plate_type, _ = val
            if plate_type not in ("tube_rack", "temp_module"):
                toolkit_plate_types.add(plate_type)
    toolkit_plates = {}
    for idx, plate_type in enumerate(sorted(toolkit_plate_types)):
        if idx < len(toolkit_slots):
            toolkit_plates[plate_type] = protocol.load_labware("nest_96_wellplate_200ul_flat", toolkit_slots[idx])
        else:
            toolkit_plates[plate_type] = None

    # Initialize pipettes with all loaded tip racks
    if tips300_racks:
        p300 = protocol.load_instrument("p300_single_gen2", "right", tip_racks=tips300_racks)
    else:
        p300 = protocol.load_instrument("p300_single_gen2", "right")
    if tips20_racks:
        p20 = protocol.load_instrument("p20_single_gen2", "left", tip_racks=tips20_racks)
    else:
        p20 = protocol.load_instrument("p20_single_gen2", "left")

    # --- TIP USAGE CHECK ---
    if (total_p20_tips + total_p300_tips) > 480:
        raise Exception(
            f"Not enough tips: Need 20 x 20uL tips and 0 x 300uL tips, "
            "but only 5 racks are loaded. Please reduce the number of reactions."
        )

    # Initialize thermocycler
    tc_mod.open_lid()

    # Pipette transfer function to handle both pipettes
    def pipette_transfer(vol, source, dest, pipette=None):
        if pipette is not None:
            pipette.transfer(vol, source, dest, new_tip='never')
        else:
            if vol < 20:
                p20.transfer(vol, source, dest, new_tip='never')
            else:
                p300.transfer(vol, source, dest, new_tip='never')

    # Blink and pause function
    def pause(message):
        for i in range(3):
            protocol.set_rail_lights(False)
            protocol.delay(seconds=0.3)
            protocol.set_rail_lights(True)
            protocol.delay(seconds=0.3)
        protocol.set_rail_lights(True)
        protocol.pause(message)

    # Distribute master mix to tubes using multi-dispense (one tip per batch)
    def distribute_master_mix(volumes, source, dest_wells, pipette):
        pipette.pick_up_tip()
        for vol, dest in zip(volumes, dest_wells):
            pipette.aspirate(vol, source)
            pipette.dispense(vol, dest)
        pipette.drop_tip()

    # Group wells by pipette type (p20 for <20uL, p300 for >=20uL)
    wells_p20 = []
    vols_p20 = []
    wells_p300 = []
    vols_p300 = []
    for idx, vol in enumerate(vol_master_mix_per_reaction):
        if vol < 20:
            wells_p20.append(tc_plate[construct_tubes[idx]])
            vols_p20.append(vol)
        else:
            wells_p300.append(tc_plate[construct_tubes[idx]])
            vols_p300.append(vol)

    # Use the correct source for master mix
    if use_reservoir_for_mm:
        mm_source = master_mix_reservoir[master_mix] if not isinstance(master_mix, (tuple, list)) else master_mix_reservoir[master_mix[1]]
    else:
        mm_source = temp_tubes[master_mix]

    # Calculate water needed for each well to reach the correct total volume
    wells_needing_water = []
    water_vols = []
    for index, construct_tube in enumerate(construct_tubes):
        construct_inserts = constructs[index]
        total_insert_vol = sum(vol_per_insert_dict.get(insert, 5) for insert in construct_inserts)
        water_needed = reaction_vol - (vol_master_mix_per_reaction[index] + total_insert_vol)
        if water_needed > 0:
            wells_needing_water.append(tc_plate[construct_tube])
            water_vols.append(water_needed)
    if wells_needing_water:
        p20.pick_up_tip()
        for vol, dest in zip(water_vols, wells_needing_water):
            p20.transfer(vol, temp_tubes['A2'], dest, new_tip='never')
        p20.drop_tip()

    # Now distribute master mix to each well
    if wells_p20:
        distribute_master_mix(vols_p20, mm_source, wells_p20, p20)
    if wells_p300:
        distribute_master_mix(vols_p300, mm_source, wells_p300, p300)

    # Now add inserts to each well
    for index, construct_tube in enumerate(construct_tubes):
        construct_inserts = constructs[index]
        for i, insert in enumerate(construct_inserts):
            insert_location = inserts[insert]
            insert_vol = vol_per_insert_dict.get(insert, 5)  # Default to 5 if not found
            p20.pick_up_tip()
            # Decide which plate to use for each insert
            if isinstance(insert_location, tuple) or isinstance(insert_location, list):
                plate_type, well = insert_location
                if plate_type in toolkit_plates and toolkit_plates[plate_type] is not None:
                    pipette_transfer(insert_vol, toolkit_plates[plate_type][well], tc_plate[construct_tube], pipette=p20)
                else:
                    pipette_transfer(insert_vol, temp_tubes[well], tc_plate[construct_tube], pipette=p20)
            else:
                pipette_transfer(insert_vol, temp_tubes[insert_location], tc_plate[construct_tube], pipette=p20)
            # After the last insert, custom mix in the destination well with the same tip, then drop
            if i == len(construct_inserts) - 1:
                custom_mix(
                    pipette=p20,
                    well=tc_plate[construct_tube],
                    mixreps=4,
                    vol=min(20, insert_vol * len(construct_inserts)),
                    z_asp=1,
                    z_disp_source_mix=8,
                    z_disp_destination=8
                )
            p20.drop_tip()

    # Close the thermocycler lid before starting the protocol
    tc_mod.close_lid()

    '''
    Thermocycler protocol based on BsaI test protocol, variables passed from script generation
    ----------------------
    Lid: inactivation_temp + 10C
    Volume: reaction_vol
    1. reaction_temp, 15min
    2. reaction_temp, 1.5min
    3. ligation_temp, 3min
    4. GOTO step 2, num_cycles x
    5. ligation_temp, 20min
    6. 50C, 10min
    7. inactivation_temp, 10min
    8. 4C, 1 min, pause to open lid
    '''    
    tc_mod.set_lid_temperature(temperature=(inactivation_temp + 10))
    tc_mod.set_block_temperature(temperature=reaction_temp, hold_time_seconds=900, block_max_volume=reaction_vol) # 15 min
    for i in range(num_cycles):
        tc_mod.set_block_temperature(temperature=reaction_temp, hold_time_seconds=90, block_max_volume=reaction_vol) # 1.5 min
        tc_mod.set_block_temperature(temperature=ligation_temp, hold_time_seconds=180, block_max_volume=reaction_vol) # 3 min
    tc_mod.set_block_temperature(temperature=ligation_temp, hold_time_seconds=1200, block_max_volume=reaction_vol) # 20 min
    tc_mod.set_block_temperature(temperature=50, hold_time_seconds=300, block_max_volume=reaction_vol) # 10 min
    tc_mod.set_block_temperature(temperature=inactivation_temp, hold_time_seconds=600, block_max_volume=reaction_vol) # 10 min
    tc_mod.set_block_temperature(temperature=4, hold_time_seconds=60) # 1 min
    tc_mod.deactivate_lid() # Deactivate lid to allow for pipetting
    protocol.delay(seconds=5) # Wait for lid to cool down

    pause("Thermocycler protocol complete, holding at 4 Celsius. Press continue to open thermocycler lid.")
    tc_mod.open_lid() # Open lid for pipetting

def custom_mix(pipette, well, mixreps=3, vol=20, z_asp=1, z_disp_source_mix=8, z_disp_destination=8):
    # Save original flow rates
    orig_asp = pipette.flow_rate.aspirate
    orig_disp = pipette.flow_rate.dispense
    # Increase flow rates for mixing
    pipette.flow_rate.aspirate *= 4
    pipette.flow_rate.dispense *= 6
    for _ in range(mixreps):
        pipette.aspirate(vol, well.bottom(z_asp))
        pipette.dispense(vol, well.bottom(z_disp_source_mix))
    # Restore original flow rates BEFORE blow out
    pipette.flow_rate.aspirate = orig_asp
    pipette.flow_rate.dispense = orig_disp
    # Blow out just above the bottom to help droplet detach
    pipette.blow_out(well.bottom(z_disp_destination + 2))
    # Touch tip to the well wall to remove any droplet
    pipette.touch_tip(well)


