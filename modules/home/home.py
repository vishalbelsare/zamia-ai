#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Copyright 2016, 2017, 2018 Guenter Bartsch
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from xsbprolog import XSBString

def get_data(k):

    k.dte.set_prefixes([u''])

    # NER, macros

    for lang in ['en', 'de']:
        for res in k.prolog_query("aiHomeLocation(HOME_LOCATION), rdfsLabel(HOME_LOCATION, %s, LABEL), aiPrepLoc(HOME_LOCATION, %s, PL)." % (lang, lang)):
            s_loc   = res[0].name
            s_label = res[1].value
            s_pl    = res[2].value if isinstance(res[2], XSBString) else u""
            k.dte.ner(lang, 'home_location', s_loc, s_label)
            k.dte.macro(lang, 'home_locations', {'LABEL': s_label, 'PL': s_pl})

    k.dte.macro('en', 'light_actions', {'LABEL':  'on', 'ACTION': 'light_on'})
    k.dte.macro('en', 'light_actions', {'LABEL': 'off', 'ACTION': 'light_off'})
    k.dte.macro('de', 'light_actions', {'LABEL':  'an', 'ACTION': 'light_on'})
    k.dte.macro('de', 'light_actions', {'LABEL': 'ein', 'ACTION': 'light_on'})
    k.dte.macro('de', 'light_actions', {'LABEL': 'aus', 'ACTION': 'light_off'})

    def turn_lights(c, ts, te, laction):

        def act(c, args):
            laction, loc = args
            c.kernal.mem_set(c.realm, 'action', XSBString(laction))
            c.kernal.mem_push(c.user, 'f1loc', loc)

        if ts>=0:
            hss = c.ner(c.lang, 'home_location', ts, te)
        else:
            hss = c.kernal.mem_get_multi(c.user, 'f1loc')
            if not hss:
                hss = [('aiHLLivingRoom', 100.0)]

        for loc, score in hss:
            c.resp(u"", score=score, action=act, action_arg=(laction, loc) )

    k.dte.dt('en', u"(please|) (switch|turn|dim) {light_actions:LABEL} the lights {home_locations:PL} {home_locations:LABEL} (please|)",
                   turn_lights, ['home_locations_0_start', 'home_locations_0_end', 'light_actions_0_action'])
    k.dte.dt('de', u"(bitte|) (schalte|mach) (bitte|) (mal|) das Licht {home_locations:PL} {home_locations:LABEL} {light_actions:LABEL} (bitte|)",
                   turn_lights, ['home_locations_0_start', 'home_locations_0_end', 'light_actions_0_action'])

    def check_light (c, args):
        action, loc = args
        # import pdb; pdb.set_trace()
        assert c.kernal.mem_get(c.realm, 'action').value == action
        l1, score = c.kernal.mem_get_multi(c.user, 'f1loc')[0]
        assert l1.name == loc
        
    k.dte.ts('en', 't0000', [(u"please switch on the lights in the living room", u"", check_light, ['light_on', 'aiHLLivingRoom'])])
    k.dte.ts('de', 't0001', [(u"bitte schalte das Licht in der Werkstatt ein", u"", check_light, ['light_on', 'aiHLWorkshop'])])

    k.dte.ts('en', 't0004', [(u"please switch off the lights in the dining room", u"", check_light, ['light_off', 'aiHLDiningRoom'])])
    k.dte.ts('de', 't0005', [(u"schalte mal das Licht im Schlafzimmer aus", u"", check_light, ['light_off', 'aiHLBedroom'])])

    k.dte.dt('en', u"(please|) lights {light_actions:LABEL} {home_locations:PL} {home_locations:LABEL}",
                   turn_lights, ['home_locations_0_start', 'home_locations_0_end', 'light_actions_0_action'])
    k.dte.dt('de', u"(bitte|) Licht {light_actions:LABEL} {home_locations:PL} {home_locations:LABEL}",
                   turn_lights, ['home_locations_0_start', 'home_locations_0_end', 'light_actions_0_action'])

    k.dte.ts('en', 't0002', [(u"lights on in the kitchen", u"", check_light, ['light_on', 'aiHLKitchen'])])
    k.dte.ts('de', 't0003', [(u"Licht an im Keller", u"", check_light, ['light_on', 'aiHLBasement'])])

    k.dte.dt('en', u"(please|) lights {light_actions:LABEL} (please|)",
                   turn_lights, [-1, -1, 'light_actions_0_action'])
    k.dte.dt('de', u"(bitte|) Licht {light_actions:LABEL} (bitte|)",
                   turn_lights, [-1, -1, 'light_actions_0_action'])

    k.dte.dt('en', u"(please|) (switch|turn|dim) {light_actions:LABEL} the lights (please|)",
                   turn_lights, [-1, -1, 'light_actions_0_action'])
    k.dte.dt('de', u"(bitte|) (schalte|mach) (bitte|) (mal|) das Licht {light_actions:LABEL} (bitte|)",
                   turn_lights, [-1, -1, 'light_actions_0_action'])

    k.dte.ts('en', 't0006', [(u"lights on in the living room", u"", check_light, ['light_on', 'aiHLLivingRoom']),
                             (u"switch on the lights in the attic", u"", check_light, ['light_on', 'aiHLAttic']),
                             (u"please turn off the lights", u"", check_light, ['light_off', 'aiHLAttic'])])
    k.dte.ts('de', 't0007', [(u"licht an im Wohnzimmer", u"", check_light, ['light_on', 'aiHLLivingRoom']),
                             (u"schalte das licht auf dem dachboden ein", u"", check_light, ['light_on', 'aiHLAttic']),
                             (u"bitte schalte das licht aus", u"", check_light, ['light_off', 'aiHLAttic'])])

