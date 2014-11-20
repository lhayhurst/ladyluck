__author__ = 'lhayhurst'

ships = { 'X-Wing': ('Wedge Antilles',
                            'Luke Skywalker',
                            'Wes Janson',
                            'Jek Porkins',
                            'Red Squadron Pilot',
                            'Garven Dreis',
                            'Rookie Pilot',
                            'Biggs Darklighter',
                            'Hobbie" Klivian',
                            'Tarn Mison'),
                'Y-Wing' : ('Horton Salm',
                            'Gray Squadron Pilot',
                            'Dutch Vander',
                            'Gold Squadron Pilot' ),
                'A-Wing' : ('Tycho Celchu',
                            'Green Sq. Pilot',
                            'Arvel Crynyd',
                            'Prototype Pilot',
                            'Gemmer Sojan',
                            'Jake Farrell'),
                'YT-1300' : ('Han Solo', 'Chewbacca', 'Lando Calrissian', 'Outer Rim Smuggler'),
                'B-Wing' : ('Ten Numb', 'Keyan Farlander', 'Ibtisam', 'Nera Dantels', 'Dagger Sq. Pilot', 'Blue Sq. Pilot'),
                'HWK-290' : ( 'Jan Ors',
                              'Kyle Katarn',
                              'Roark Garnet',
                              'Rebel Operative' ),
                'E-Wing' : ('Corran Horn',
                            'Etahn A\'Baht',
                            'Blackmoon Squadron Pilot',
                            'Knave Squadron Pilot'),
                'Z-95 Headhunter' : ('Airen Cracken',
                                     'Lt. Blount',
                                     'Tala Squadron Pilot',
                                     'Bandit Squadron Pilot' ),
                'YT-2400' : ( 'Dash Rendar',
                              'Leebo',
                              'Eaden Vrill',
                              'Wild Space Fringer'),
                'TIE Fighter' : ( 'Howlrunner',
                                'Mauler Mithel',
                                'Dark Curse',
                                'Backstabber',
                                'Winged Gundark',
                                'Night Beast',
                                'Black Squadron Pilot',
                                'Obsidian Squadron Pilot',
                                'Academy Pilot' ),
               'TIE Advanced' : ('Darth Vader',
                                 'Maarek Steel',
                                 'Storm Squadron Pilot',
                                 'Tempest Squadron Pilot' ),
               'TIE Interceptor' : ('Soontir Fel',
                                    'Turr Phennir',
                                    'Fel\'s Wrath',
                                    'Saber Squadron Pilot',
                                    'Avenger Squadron Pilot',
                                    'Alpha Squadron Pilot',
                                    'Carnor Jax',
                                    'Tetran Cowall',
                                    'Kir Kanos',
                                    'Lt. Lorrir',
                                    'Royal Guard Pilot' ),
               'Firespray-31' : ('Boba Fett','Kath Scarlet','Krassis Trelix','Bounty Hunter' ),
               'Lambda Shuttle' : ('Captain Kagi', 'Colonel Jendon','Captain Yorr', 'Omicron Group Pilot' ),
               'TIE Bomber' : ('Major Rhymer',
                               'Captain Jonus',
                               'Gamma Squadron. Pilot',
                               'Scimitar Squadron Pilot' ),
               'TIE Defender' : ('Rexler Brath',
                                 'Col. Vessery',
                                 'Onyx Squadron Pilot',
                                 'Delta Squadron Pilot' ),
               'TIE Phantom' : ('Whisper', 'Echo', 'Shadow Squadron Pilot', 'Sigma Squadron Pilot' ),
               'VT-49 Decimator' : ( 'Rear Admiral Chiraneau',
                                     'Commander Kenkirk',
                                     'Captain Oicunn',
                                     'Patrol Leader' ) }


droids = ('R2-D2', 'R2-F2','R5-D8','R5-P9','R7-T1','R5-K6','R3-A2','R7 Astromech','R2-D6','R4-D6','R2 Astromech','R5 Astromech')

