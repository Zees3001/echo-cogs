import discord
from discord.ext import commands
from random import randint
import aiohttp
import random
import json
import requests

def setup(bot):
    bot.add_cog(EchoWoW(bot))

LEG_WITH_SOCKET = [
    132369, 132410, 137044, 132444, 132449, 132452, 132460, 133973, 133974, 137037, 137038, 137039, 137040,
    137041, 137042, 137043, 132378, 137045, 137046, 137047, 137048, 137049, 137050, 137051, 137052, 137054, 137055,
    137220, 137223, 137276, 137382, 138854
]

ENCHANTABLE_SLOTS = ["neck", "back", "finger1", "finger2"]

config = {
  "blizzard_api_key": "33weunqrkpvj4zzcbx29tstyjrcubbyn",
  "default_region": "eu",
  "default_server": "Frostwolf"
}
API_KEY = config["blizzard_api_key"]
default_region = config["default_region"]
default_server = config["default_server"]

region_locale = {
    'us': ['us', 'en_US', 'en'],
#    'kr': ['kr', 'ko_KR', 'ko'],
#    'tw': ['tw', 'zh_TW', 'zh'],
    'eu': ['eu', 'en_GB', 'en']
}

def group(n, sep = '.'):
    s = str(abs(n))[::-1]
    groups = []
    i = 0
    while i < len(s):
        groups.append(s[i:i+3])
        i+=3
    retval = sep.join(groups)[::-1]
    if n < 0:
        return '-%s' % retval
    else:
        return retval

def get_sockets(player_dictionary):
    """
    Return dict with total sockets and count of equipped gems and slots that are missing
    :param player_dictionary: Retrieved player dict from API
    :return: dict()
    """
    sockets = 0
    equipped_gems = 0

    for item in player_dictionary["items"]:
        if item in "averageItemLevel" or item in "averageItemLevelEquipped":
            continue

        if int(player_dictionary["items"][item]["id"]) in LEG_WITH_SOCKET:
            sockets += 1
        else:
            for bonus in player_dictionary["items"][item]["bonusLists"]:
                if bonus == 1808:  # 1808 is Legion prismatic socket bonus
                    sockets += 1

            if item in ["neck", "finger1", "finger2"]:
                if player_dictionary["items"][item]["context"] == "trade-skill":
                    sockets += 1                

        for ttip in player_dictionary["items"][item]["tooltipParams"]:
            if item in "mainHand" or item in "offHand":  # Ignore Relic
                continue
            if "gem" in ttip:  # Equipped gems are listed as gem0, gem1, etc...
                equipped_gems += 1

    return {"total_sockets": sockets,
            "equipped_gems": equipped_gems}


def get_enchants(player_dictionary):
    """
    Get count of enchants missing and slots that are missing
    :param player_dictionary:
    :return: dict()
    """
    missing_enchant_slots = []
    for slot in ENCHANTABLE_SLOTS:
        if "enchant" not in player_dictionary["items"][slot]["tooltipParams"]:
            missing_enchant_slots.append(slot)

    return {
        "enchantable_slots": len(ENCHANTABLE_SLOTS),
        "missing_slots": missing_enchant_slots,
        "total_missing": len(missing_enchant_slots)
    }


def get_raid_progression(player_dictionary, raid):
    r = [x for x in player_dictionary["progression"]
    ["raids"] if x["name"] in raid][0]
    normal = 0
    heroic = 0
    mythic = 0

    for boss in r["bosses"]:
        if boss["normalKills"] > 0:
            normal += 1
        if boss["heroicKills"] > 0:
            heroic += 1
        if boss["mythicKills"] > 0:
            mythic += 1

    return {"normal": normal,
            "heroic": heroic,
            "mythic": mythic,
            "total_bosses": len(r["bosses"])}


def get_mythic_progression(player_dictionary):
    achievements = player_dictionary["achievements"]
    plus_two = 0
    plus_five = 0
    plus_ten = 0
    plus_fifteen = 0

    if 33096 in achievements["criteria"]:
        index = achievements["criteria"].index(33096)
        plus_two = achievements["criteriaQuantity"][index]

    if 33097 in achievements["criteria"]:
        index = achievements["criteria"].index(33097)
        plus_five = achievements["criteriaQuantity"][index]

    if 33098 in achievements["criteria"]:
        index = achievements["criteria"].index(33098)
        plus_ten = achievements["criteriaQuantity"][index]

    if 32028 in achievements["criteria"]:
        index = achievements["criteria"].index(32028)
        plus_fifteen = achievements["criteriaQuantity"][index]

    return {
        "plus_two": plus_two,
        "plus_five": plus_five,
        "plus_ten": plus_ten,
        "plus_fifteen": plus_fifteen
    }

