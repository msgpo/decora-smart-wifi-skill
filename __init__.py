#!/usr/bin/env python
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Mycroft Core.  If not, see <http://www.gnu.org/licenses/>.

from os.path import dirname
from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger
import re
from decora_wifi import DecoraWiFiSession
from decora_wifi.models.residential_account import ResidentialAccount


__author__ = 'PCWii'

# Logger: used for debug lines, like "LOGGER.debug(xyz)". These
# statements will show up in the command line when running Mycroft.
LOGGER = getLogger(__name__)

# List each of the bulbs here
decora_email = ""
decora_pass = ""
session = DecoraWiFiSession()
session.login(decora_email, decora_pass)
perms = session.user.get_residential_permissions() # Usually just one of these


def getSwitch:
    attribs = {}
    attribs['brightness'] = decora_bright
    for permission in perms:
        acct = ResidentialAccount(session, permission.residentialAccountId)
        residences = acct.get_residences()
        for residence in residences:
            switches = residence.get_iot_switches()
            for switch in switches:
                setSwitch = switch
                break
            break
        break
    return setSwitch

# The logic of each skill is contained within its own class, which inherits
# base methods from the MycroftSkill class with the syntax you can see below:
# "class ____Skill(MycroftSkill)"
class DecoraWifiSkill(MycroftSkill):

    # The constructor of the skill, which calls MycroftSkill's constructor
    def __init__(self):
        super(DecoraWifiSkill, self).__init__(name="DecoraWifiSkill")

    # This method loads the files needed for the skill's functioning, and
    # creates and registers each intent that the skill uses
    def initialize(self):
        self.load_data_files(dirname(__file__))

        decora_light_on_intent = IntentBuilder("DecoraWifiOnIntent").\
            require("DeviceKeyword").require("OnKeyword").\
            optionally("LightKeyword").build()
        self.register_intent(decora_light_on_intent, self.handle_decora_light_on_intent)

        decora_light_off_intent = IntentBuilder("DecoraWifiOffIntent").\
            require("DeviceKeyword").require("OffKeyword").\
            optionally("LightKeyword").build()
        self.register_intent(decora_light_off_intent, self.handle_decora_light_off_intent)

        decora_light_dim_intent = IntentBuilder("DecoraWifiDimIntent").\
            require("DimKeyword").require("DeviceKeyword").\
            optionally("LightKeyword").build()
        self.register_intent(decora_light_dim_intent, self.handle_decora_light_dim_intent)

        decora_light_set_intent = IntentBuilder("DecoraWifiSetIntent").\
            require("SetKeyword").require("DeviceKeyword").\
            optionally("Lightkeyword").build()
        self.register_intent(decora_light_set_intent, self.handle_decora_light_set_intent)


    # The "handle_xxxx_intent" functions define Mycroft's behavior when
    # each of the skill's intents is triggered: in this case, he simply
    # speaks a response. Note that the "speak_dialog" method doesn't
    # actually speak the text it's passed--instead, that text is the filename
    # of a file in the dialog folder, and Mycroft speaks its contents when
    # the method is called.
    def handle_decora_light_on_intent(self, message):
        mySwitch = getSwitch()
        mySwitch.update_attributes({'power': 'ON', 'brightness': '100'})
        self.speak_dialog("light.on")

    def handle_decora_light_off_intent(self, message):
        mySwitch = getSwitch()
        mySwitch.update_attributes({'power': 'OFF'})
        self.speak_dialog("light.off")

    def handle_decora_light_dim_intent(self, message):
        mySwitch = getSwitch()
        mySwitch.update_attributes({'brightness': '5'})
        self.speak_dialog("light.dim")

    def handle_decora_light_set_intent(self, message):
        str_remainder = str(message.utterance_remainder())
        dim_level = re.findall('\d+', str_remainder)
        if dim_level:
            mySwitch = getSwitch()
            mySwitch.update_attributes({'brightness': dim_level[0]})
            self.speak_dialog("light.set", data={"result": str(dim_level[0])+ ", percent"})

    # The "stop" method defines what Mycroft does when told to stop during
    # the skill's execution. In this case, since the skill's functionality
    # is extremely simple, the method just contains the keyword "pass", which
    # does nothing.
    def stop(self):
        pass

# The "create_skill()" method is used to create an instance of the skill.
# Note that it's outside the class itself.
def create_skill():
    return DecoraWifiSkill()
