"""
STW Daily Discord bot Copyright 2023 by the STW Daily team.
Please do not skid our hard work.
https://github.com/dippyshere/stw-daily

This file is used as a datatable for Fortnite's daily rewards.
Initially compiled by dippyshere, later revised by PRO100KatYT, eventually updated for rewrite by jean1398reborn
Rewritten by dippyshere to use game datatables and support multiple languages.
"""

# this is misspelt, but I am not bothered to fix it
# i am
LootTable = {
    "/Game/Items/PersistentResources/HeroXP.HeroXP": ["heroxp", "Hero XP", "Used to level heroes and defenders. Can be found in llamas and by retiring heroes or defenders."],
    "/Game/Items/PersistentResources/Voucher_BasicPack.Voucher_BasicPack": ["minillama", "Mini Reward Llama", "Claim your free reward llama in the Loot tab."],
    "/SaveTheWorld/Items/CardPacks/GenericRewards/CardPack_Hero_R.CardPack_Hero_R": ["herogeneric", "Rare Hero", "One random hero."],
    "/SaveTheWorld/Items/CardPacks/GenericRewards/CardPack_Ranged_R.CardPack_Ranged_R": ["rangedgeneric", "Rare Ranged Weapon Schematic", "One random ranged weapon schematic."],
    "/SaveTheWorld/Items/CardPacks/GenericRewards/CardPack_Melee_R.CardPack_Melee_R": ["meleegeneric", "Rare Melee Weapon Schematic", "One random melee weapon schematic."],
    "/Game/Items/PersistentResources/Reagent_C_T01.Reagent_C_T01": ["pdor", "Pure Drop of Rain", "Resource used to evolve all types of items."],
    "/SaveTheWorld/Items/Schematics/Ranged/Pistol/FireCracker/SID_Pistol_FireCracker_R_Ore_T01.SID_Pistol_FireCracker_R_Ore_T01": ["freedoms_herald", "Freedom's Herald", "Pistol: Special. Launches firecrackers that bounce off walls, and will knockback and damage enemies in a small radius when they explode."],
    "/SaveTheWorld/Items/CardPacks/GenericRewards/CardPack_Trap_R.CardPack_Trap_R": ["trapgeneric", "Rare Trap Schematic", "One random trap schematic."],
    "/SaveTheWorld/Items/CardPacks/GenericRewards/CardPack_Defender_R.CardPack_Defender_R": ["defendergeneric", "Rare Defender", "One random defender."],
    "/SaveTheWorld/Items/CardPacks/GenericRewards/CardPack_Hero_VR.CardPack_Hero_VR": ["herogeneric", "Epic Hero", "One random hero."],
    "/Game/Items/PersistentResources/Currency_MtxSwap.Currency_MtxSwap": ["mtxswap_combined", "V-Bucks Voucher", "Turns into X-Ray Tickets for everyone, and also V-Bucks if you have a Founders account."],
    "/Game/Items/PersistentResources/Currency_XRayLlama.Currency_XRayLlama": ["xray", "X-Ray Tickets", "Currency earned by completing Daily Quests, Storm Shield Defenses, and some Mission Alerts. Traded for X-Ray Llamas in the Llama Shop."],
    "/Game/Items/PersistentResources/Currency_Hybrid_MTX_XRayLlama.Currency_Hybrid_MTX_XRayLlama": ["mtxswap_combined", "V-Bucks and X-Ray Tickets", "Turns into X-Ray Tickets for everyone, and also V-Bucks if you have a Founders account."],
    "/SaveTheWorld/Items/CardPacks/GenericRewards/CardPack_Manager_R.CardPack_Manager_R": ["leadsurvivor", "Rare Lead Survivor", "One random lead survivor."],
    "/Game/Items/AccountConsumables/SmallXpBoost.SmallXpBoost": ["xpboost", "XP Boost", "Activate an XP Boost to gain Account XP boost points. Boost points earn {0} more experience for yourself, as well as give a {0} bonus to all other players on your team! If you are a Founder, you automatically grant a 5% bonus to all your team mates. The more players that use XP Boosts, the bigger the bonus for everyone!"],
    "/SaveTheWorld/Items/CardPacks/GenericRewards/CardPack_Worker_VR.CardPack_Worker_VR": ["survivorgeneric", "Epic Survivor", "One random survivor."],
    "/Game/Items/PersistentResources/EventCurrency_Scaling.EventCurrency_Scaling": ["gold", "Gold", "Special currency earned by completing missions and opening mini llamas. Can be traded for items in the Event Store."],
    "/Game/Items/CardPacks/CardPack_Bronze.CardPack_Bronze": ["pinatastandardpackupgrade", "Upgrade Llama", "The old faithful llama, packed with a variety of goodies and upgrade materials. Contains at least 4 items, including a rare item or a hero! Has a high chance to upgrade."],
    "/Game/Items/PersistentResources/Reagent_C_T02.Reagent_C_T02": ["bottlelightning", "5 Lightning in a Bottle", "Resource used to evolve all types of items. Found primarily in Plankerton."],
    "/SaveTheWorld/Items/CardPacks/GenericRewards/CardPack_Hero_SR.CardPack_Hero_SR": ["herogeneric", "Legendary Hero", "One random hero."],
    "/Game/Items/PersistentResources/Reagent_C_T03.Reagent_C_T03": ["stormeye", "Eye of the Storm", "Resource used to evolve all types of items. Found primarily in Canny Valley."],
    # Lil Nas X - MONTERO (Call Me By Your Name) [SATAN’S EXTENDED VERSION] thank you for coming to my ted talk
    "/Game/Items/AccountConsumables/SmallXpBoost_Gift.SmallXpBoost_Gift": ["teammatexpboost", "3 Teammate XP Boosts", "Activate a Teammate XP Boost to give a teammate Account XP boost points. Boost points earn {0} more experience for a teammate, as well as give a {1} bonus to you and the other players on your team!  The more players that use XP Boosts, the bigger the bonus for everyone!"],
    "/SaveTheWorld/Items/CardPacks/GenericRewards/CardPack_Worker_SR.CardPack_Worker_SR": ["survivorgeneric", "Legendary Survivor", "One random survivor."],
    "/SaveTheWorld/Items/CardPacks/Events/Release/CardPack_Event_Founders.CardPack_Event_Founders": ["foundersllama", "Founder's Llama", "A special event pack! Guarantees one Founder's Epic weapon with a powerful level 5 perk."]
}