def get_artifact_info(player_dictionary):
    ak = 0
    ap = 0
    ar = 0

    achievements = player_dictionary["achievements"]
    items = player_dictionary["items"]

    relicItems = ["mainHand", "offHand"]
    relicCount = 0

    for i in range(len(relicItems)):
        if relicItems[i] in items:
            relicItem = items[relicItems[i]]
            if (relicItem["quality"] == 6):
                artifactRank = 0
                relicCount += len(relicItem["relics"])
    #print("Loop done.")

    if (items["mainHand"]["artifactTraits"][0]):
        for trait in range(len(items["mainHand"]["artifactTraits"])):
            artifactRank += items["mainHand"]["artifactTraits"][trait]["rank"]
            ar = artifactRank - relicCount
    elif (items["offHand"]["artifactTraits"][0]):
        for trait in range(len(items["offHand"]["artifactTraits"])):
            artifactRank += items["offHand"]["artifactTraits"][trait]["rank"]
            ar = artifactRank - relicCount

    if 30103 in achievements["criteria"]:
        index = achievements["criteria"].index(30103)
        ap = achievements["criteriaQuantity"][index]

    if 31466 in achievements["criteria"]:
        index = achievements["criteria"].index(31466)
        ak = achievements["criteriaQuantity"][index]

    return {
        "ar": ar,
        "ap": ap,
        "ak": ak
    }	


def get_char(name, server, target_region):
    r = requests.get("https://%s.api.battle.net/wow/character/%s/%s?fields=items+progression+achievements&locale=%s&apikey=%s" % (
            region_locale[target_region][0], server, name, region_locale[target_region][1], API_KEY))
    
    if r.status_code != 200:
        raise Exception("Could Not Find Character (No 200 from API)")

    player_dict = json.loads(r.text)

    r = requests.get(
        "https://%s.api.battle.net/wow/data/character/classes?locale=%s&apikey=%s" % (
            region_locale[target_region][0], region_locale[target_region][1], API_KEY))
    if r.status_code != 200:
        raise Exception("Could Not Find Character Classes (No 200 From API)")
    class_dict = json.loads(r.text)
    class_dict = {c['id']: c['name'] for c in class_dict["classes"]}

    equipped_ivl = player_dict["items"]["averageItemLevelEquipped"]
    sockets = get_sockets(player_dict)
    enchants = get_enchants(player_dict)
    tov_progress = get_raid_progression(player_dict, "Trial of Valor")
    en_progress = get_raid_progression(player_dict, "The Emerald Nightmare")
    nh_progress = get_raid_progression(player_dict, "The Nighthold")
    mythic_progress = get_mythic_progression(player_dict)
    artifact_info = get_artifact_info(player_dict)

    armory_url = 'http://{}.battle.net/wow/{}/character/{}/{}/advanced'.format(
        region_locale[target_region][0], region_locale[target_region][2], server, name)

    return_string = ''
    return_string += "**%s** - **%s** - **%s %s**\n" % (
        name.title(), server.title(), player_dict['level'], class_dict[player_dict['class']])
    return_string += '<{}>\n'.format(armory_url)
    return_string += '```CSS\n'  # start Markdown

    # iLvL
    return_string += "Equipped Item Level: %s\n" % equipped_ivl

    # Artifact
    return_string += "Artifact Rank: %s (%s) Total Power: %s\n" % (artifact_info["ar"], artifact_info ["ak"], group(artifact_info["ap"]))

    # Mythic Progression
    return_string += "Mythics: +2: %s, +5: %s, +10: %s, +15: %s\n" % (mythic_progress["plus_two"],
                                                             mythic_progress["plus_five"],
                                                             mythic_progress["plus_ten"],
                                                             mythic_progress["plus_fifteen"])

    # Raid Progression
    return_string += "EN: {1}/{0} (N), {2}/{0} (H), {3}/{0} (M)\n".format(en_progress["total_bosses"],
                                                                          en_progress["normal"],
                                                                          en_progress["heroic"],
                                                                          en_progress["mythic"])
    return_string += "TOV: {1}/{0} (N), {2}/{0} (H), {3}/{0} (M)\n".format(tov_progress["total_bosses"],
                                                                           tov_progress["normal"],
                                                                           tov_progress["heroic"],
                                                                           tov_progress["mythic"])
    return_string += "NH: {1}/{0} (N), {2}/{0} (H), {3}/{0} (M)\n".format(nh_progress["total_bosses"],
                                                                           nh_progress["normal"],
                                                                           nh_progress["heroic"],
                                                                           nh_progress["mythic"])

    # Gems
    return_string += "Gems Equipped: %s/%s\n" % (
        sockets["equipped_gems"], sockets["total_sockets"])

    # Enchants
    return_string += "Enchants: %s/%s\n" % (enchants["enchantable_slots"] - enchants["total_missing"],
                                            enchants["enchantable_slots"])
    if enchants["total_missing"] > 0:
        return_string += "Missing Enchants: {0}".format(
            ", ".join(enchants["missing_slots"]))

    return_string += '```'  # end Markdown
    return return_string

class EchoWoW:
    """echo wow commands."""

    def __init__(self, bot):
        self.bot = bot
        #Reserved for further ...

    """Commands section"""

    @commands.command(no_pm=True)
    async def wowcheck(self, *text):
        target_region = default_region
        target_server = default_server      
        try:
            name = text[0]
            if len(text) == 2 and text[1].lower() not in region_locale.keys():
                target_server = text[1].lower()
            if len(text) == 3 and text[2].lower() in region_locale.keys():
                target_server = text[1].lower()
                target_region = text[2].lower()
            character_info = get_char(name, target_server, target_region)
            await self.bot.say(character_info)
        except Exception as e:
            print(e)
            await self.bot.say("Error With Name or Server\n"
                               "Use: ?wowcheck <name> <opt. server> <opt. region>\n"
                               "Hyphenate Two Word Servers (Ex: Twisting-Nether)")

class ModuleNotFound(Exception):
    def __init__(self, m):
        self.message = m
    def __str__(self):
        return self.message