crew = ('Luke Skywalker',
'Gunner',
'Chewbacca',
'Leia Organa',
'R2-D2',
'Flight Instructor',
'Ysanne Isard',
'C-3PO',
'Darth Vader',
'Rebel Captive',
'Weapons Engineer',
'Recon Specialist',
'Navigator',
'Kyle Katarn',
'Lando Calrissian',
'Fleet Officer',
'Mara Jade',
'Han Solo',
'Mercenary Copilot',
'Saboteur',
'Tactician',
'Jan Ors',
'Dash Rendar',
'Leebo',
'Moff Jerjerrod',
'Nien Nunb',
'Intelligence Agent')


epts = ('Expose',
'Opportunist',
'Push the Limit',
'Marksmanship',
'Daredevil',
'Outmaneuver',
'Predator',
'Ruthlessness',
'Swarm Tactics',
'Squad Leader',
'Expert Handling',
'Elusiveness',
'Wingman',
'Decoy',
'Lone Wolf',
'Stay on Target',
'Intimidation',
'Veteran Instincts',
'Draw Their Fire',
'Determination',
'Deadeye',
'Adrenaline Rush')

titles = (
 'Outrider',
'Moldy Crow',
'ST-321',
'Dauntless',
'Millennium Falcon',
'Slave 1',
'Royal Guard TIE',
'A-Wing Test Pilot')

mods = ('Combat Retrofit',
'Shield Upgrade',
'Engine Upgrade',
'Advanced Cloaking Device',
'Stealth Device',
'Hull Upgrade',
'Counter-Measures',
'Experimental Interface',
'Anti-Pursuit Lasers',
'Targeting Computer',
'Stygium Particle Accelerator',
'Munitions Failsafe',
'B-Wing/E2',
'Tactical Jammer')

system_upgrades = ('Sensor Jammer',
'Advanced Sensors',
'Fire-Control System',
'Enhanced Scopes')

bombs_mines = ( 'Proton Bombs','Proximity Mines','Seismic Charges')

cannons =  ('Heavy Laser Cannon', 'AutoBlaster', 'Ion Cannon')

missiles = ('Assault Missiles',
'Homing Missiles',
'Concussion Missiles',
'Cluster Missiles',
'Ion Pulse Missle',
'Proton Rockets',
'Chardaan Refit')

torpedos = ('Advanced Proton Torpedoes',
'Ion Torpedoes',
'Proton Torpedos',
'Flechette Torpedoes')

turrets = ('Ion Cannon Turret','Blaster Turret')

class XWingMetaData:
    def is_rebel(self):
        self.is_rebel = True
        print ("is rebel")

    def is_imperial(self):
        self.is_rebel = False
        print ("is imp")

    def ships(self):
        return ships.keys()

    def ships_full(self):
        return ships

    def pilots_for_ship(self, ship):
        return ships[ ship ]

    def droids(self):
        return droids

    def crew(self):
        return crew

    def epts(self):
        return epts

    def titles(self):
        return titles

    def mods(self):
        return mods

    def system_upgrades(self):
        return system_upgrades

    def bomb_mines(self):
        return bombs_mines

    def cannons(self):
        return cannons

    def torpedos(self):
        return torpedos

    def missiles(self):
        return missiles

    def turrets(self):
        return turrets

class XWingList:

    def get_ship_for_id(self, id, request_form):
        ship = {}
        for k in request_form.keys():
            if k.endswith(id ) and request_form[k] is not None and len(request_form[k]) > 0 :
                ship[ k ] = request_form[ k ]
        return ship

    def get_ships_submitted(self, request_form):

        ret = []
        #8 ships is the most you can have, for now :-)
        for id in range(0,7,1):
            id = str(id)
            ship = self.get_ship_for_id(id, request_form)
            if len(ship.keys()) > 0:
                ret.append(ship)
        return ret

    def __init__(self, request_form):

        self.player  = request_form['player']
        self.faction = request_form['faction']
        self.points  = request_form['points']

        self.ships_submitted = self.get_ships_submitted(request_form)

