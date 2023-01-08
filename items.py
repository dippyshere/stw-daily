"""
STW Daily Discord bot Copyright 2023 by the STW Daily team.
Please do not skid our hard work.
https://github.com/dippyshere/stw-daily

This file is used as a datatable for Fortnite's daily rewards.
Initially compiled by dippyshere, later revised by PRO100KatYT, eventually updated for rewrite by jean1398reborn
"""

# this is misspelt, but I am not bothered to fix it
# i am
ItemDictionary = {
    "1": ["300 Hero XP", "heroxp"],
    "2": ["2 Mini Llamas", "minillama"],
    "3": ["Rare Hero", "herogeneric"],
    "4": ["Rare Ranged Weapon", "rangedgeneric"],
    "5": ["Rare Melee Weapon", "meleegeneric"],
    "6": ["5 Pure Drops of Rain", "pdor"],
    "7": ["Rare Freedom's Herald Pistol", "freedoms_herald"],
    "8": ["Rare Trap", "trapgeneric"],
    "9": ["Rare Defender", "defendergeneric"],
    "10": ["Epic Hero", "herogeneric"],
    "11": ["50 V-Bucks & X-Ray Tickets", "mtxswap_combined"],
    "12": ["Epic Lead Survivor", "leadsurvivor"],
    "13": ["3 XP Boosts", "xpboost"],
    "14": ["Epic Survivor", "survivorgeneric"],
    "15": ["Mini Llama", "minillama"],
    "16": ["20 Gold", "gold"],
    "17": ["15 Pure Drops of Rain", "pdor"],
    "18": ["Upgrade Llama", "llama"],
    "19": ["Rare Trap", "trapgeneric"],
    "20": ["5 Lightning in a Bottle", "bottlelightning"],
    "21": ["Legendary Hero", "herogeneric"],
    "22": ["15 Pure Drops of Rain", "pdor"],
    "23": ["20 Gold", "gold"],
    "24": ["2 Mini Llamas", "minillama"],
    "25": ["Rare Melee Weapon", "meleegeneric"],
    "26": ["Upgrade Llama", "llama"],
    "27": ["5 Eye of the Storm", "stormeye"],
    "28": ["300 V-Bucks & X-Ray Tickets", "mtxswap_combined"],
    "29": ["2 Mini Llamas", "minillama"],
    "30": ["10 Pure Drops of Rain", "pdor"],
    "31": ["Rare Hero", "herogeneric"],
    "32": ["20 Gold", "gold"],
    "33": ["Upgrade Llama", "llama"],
    "34": ["3 XP Boosts", "xpboost"],
    "35": ["150 V-Bucks & X-Ray Tickets", "mtxswap_combined"],
    "36": ["20 Gold", "gold"],
    # Lil Nas X - MONTERO (Call Me By Your Name) [SATAN’S EXTENDED VERSION] thank you for coming to my ted talk
    "37": ["10 Pure Drops of Rain", "pdor"],
    "38": ["Rare Ranged Weapon", "rangedgeneric"],
    "39": ["5 Lightning in a Bottle", "bottlelightning"],
    "40": ["Upgrade Llama", "llama"],
    "41": ["3 Teammate XP Boosts", "teammatexpboost"],
    "42": ["Epic Lead Survivor", "leadsurvivor"],
    "43": ["2 Mini Llamas", "minillama"],
    "44": ["20 Gold", "gold"],
    "45": ["15 Pure Drops of Rain", "pdor"],
    "46": ["Upgrade Llama", "llama"],
    "47": ["Rare Trap", "trapgeneric"],
    "48": ["5 Lightning in a Bottle", "bottlelightning"],
    "49": ["150 V-Bucks & X-Ray Tickets", "mtxswap_combined"],
    "50": ["15 Pure Drops of Rain", "pdor"],
    "51": ["20 Gold", "gold"],
    "52": ["2 Mini Llamas", "minillama"],
    "53": ["Rare Melee Weapon", "meleegeneric"],
    "54": ["Upgrade Llama", "llama"],
    "55": ["5 Eye of the Storm", "stormeye"],
    "56": ["300 V-Bucks & X-Ray Tickets", "mtxswap_combined"],
    "57": ["2 Mini Llamas", "minillama"],
    "58": ["10 Pure Drops of Rain", "pdor"],
    "59": ["Rare Hero", "herogeneric"],
    "60": ["20 Gold", "gold"],
    "61": ["Upgrade Llama", "llama"],
    "62": ["3 XP Boosts", "xpboost"],
    "63": ["Legendary Survivor", "survivorgeneric"],
    "64": ["20 Gold", "gold"],
    "65": ["10 Pure Drops of Rain", "pdor"],
    "66": ["Rare Ranged Weapon", "rangedgeneric"],
    "67": ["5 Lightning in a Bottle", "bottlelightning"],
    "68": ["Upgrade Llama", "llama"],
    "69": ["3 Teammate XP Boosts", "teammatexpboost"],
    "70": ["150 V-Bucks & X-Ray Tickets", "mtxswap_combined"],
    "71": ["2 Mini Llamas", "minillama"],
    "72": ["20 Gold", "gold"],
    "73": ["15 Pure Drops of Rain", "pdor"],
    "74": ["Upgrade Llama", "llama"],
    "75": ["Rare Trap", "trapgeneric"],
    "76": ["5 Lightning in a Bottle", "bottlelightning"],
    "77": ["150 V-Bucks & X-Ray Tickets", "mtxswap_combined"],
    "78": ["15 Pure Drops of Rain", "pdor"],
    "79": ["20 Gold", "gold"],
    "80": ["2 Mini Llamas", "minillama"],
    "81": ["Legendary Survivor", "survivorgeneric"],
    "82": ["Upgrade Llama", "llama"],
    "83": ["5 Eye of the Storm", "stormeye"],
    "84": ["300 V-Bucks & X-Ray Tickets", "mtxswap_combined"],
    "85": ["2 Mini Llamas", "minillama"],
    "86": ["10 Pure Drops of Rain", "pdor"],
    "87": ["Rare Hero", "herogeneric"],
    "88": ["20 Gold", "gold"],
    "89": ["Upgrade Llama", "llama"],
    "90": ["3 XP Boosts", "xpboost"],
    "91": ["150 V-Bucks & X-Ray Tickets", "mtxswap_combined"],
    "92": ["20 Gold", "gold"],
    "93": ["10 Pure Drops of Rain", "pdor"],
    "94": ["Rare Ranged Weapon", "rangedgeneric"],
    "95": ["5 Lightning in a Bottle", "bottlelightning"],
    "96": ["Upgrade Llama", "llama"],
    "97": ["3 Teammate XP Boosts", "teammatexpboost"],
    "98": ["150 V-Bucks & X-Ray Tickets", "mtxswap_combined"],
    "99": ["2 Mini Llamas", "minillama"],
    "100": ["Legendary Hero", "herogeneric"],
    "101": ["15 Pure Drops of Rain", "pdor"],
    "102": ["Upgrade Llama", "llama"],
    "103": ["Rare Trap", "trapgeneric"],
    "104": ["5 Lightning in a Bottle", "bottlelightning"],
    "105": ["150 V-Bucks & X-Ray Tickets", "mtxswap_combined"],
    "106": ["15 Pure Drops of Rain", "pdor"],
    "107": ["20 Gold", "gold"],
    "108": ["2 Mini Llamas", "minillama"],
    "109": ["Rare Melee Weapon", "meleegeneric"],
    "110": ["Upgrade Llama", "llama"],
    "111": ["5 Eye of the Storm", "stormeye"],
    "112": ["800 V-Bucks & X-Ray Tickets", "mtxswap_combined"],
    "113": ["2 Mini Llamas", "minillama"],
    "114": ["10 Pure Drops of Rain", "pdor"],
    "115": ["Rare Hero", "herogeneric"],
    "116": ["20 Gold", "gold"],
    "117": ["Upgrade Llama", "llama"],
    "118": ["3 XP Boosts", "xpboost"],
    "119": ["150 V-Bucks & X-Ray Tickets", "mtxswap_combined"],
    "120": ["20 Gold", "gold"],
    "121": ["10 Pure Drops of Rain", "pdor"],
    "122": ["Rare Ranged Weapon", "rangedgeneric"],
    "123": ["5 Lightning in a Bottle", "bottlelightning"],
    "124": ["Upgrade Llama", "llama"],
    "125": ["3 Teammate XP Boosts", "teammatexpboost"],
    "126": ["150 V-Bucks & X-Ray Tickets", "mtxswap_combined"],
    "127": ["2 Mini Llamas", "minillama"],
    "128": ["20 Gold", "gold"],
    "129": ["15 Pure Drops of Rain", "pdor"],
    "130": ["Upgrade Llama", "llama"],
    "131": ["Rare Trap", "trapgeneric"],
    "132": ["5 Lightning in a Bottle", "bottlelightning"],
    "133": ["150 V-Bucks & X-Ray Tickets", "mtxswap_combined"],
    "134": ["15 Pure Drops of Rain", "pdor"],
    "135": ["20 Gold", "gold"],
    "136": ["2 Mini Llamas", "minillama"],
    "137": ["Rare Melee Weapon", "meleegeneric"],
    "138": ["Upgrade Llama", "llama"],
    "139": ["5 Eye of the Storm", "stormeye"],
    "140": ["300 V-Bucks & X-Ray Tickets", "mtxswap_combined"],
    "141": ["2 Mini Llamas", "minillama"],
    "142": ["10 Pure Drops of Rain", "pdor"],
    "143": ["Rare Hero", "herogeneric"],
    "144": ["20 Gold", "gold"],
    "145": ["Upgrade Llama", "llama"],
    "146": ["3 XP Boosts", "xpboost"],
    "147": ["150 V-Bucks & X-Ray Tickets", "mtxswap_combined"],
    "148": ["20 Gold", "gold"],
    "149": ["10 Pure Drops of Rain", "pdor"],
    "150": ["Rare Ranged Weapon", "rangedgeneric"],
    "151": ["5 Lightning in a Bottle", "bottlelightning"],
    "152": ["Upgrade Llama", "llama"],
    "153": ["3 Teammate XP Boosts", "teammatexpboost"],
    "154": ["150 V-Bucks & X-Ray Tickets", "mtxswap_combined"],
    "155": ["2 Mini Llamas", "minillama"],
    "156": ["20 Gold", "gold"],
    "157": ["15 Pure Drops of Rain", "pdor"],
    "158": ["Upgrade Llama", "llama"],
    "159": ["Rare Trap", "trapgeneric"],
    "160": ["5 Lightning in a Bottle", "bottlelightning"],
    "161": ["150 V-Bucks & X-Ray Tickets", "mtxswap_combined"],
    "162": ["15 Pure Drops of Rain", "pdor"],
    "163": ["20 Gold", "gold"],
    "164": ["2 Mini Llamas", "minillama"],
    "165": ["Rare Melee Weapon", "meleegeneric"],
    "166": ["Upgrade Llama", "llama"],
    "167": ["5 Eye of the Storm", "stormeye"],
    "168": ["300 V-Bucks & X-Ray Tickets", "mtxswap_combined"],
    "169": ["2 Mini Llamas", "minillama"],
    "170": ["10 Pure Drops of Rain", "pdor"],
    "171": ["Rare Hero", "herogeneric"],
    "172": ["20 Gold", "gold"],
    "173": ["Upgrade Llama", "llama"],
    "174": ["3 XP Boosts", "xpboost"],
    "175": ["150 V-Bucks & X-Ray Tickets", "mtxswap_combined"],
    "176": ["20 Gold", "gold"],
    "177": ["10 Pure Drops of Rain", "pdor"],
    "178": ["Rare Ranged Weapon", "rangedgeneric"],
    "179": ["5 Lightning in a Bottle", "bottlelightning"],
    "180": ["Upgrade Llama", "llama"],
    "181": ["3 Teammate XP Boosts", "teammatexpboost"],
    "182": ["150 V-Bucks & X-Ray Tickets", "mtxswap_combined"],
    "183": ["2 Mini Llamas", "minillama"],
    "184": ["20 Gold", "gold"],
    "185": ["15 Pure Drops of Rain", "pdor"],
    "186": ["Upgrade Llama", "llama"],
    "187": ["Rare Trap", "trapgeneric"],
    "188": ["5 Lightning in a Bottle", "bottlelightning"],
    "189": ["150 V-Bucks & X-Ray Tickets", "mtxswap_combined"],
    "190": ["15 Pure Drops of Rain", "pdor"],
    "191": ["20 Gold", "gold"],
    "192": ["2 Mini Llamas", "minillama"],
    "193": ["Rare Melee Weapon", "meleegeneric"],
    "194": ["Upgrade Llama", "llama"],
    "195": ["5 Eye of the Storm", "stormeye"],
    "196": ["300 V-Bucks & X-Ray Tickets", "mtxswap_combined"],
    "197": ["2 Mini Llamas", "minillama"],
    "198": ["10 Pure Drops of Rain", "pdor"],
    "199": ["Rare Hero", "herogeneric"],
    "200": ["20 Gold", "gold"],
    "201": ["Upgrade Llama", "llama"],
    "202": ["3 XP Boosts", "xpboost"],
    "203": ["150 V-Bucks & X-Ray Tickets", "mtxswap_combined"],
    "204": ["20 Gold", "gold"],
    "205": ["10 Pure Drops of Rain", "pdor"],
    "206": ["Rare Ranged Weapon", "rangedgeneric"],
    "207": ["5 Lightning in a Bottle", "bottlelightning"],
    "208": ["Upgrade Llama", "llama"],
    "209": ["3 Teammate XP Boosts", "teammatexpboost"],
    "210": ["150 V-Bucks & X-Ray Tickets", "mtxswap_combined"],
    "211": ["2 Mini Llamas", "minillama"],
    "212": ["20 Gold", "gold"],
    "213": ["15 Pure Drops of Rain", "pdor"],
    "214": ["Upgrade Llama", "llama"],
    "215": ["Rare Trap", "trapgeneric"],
    "216": ["5 Lightning in a Bottle", "bottlelightning"],
    "217": ["150 V-Bucks & X-Ray Tickets", "mtxswap_combined"],
    "218": ["15 Pure Drops of Rain", "pdor"],
    "219": ["20 Gold", "gold"],
    "220": ["2 Mini Llamas", "minillama"],
    "221": ["Rare Melee Weapon", "meleegeneric"],
    "222": ["Upgrade Llama", "llama"],
    "223": ["5 Eye of the Storm", "stormeye"],
    "224": ["800 V-Bucks & X-Ray Tickets", "mtxswap_combined"],
    "225": ["2 Mini Llamas", "minillama"],
    "226": ["10 Pure Drops of Rain", "pdor"],
    "227": ["Rare Hero", "herogeneric"],
    "228": ["20 Gold", "gold"],
    "229": ["Upgrade Llama", "llama"],
    "230": ["3 XP Boosts", "xpboost"],
    "231": ["150 V-Bucks & X-Ray Tickets", "mtxswap_combined"],
    "232": ["20 Gold", "gold"],
    "233": ["10 Pure Drops of Rain", "pdor"],
    "234": ["Rare Ranged Weapon", "rangedgeneric"],
    "235": ["5 Lightning in a Bottle", "bottlelightning"],
    "236": ["Upgrade Llama", "llama"],
    "237": ["3 Teammate XP Boosts", "teammatexpboost"],
    "238": ["150 V-Bucks & X-Ray Tickets", "mtxswap_combined"],
    "239": ["2 Mini Llamas", "minillama"],
    "240": ["20 Gold", "gold"],
    "241": ["15 Pure Drops of Rain", "pdor"],
    "242": ["Upgrade Llama", "llama"],
    "243": ["Rare Trap", "trapgeneric"],
    "244": ["5 Lightning in a Bottle", "bottlelightning"],
    "245": ["150 V-Bucks & X-Ray Tickets", "mtxswap_combined"],
    "246": ["15 Pure Drops of Rain", "pdor"],
    "247": ["20 Gold", "gold"],
    "248": ["2 Mini Llamas", "minillama"],
    "249": ["Rare Melee Weapon", "meleegeneric"],
    "250": ["Upgrade Llama", "llama"],
    "251": ["5 Eye of the Storm", "stormeye"],
    "252": ["300 V-Bucks & X-Ray Tickets", "mtxswap_combined"],
    "253": ["2 Mini Llamas", "minillama"],
    "254": ["10 Pure Drops of Rain", "pdor"],
    "255": ["Rare Hero", "herogeneric"],
    "256": ["20 Gold", "gold"],
    "257": ["Upgrade Llama", "llama"],
    "258": ["3 XP Boosts", "xpboost"],
    "259": ["150 V-Bucks & X-Ray Tickets", "mtxswap_combined"],
    "260": ["20 Gold", "gold"],
    "261": ["10 Pure Drops of Rain", "pdor"],
    "262": ["Rare Ranged Weapon", "rangedgeneric"],
    "263": ["5 Lightning in a Bottle", "bottlelightning"],
    "264": ["Upgrade Llama", "llama"],
    "265": ["3 Teammate XP Boosts", "teammatexpboost"],
    "266": ["150 V-Bucks & X-Ray Tickets", "mtxswap_combined"],
    "267": ["2 Mini Llamas", "minillama"],
    "268": ["20 Gold", "gold"],
    "269": ["15 Pure Drops of Rain", "pdor"],
    "270": ["Upgrade Llama", "llama"],
    "271": ["Rare Trap", "trapgeneric"],
    "272": ["5 Lightning in a Bottle", "bottlelightning"],
    "273": ["150 V-Bucks & X-Ray Tickets", "mtxswap_combined"],
    "274": ["15 Pure Drops of Rain", "pdor"],
    "275": ["20 Gold", "gold"],
    "276": ["2 Mini Llamas", "minillama"],
    "277": ["Rare Melee Weapon", "meleegeneric"],
    "278": ["Upgrade Llama", "llama"],
    "279": ["5 Eye of the Storm", "stormeye"],
    "280": ["300 V-Bucks & X-Ray Tickets", "mtxswap_combined"],
    "281": ["2 Mini Llamas", "minillama"],
    "282": ["10 Pure Drops of Rain", "pdor"],
    "283": ["Rare Hero", "herogeneric"],
    "284": ["20 Gold", "gold"],
    "285": ["Upgrade Llama", "llama"],
    "286": ["3 XP Boosts", "xpboost"],
    "287": ["150 V-Bucks & X-Ray Tickets", "mtxswap_combined"],
    "288": ["20 Gold", "gold"],
    "289": ["10 Pure Drops of Rain", "pdor"],
    "290": ["Rare Ranged Weapon", "rangedgeneric"],
    "291": ["5 Lightning in a Bottle", "bottlelightning"],
    "292": ["Upgrade Llama", "llama"],
    "293": ["3 Teammate XP Boosts", "teammatexpboost"],
    "294": ["150 V-Bucks & X-Ray Tickets", "mtxswap_combined"],
    "295": ["2 Mini Llamas", "minillama"],
    "296": ["20 Gold", "gold"],
    "297": ["15 Pure Drops of Rain", "pdor"],
    "298": ["Upgrade Llama", "llama"],
    "299": ["Rare Trap", "trapgeneric"],
    "300": ["5 Lightning in a Bottle", "bottlelightning"],
    "301": ["150 V-Bucks & X-Ray Tickets", "mtxswap_combined"],
    "302": ["15 Pure Drops of Rain", "pdor"],
    "303": ["20 Gold", "gold"],
    "304": ["2 Mini Llamas", "minillama"],
    "305": ["Rare Melee Weapon", "meleegeneric"],
    "306": ["Upgrade Llama", "llama"],
    "307": ["5 Eye of the Storm", "stormeye"],
    "308": ["300 V-Bucks & X-Ray Tickets", "mtxswap_combined"],
    "309": ["2 Mini Llamas", "minillama"],
    "310": ["10 Pure Drops of Rain", "pdor"],
    "311": ["Rare Hero", "herogeneric"],
    "312": ["20 Gold", "gold"],
    "313": ["Upgrade Llama", "llama"],
    "314": ["3 XP Boosts", "xpboost"],
    "315": ["150 V-Bucks & X-Ray Tickets", "mtxswap_combined"],
    "316": ["20 Gold", "gold"],
    "317": ["10 Pure Drops of Rain", "pdor"],
    "318": ["Rare Ranged Weapon", "rangedgeneric"],
    "319": ["5 Lightning in a Bottle", "bottlelightning"],
    "320": ["Upgrade Llama", "llama"],
    "321": ["3 Teammate XP Boosts", "teammatexpboost"],
    "322": ["150 V-Bucks & X-Ray Tickets", "mtxswap_combined"],
    "323": ["2 Mini Llamas", "minillama"],
    "324": ["20 Gold", "gold"],
    "325": ["15 Pure Drops of Rain", "pdor"],
    "326": ["Upgrade Llama", "llama"],
    "327": ["Rare Trap", "trapgeneric"],
    "328": ["5 Lightning in a Bottle", "bottlelightning"],
    "329": ["150 V-Bucks & X-Ray Tickets", "mtxswap_combined"],
    "330": ["15 Pure Drops of Rain", "pdor"],
    "331": ["20 Gold", "gold"],
    "332": ["2 Mini Llamas", "minillama"],
    "333": ["Rare Melee Weapon", "meleegeneric"],
    "334": ["Upgrade Llama", "llama"],
    "335": ["5 Eye of the Storm", "stormeye"],
    "336": ["1000 V-Bucks & X-Ray Tickets", "celebrate", "mtxswap_combined", "celebrate"],
}
