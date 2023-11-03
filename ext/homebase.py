"""
STW Daily Discord bot Copyright 2023 by the STW Daily team.
Please do not skid our hard work.
https://github.com/dippyshere/stw-daily

This file is the cog for the homebase command. renames homebase / displays current name + renders banner
"""

import discord
import discord.ext.commands as ext
from discord import Option, OptionChoice
import orjson
import logging

import stwutil as stw

logger = logging.getLogger(__name__)


class Homebase(ext.Cog):
    """
    Cog for the homebase command
    """

    def __init__(self, client):
        self.client = client
        self.emojis = client.config["emojis"]

    async def check_errors(self, ctx, public_json_response, auth_info, final_embeds, name="", desired_lang="en"):
        """
        Checks for errors in the public_json_response and edits the original message if an error is found.

        Args:
            ctx: The context of the command.
            public_json_response: The json response from the public API.
            auth_info: The auth_info tuple from get_or_create_auth_session.
            final_embeds: The list of embeds to be edited.
            name: The attempted name of the homebase. Used to check if empty (for no stw)
            desired_lang: The desired language for the error message.

        Returns:
            True if an error is found, False otherwise.
        """
        # if "errorCode" in public_json_response:
        try:
            # general error
            error_code = public_json_response["errorCode"]
            acc_name = auth_info[1]["account_name"]
            embed = await stw.post_error_possibilities(ctx, self.client, "homebase", acc_name, error_code,
                                                       verbiage_action="hbrn",
                                                       desired_lang=desired_lang)
            final_embeds.append(embed)
            await stw.slash_edit_original(ctx, auth_info[0], final_embeds)
            return error_code, True
        except:
            try:
                # if there is a homebase name, continue with command
                # check_hbname = public_json_response["profileChanges"][0]["profile"]["stats"]["attributes"][
                #     "homebase_name"]
                return False, False
            except:
                # trying to check homebase with no stw or homebase, assume error
                # if name == "":
                #     acc_name = auth_info[1]["account_name"]
                #     error_code = "errors.com.epicgames.fortnite.check_access_failed"
                #     embed = await stw.post_error_possibilities(ctx, self.client, "homebase", acc_name, error_code,
                #                                                verbiage_action="hbrn",
                #                                                desired_lang=desired_lang)
                #     final_embeds.append(embed)
                #     await stw.slash_edit_original(ctx, auth_info[0], final_embeds)
                #     return error_code, True
                # allow name change for no stw because it works somehow
                return False, False

    async def hbrename_command(self, ctx, name, authcode, auth_opt_out):
        """
        The main function for the homebase command.

        Args:
            ctx: The context of the command.
            name: The name to change the homebase to.
            authcode: The authcode to use for the command.
            auth_opt_out: Whether or not to opt out of authcode usage.

        Returns:
            None
        """

        desired_lang = await stw.I18n.get_desired_lang(self.client, ctx)

        succ_colour = self.client.colours["success_green"]
        white = self.client.colours["auth_white"]

        auth_info = await stw.get_or_create_auth_session(self.client, ctx, "homebase", authcode, auth_opt_out, True,
                                                         desired_lang=desired_lang)
        if not auth_info[0]:
            return

        final_embeds = []

        ainfo3 = ""
        try:
            ainfo3 = auth_info[3]
        except:
            pass

        # what is this black magic???????? I totally forgot what any of this is and how is there a third value to the auth_info??
        # okay I discovered what it is, it's basically the "welcome whoever" embed that is edited
        if ainfo3 != "logged_in_processing" and auth_info[2] != []:
            final_embeds = auth_info[2]

        # get public info about current Homebase name
        public_request = await stw.profile_request(self.client, "query_public", auth_info[1],
                                                   profile_id="common_public")
        public_json_response = orjson.loads(await public_request.read())
        logger.debug(f"Query Public response: {public_json_response}")

        # stw_request = await stw.profile_request(self.client, "query_public", auth_info[1])
        # stw_json_response = orjson.loads(await stw_request.read())
        # ROOT.profileChanges[0].profile.stats.attributes.homebase_name

        file = None
        # check for le error code
        error_check = await self.check_errors(ctx, public_json_response, auth_info, final_embeds, name, desired_lang)
        if error_check[1]:
            return
        elif error_check[0] == "errors.stwdaily.no_stw":
            br_request = await stw.profile_request(self.client, "query", auth_info[1], profile_id="br")
            br_json_response = orjson.loads(await br_request.read())
            current = " "
            try:
                homebase_icon = br_json_response["profileChanges"][0]["profile"]["items"][br_json_response["profileChanges"][0]["profile"]["stats"]["attributes"]["last_applied_loadout"]]["attributes"]["banner_icon_template"]
            except KeyError:
                homebase_icon = "placeholder"
            try:
                homebase_colour = br_json_response["profileChanges"][0]["profile"]["items"][br_json_response["profileChanges"][0]["profile"]["stats"]["attributes"]["last_applied_loadout"]]["attributes"]["banner_color_template"]
            except KeyError:
                homebase_colour = "DefaultColor1"
        else:
            stw_request = await stw.profile_request(self.client, "query", auth_info[1])
            stw_json_response = orjson.loads(await stw_request.read())
            # extract info from response
            try:
                current = public_json_response["profileChanges"][0]["profile"]["stats"]["attributes"]["homebase_name"]
            except:
                current = " "
            try:
                homebase_icon = stw_json_response["profileChanges"][0]["profile"]["items"][stw_json_response["profileChanges"][0]["profile"]["stats"]["attributes"]["last_applied_loadout"]]["attributes"]["banner_icon_template"]
                try:
                    homebase_colour = stw_json_response["profileChanges"][0]["profile"]["items"][stw_json_response["profileChanges"][0]["profile"]["stats"]["attributes"]["last_applied_loadout"]]["attributes"]["banner_color_template"]
                except KeyError:
                    try:
                        homebase_colour = public_json_response["profileChanges"][0]["profile"]["stats"]["attributes"]["banner_color"]
                    except:
                        homebase_colour = "DefaultColor1"
            except KeyError:
                try:
                    homebase_icon = public_json_response["profileChanges"][0]["profile"]["stats"]["attributes"]["banner_icon"]
                except:
                    try:
                        br_request = await stw.profile_request(self.client, "query", auth_info[1], profile_id="br")
                        br_json_response = orjson.loads(await br_request.read())
                        try:
                            homebase_icon = br_json_response["profileChanges"][0]["profile"]["items"][br_json_response["profileChanges"][0]["profile"]["stats"]["attributes"]["last_applied_loadout"]]["attributes"]["banner_icon_template"]
                        except KeyError:
                            homebase_icon = "placeholder"
                        try:
                            homebase_colour = br_json_response["profileChanges"][0]["profile"]["items"][br_json_response["profileChanges"][0]["profile"]["stats"]["attributes"]["last_applied_loadout"]]["attributes"]["banner_color_template"]
                        except KeyError:
                            homebase_colour = "DefaultColor1"
                    except:
                        homebase_icon = "placeholder"

        # Empty name should fetch current name
        if name == "":
            embed = discord.Embed(
                title=await stw.add_emoji_title(self.client, stw.I18n.get("homebase.embed.title", desired_lang),
                                                "storm_shield"),
                description=f"\u200b\n"
                            f"{stw.I18n.get('homebase.embed.description', desired_lang)}\n"
                            f"```{current}```\u200b", colour=white)
            if homebase_icon != "placeholder":
                try:
                    embed, file = await stw.generate_banner(self.client, embed, homebase_icon, homebase_colour,
                                                            ctx.author.id)
                    colour = await stw.get_banner_colour(homebase_colour, "rgb")
                    embed.colour = discord.Colour.from_rgb(colour[0], colour[1], colour[2])
                except:
                    embed.set_thumbnail(url=self.client.config["thumbnails"]["placeholder"])
            else:
                embed.set_thumbnail(url=self.client.config["thumbnails"]["placeholder"])
            embed = await stw.add_requested_footer(ctx, embed, desired_lang)
            final_embeds.append(embed)
            if file is not None:
                await stw.slash_edit_original(ctx, auth_info[0], final_embeds, files=file)
                return
            await stw.slash_edit_original(ctx, auth_info[0], final_embeds)
            return

        # failing these checks means the name has problems thus we cannot accept it
        if len(name) > 16:
            error_code = "errors.stwdaily.homebase_long"
            embed = await stw.post_error_possibilities(ctx, self.client, "homebase", name, error_code,
                                                       verbiage_action="hbrn",
                                                       desired_lang=desired_lang)
            final_embeds.append(embed)
            await stw.slash_edit_original(ctx, auth_info[0], final_embeds)
            return
        name_validation = await stw.validate_homebase_name(name)
        if not name_validation[0]:
            error_code = "errors.stwdaily.homebase_illegal"
            embed = await stw.post_error_possibilities(ctx, self.client, "homebase", name, error_code,
                                                       verbiage_action="hbrn",
                                                       hb_badchars=name_validation[1],
                                                       desired_lang=desired_lang)
            final_embeds.append(embed)
            await stw.slash_edit_original(ctx, auth_info[0], final_embeds)
            return

        # wih all checks passed, we may now attempt to change name
        request = await stw.profile_request(self.client, "set_homebase", auth_info[1], profile_id="common_public",
                                            data=orjson.dumps({"homebaseName": f"{name}"}))
        request_json_response = orjson.loads(await request.read())

        # check for le error code
        error_check = await self.check_errors(ctx, request_json_response, auth_info, final_embeds, name, desired_lang)
        if error_check[1]:
            return

        # If passed all checks and changed name, present success embed
        embed = discord.Embed(
            title=await stw.add_emoji_title(self.client, stw.I18n.get("generic.success", desired_lang), "checkmark"),
            description="\u200b",
            colour=succ_colour)

        embed.add_field(name=stw.I18n.get("homebase.embed.field1.name", desired_lang, self.emojis["broken_heart"]),
                        value=f"```{current}```\u200b",
                        inline=False)

        embed.add_field(name=stw.I18n.get("homebase.embed.field2.name", desired_lang, self.emojis["storm_shield"]),
                        value=f"```{name}```\u200b",
                        inline=False)

        if homebase_icon != "placeholder":
            try:
                embed, file = await stw.generate_banner(self.client, embed, homebase_icon, homebase_colour,
                                                        ctx.author.id)
                colour = await stw.get_banner_colour(homebase_colour, "rgb")
                embed.colour = discord.Colour.from_rgb(colour[0], colour[1], colour[2])
            except:
                embed = await stw.set_thumbnail(self.client, embed, "check")
        else:
            embed = await stw.set_thumbnail(self.client, embed, "check")
        embed = await stw.add_requested_footer(ctx, embed, desired_lang)
        final_embeds.append(embed)
        if file is not None:
            await stw.slash_edit_original(ctx, auth_info[0], final_embeds, files=file)
            return
        await stw.slash_edit_original(ctx, auth_info[0], final_embeds)
        return

    @ext.slash_command(name='homebase', name_localization=stw.I18n.construct_slash_dict("homebase.slash.name"),
                       description='This command allows you to view / change the name of your Homebase in STW',
                       description_localization=stw.I18n.construct_slash_dict("homebase.slash.description"),
                       guild_ids=stw.guild_ids)
    async def slashhbrename(self, ctx: discord.ApplicationContext,
                            name: Option(
                                description="The new name for your Homebase. Leave blank to view your current name + banner",
                                description_localizations=stw.I18n.construct_slash_dict("homebase.meta.args.name.description"),
                                name_localizations=stw.I18n.construct_slash_dict("homebase.meta.args.name"),
                                min_length=1, max_length=16) = "",
                            token: Option(description="Your Epic Games authcode. Required unless you have an active "
                                                      "session.",
                                          description_localizations=stw.I18n.construct_slash_dict(
                                              "generic.slash.token"),
                                          name_localizations=stw.I18n.construct_slash_dict("generic.meta.args.token"),
                                          min_length=32) = "",
                            auth_opt_out: Option(default="False",
                                                 description="Opt out of starting an authentication session",
                                                 description_localizations=stw.I18n.construct_slash_dict(
                                                     "generic.slash.optout"),
                                                 name_localizations=stw.I18n.construct_slash_dict(
                                                     "generic.meta.args.optout"),
                                                 choices=[OptionChoice("Do not start an authentication session", "True",
                                                                       stw.I18n.construct_slash_dict(
                                                                           "generic.slash.optout.true")),
                                                          OptionChoice("Start an authentication session (Default)",
                                                                       "False",
                                                                       stw.I18n.construct_slash_dict(
                                                                           "generic.slash.optout.false"))]) = "False"):
        """
        This function is the entry point for the homebase command when called via slash

        Args:
            ctx (discord.ApplicationContext): The context of the slash command
            name: The new name for your Homebase. Leave blank to view your current name + banner
            token: Your Epic Games authcode. Required unless you have an active session.
            auth_opt_out: Opt out of starting an authentication session
        """
        await self.hbrename_command(ctx, name, token, not eval(auth_opt_out))

    @ext.command(name='homebase',
                 aliases=['hbrename', 'hbrn', 'rename', 'changehomebase', 'homebasename', 'hbname', 'hb', 'brn', 'hrn',
                          'hbn', 'hbr', 'hhbrn', 'hbbrn', 'hbrrn', 'hbrnn', 'bhrn', 'hrbn', 'hbnr', 'gbrn', 'ybrn',
                          'ubrn', 'jbrn', 'nbrn', 'bbrn', 'hvrn', 'hgrn', 'hhrn', 'hnrn', 'hben', 'hb4n', 'hb5n',
                          'hbtn', 'hbgn', 'hbfn', 'hbdn', 'hbrb', 'hbrh', 'hbrj', 'hbrm', 'ghbrn', 'hgbrn', 'yhbrn',
                          'hybrn', 'uhbrn', 'hubrn', 'jhbrn', 'hjbrn', 'nhbrn', 'hnbrn', 'bhbrn', 'hvbrn', 'hbvrn',
                          'hbgrn', 'hbhrn', 'hbnrn', 'hbern', 'hbren', 'hb4rn', 'hbr4n', 'hb5rn', 'hbr5n', 'hbtrn',
                          'hbrtn', 'hbrgn', 'hbfrn', 'hbrfn', 'hbdrn', 'hbrdn', 'hbrbn', 'hbrnb', 'hbrhn', 'hbrnh',
                          'hbrjn', 'hbrnj', 'hbrmn', 'hbrnm', 'omebase', 'hmebase', 'hoebase', 'hombase', 'homease',
                          'homebse', 'homebae', 'homebas', 'hhomebase', 'hoomebase', 'hommebase', 'homeebase',
                          'homebbase', 'homebaase', 'homebasse', 'homebasee', 'ohmebase', 'hmoebase', 'hoembase',
                          'hombease', 'homeabse', 'homebsae', 'homebaes', 'gomebase', 'yomebase', 'uomebase',
                          'jomebase', 'nomebase', 'bomebase', 'himebase', 'h9mebase', 'h0mebase', 'hpmebase',
                          'hlmebase', 'hkmebase', 'honebase', 'hojebase', 'hokebase', 'homwbase', 'hom3base',
                          'hom4base', 'homrbase', 'homfbase', 'homdbase', 'homsbase', 'homevase', 'homegase',
                          'homehase', 'homenase', 'homebqse', 'homebwse', 'homebsse', 'homebxse', 'homebzse',
                          'homebaae', 'homebawe', 'homebaee', 'homebade', 'homebaxe', 'homebaze', 'homebasw',
                          'homebas3', 'homebas4', 'homebasr', 'homebasf', 'homebasd', 'homebass', 'ghomebase',
                          'hgomebase', 'yhomebase', 'hyomebase', 'uhomebase', 'huomebase', 'jhomebase', 'hjomebase',
                          'nhomebase', 'hnomebase', 'bhomebase', 'hbomebase', 'hiomebase', 'hoimebase', 'h9omebase',
                          'ho9mebase', 'h0omebase', 'ho0mebase', 'hpomebase', 'hopmebase', 'hlomebase', 'holmebase',
                          'hkomebase', 'hokmebase', 'honmebase', 'homnebase', 'hojmebase', 'homjebase', 'homkebase',
                          'homwebase', 'homewbase', 'hom3ebase', 'home3base', 'hom4ebase', 'home4base', 'homrebase',
                          'homerbase', 'homfebase', 'homefbase', 'homdebase', 'homedbase', 'homsebase', 'homesbase',
                          'homevbase', 'homebvase', 'homegbase', 'homebgase', 'homehbase', 'homebhase', 'homenbase',
                          'homebnase', 'homebqase', 'homebaqse', 'homebwase', 'homebawse', 'homebsase', 'homebxase',
                          'homebaxse', 'homebzase', 'homebazse', 'homebasae', 'homebaswe', 'homebaese', 'homebadse',
                          'homebasde', 'homebasxe', 'homebasze', 'homebasew', 'homebas3e', 'homebase3', 'homebas4e',
                          'homebase4', 'homebasre', 'homebaser', 'homebasfe', 'homebasef', 'homebased', 'homebases',
                          'hhb', 'hbb', 'bh', 'gb', 'yb', 'ub', 'jb', 'nb', 'hv', 'hg', 'hh', 'hn', 'ghb', 'hgb', 'yhb',
                          'hyb', 'uhb', 'hub', 'jhb', 'hjb', 'nhb', 'hnb', 'bhb', 'hvb', 'hbv', 'hbg', 'hbh', 'brename',
                          'hrename', 'hbename', 'hbrname', 'hbreame', 'hbrenme', 'hbrenae', 'hbrenam', 'hhbrename',
                          'hbbrename', 'hbrrename', 'hbreename', 'hbrenname', 'hbrenaame', 'hbrenamme', 'hbrenamee',
                          'bhrename', 'hrbename', 'hbername', 'hbrneame', 'hbreanme', 'hbrenmae', 'hbrenaem',
                          'gbrename', 'ybrename', 'ubrename', 'jbrename', 'nbrename', 'bbrename', 'hvrename',
                          'hgrename', 'hhrename', 'hnrename', 'hbeename', 'hb4ename', 'hb5ename', 'hbtename',
                          'hbgename', 'hbfename', 'hbdename', 'hbrwname', 'hbr3name', 'hbr4name', 'hbrrname',
                          'hbrfname', 'hbrdname', 'hbrsname', 'hbrebame', 'hbrehame', 'hbrejame', 'hbremame',
                          'hbrenqme', 'hbrenwme', 'hbrensme', 'hbrenxme', 'hbrenzme', 'hbrenane', 'hbrenaje',
                          'hbrenake', 'hbrenamw', 'hbrenam3', 'hbrenam4', 'hbrenamr', 'hbrenamf', 'hbrenamd',
                          'hbrenams', 'ghbrename', 'hgbrename', 'yhbrename', 'hybrename', 'uhbrename', 'hubrename',
                          'jhbrename', 'hjbrename', 'nhbrename', 'hnbrename', 'bhbrename', 'hvbrename', 'hbvrename',
                          'hbgrename', 'hbhrename', 'hbnrename', 'hberename', 'hb4rename', 'hbr4ename', 'hb5rename',
                          'hbr5ename', 'hbtrename', 'hbrtename', 'hbrgename', 'hbfrename', 'hbrfename', 'hbdrename',
                          'hbrdename', 'hbrwename', 'hbrewname', 'hbr3ename', 'hbre3name', 'hbre4name', 'hbrername',
                          'hbrefname', 'hbredname', 'hbrsename', 'hbresname', 'hbrebname', 'hbrenbame', 'hbrehname',
                          'hbrenhame', 'hbrejname', 'hbrenjame', 'hbremname', 'hbrenmame', 'hbrenqame', 'hbrenaqme',
                          'hbrenwame', 'hbrenawme', 'hbrensame', 'hbrenasme', 'hbrenxame', 'hbrenaxme', 'hbrenzame',
                          'hbrenazme', 'hbrenanme', 'hbrenamne', 'hbrenajme', 'hbrenamje', 'hbrenakme', 'hbrenamke',
                          'hbrenamwe', 'hbrenamew', 'hbrenam3e', 'hbrename3', 'hbrenam4e', 'hbrename4', 'hbrenamre',
                          'hbrenamer', 'hbrenamfe', 'hbrenamef', 'hbrenamde', 'hbrenamed', 'hbrenamse', 'hbrenames',
                          '/hbrn', '/homebase', '/hbrename', '/homebasern', '/rename', '/hbname', 'tuisbasis',
                          'গৃহভিত্তিক', "base d'inici", 'domovská základna', 'έδρα', 'base', 'kodubaas', 'پایگاه خانگی',
                          'kotipesä', 'ઘર આધાર', 'gidan gida', 'בסיס בית', 'घर आधार', 'hazai bázis', 'ホームベース', '홈베이스',
                          'namų bazė', 'mājas bāze', 'घर बसल्या', 'hjemmebase', 'ਹੋਮਬੇਸ', 'bazę główną',
                          'baza de acasă', 'домашняя база', 'domáca základňa', 'база', 'msingi wa nyumbani',
                          'வீட்டுத்தளம்', 'ఇంటి బేస్', 'ana üs', 'گھریلو', '本垒', '本壘', "based'inici", 'basedinici',
                          'domovskázákladna', 'پایگاهخانگی', 'ઘરઆધાર', 'આધાર', 'gidangida', 'בסיסבית', 'घरआधार', 'आधार',
                          'hazaibázis', 'namųbazė', 'mājasbāze', 'घरबसल्या', 'bazęgłówną', 'bazadeacasă',
                          'домашняябаза', 'domácazákladňa', 'msingiwanyumbani', 'anaüs', 'homefase', 'hotmebase',
                          'homebavse', 'pomebase', 'hompbase', 'homebave', 'homiebase', 'hovebase', 'ohomebase',
                          'domebase', 'hfmebase', 'homebasbe', 'homebasev', 'homebasj', 'homebasce', 'vomebase',
                          'homzbase', 'lomebase', 'hrmebase', 'ehomebase', 'hoamebase', 'homecbase', 'hobmebase',
                          'ihomebase', 'homebasqe', 'hozebase', 'eomebase', 'htomebase', 'homebasej', 'homebape',
                          'mhomebase', 'homebarse', 'hooebase', 'homebasne', 'homebasex', 'homebose', 'hwomebase',
                          'homebrse', 'homxebase', 'homebanse', 'homecase', 'htmebase', 'hoyebase', 'hombbase',
                          'hoxebase', 'homebaset', 'homejbase', 'homebtse', 'ahomebase', 'homebise', 'homebasb',
                          'zomebase', 'phomebase', 'homeaase', 'homebasv', 'homeqase', 'haomebase', 'homebkse',
                          'homebjse', 'hovmebase', 'homezbase', 'hqmebase', 'hometbase', 'hoeebase', 'xhomebase',
                          'homebaske', 'homebasc', 'homebajse', 'homgbase', 'homebage', 'homebame', 'homebpse',
                          'homtbase', 'homebask', 'homebdase', 'hosmebase', 'homebaso', 'homebuase', 'homebasx',
                          'hodebase', 'howebase', 'homebaose', 'homebapse', 'homebasec', 'homebhse', 'homebasea',
                          'homeuase', 'homebnse', 'homuebase', 'homebasek', 'homebasen', 'homebjase', 'homebayse',
                          'homebalse', 'homebcase', 'homekbase', 'homebane', 'homebasm', 'homebasle', 'hzomebase',
                          'howmebase', 'homoebase', 'homeease', 'homeybase', 'homebate', 'komebase', 'homelase',
                          'homebahse', 'homeblse', 'hoqmebase', 'shomebase', 'homebasje', 'homebasl', 'homebasey',
                          'homhebase', 'homebaseb', 'homejase', 'hoymebase', 'homebgse', 'hnmebase', 'hfomebase',
                          'homqbase', 'hmomebase', 'homebasez', 'homlebase', 'hoiebase', 'hoqebase', 'homesase',
                          'homebale', 'tomebase', 'homebfse', 'homebasg', 'homzebase', 'whomebase', 'homebasei',
                          'homlbase', 'hdomebase', 'hymebase', 'hodmebase', 'homubase', 'homebyase', 'hozmebase',
                          'homebuse', 'homebbse', 'womebase', 'homebasz', 'hzmebase', 'homyebase', 'homebasoe',
                          'qomebase', 'homebaje', 'hobebase', 'homebiase', 'homobase', 'fhomebase', 'homebasge',
                          'comebase', 'hocebase', 'momebase', 'homebagse', 'homebacse', 'homebace', 'hxmebase',
                          'hromebase', 'heomebase', 'houebase', 'zhomebase', 'thomebase', 'homebabe', 'homeyase',
                          'hgmebase', 'hotebase', 'homezase', 'homepase', 'hwmebase', 'hometase', 'homaebase',
                          'homebare', 'homeibase', 'hemebase', 'hbmebase', 'vhomebase', 'homkbase', 'hopebase',
                          'homebasep', 'homebaoe', 'homebaseo', 'homebaspe', 'homelbase', 'homeqbase', 'dhomebase',
                          'homepbase', 'homeubase', 'homebasq', 'homebafse', 'hohmebase', 'hcmebase', 'hoaebase',
                          'hompebase', 'hjmebase', 'homgebase', 'homewase', 'homedase', 'homhbase', 'xomebase',
                          'homcbase', 'hofebase', 'homebfase', 'homebaue', 'rhomebase', 'homebaste', 'hhmebase',
                          'homekase', 'hvomebase', 'homebaseg', 'somebase', 'homebtase', 'romebase', 'homebaseq',
                          'homebasem', 'hommbase', 'homebese', 'qhomebase', 'homebmase', 'hvmebase', 'homebashe',
                          'homebasn', 'homebatse', 'homebvse', 'homebasa', 'homebasy', 'humebase', 'hogebase',
                          'homeboase', 'oomebase', 'homybase', 'hsmebase', 'homebahe', 'homebast', 'homebaqe',
                          'homebyse', 'homeblase', 'lhomebase', 'homebease', 'homebaseu', 'khomebase', 'homibase',
                          'houmebase', 'homebaie', 'hocmebase', 'homebakse', 'hormebase', 'homnbase', 'homebasie',
                          'chomebase', 'homebaise', 'homebasve', 'hsomebase', 'iomebase', 'homebkase', 'homeiase',
                          'homvbase', 'homeobase', 'homjbase', 'homembase', 'hqomebase', 'hamebase', 'aomebase',
                          'homebasme', 'fomebase', 'homtebase', 'holebase', 'homebaye', 'hohebase', 'hosebase',
                          'homxbase', 'homebmse', 'hogmebase', 'homebafe', 'hxomebase', 'homebasel', 'homqebase',
                          'hombebase', 'homebamse', 'hoemebase', 'homebcse', 'homabase', 'homebash', 'homemase',
                          'hoxmebase', 'hdmebase', 'homeabase', 'homebpase', 'homerase', 'homebasu', 'homebasue',
                          'homebaseh', 'homebasp', 'homebrase', 'homeoase', 'hcomebase', 'homcebase', 'horebase',
                          'homvebase', 'hmmebase', 'homexbase', 'homebause', 'homebasi', 'homexase', 'homebake',
                          'homebdse', 'homebabse', 'homebasye', 'hofmebase', 'h8mebase', 'h;mebase', 'h*mebase',
                          'h(mebase', 'h)mebase', 'ho,ebase', 'ho<ebase', 'hom2base', 'hom$base', 'hom#base',
                          'hom@base', 'homebas2', 'homebas$', 'homebas#', 'homebas@', 'hbrr', 'hbirn', 'hbrvn', 'hbrln',
                          'hebrn', 'lbrn', 'hbrnf', 'hbjrn', 'hobrn', 'hwrn', 'hfbrn', 'hirn', 'hbrns', 'hbrnl',
                          'hqbrn', 'hbrnp', 'hbre', 'hbrg', 'hbra', 'hlbrn', 'hburn', 'ehbrn', 'hbrnv', 'hbhn', 'hbzn',
                          'hyrn', 'hwbrn', 'hbrcn', 'lhbrn', 'hbrw', 'hbun', 'hbrnz', 'obrn', 'habrn', 'hsbrn', 'hbrun',
                          'vbrn', 'hborn', 'hbwrn', 'hrrn', 'hblrn', 'shbrn', 'wbrn', 'hbrnt', 'hfrn', 'qbrn', 'hbprn',
                          'hbrt', 'hdbrn', 'khbrn', 'hbcrn', 'xbrn', 'tbrn', 'hbrwn', 'htrn', 'hdrn', 'rbrn', 'hbrp',
                          'hqrn', 'htbrn', 'hbvn', 'hbkrn', 'hbri', 'hbjn', 'hkrn', 'hbrnx', 'hbarn', 'sbrn', 'hibrn',
                          'hbrkn', 'hbqrn', 'pbrn', 'hpbrn', 'hkbrn', 'ebrn', 'ihbrn', 'hbrnu', 'hlrn', 'hbrnc', 'hbkn',
                          'hbln', 'hbwn', 'hbrk', 'hbrxn', 'hbzrn', 'hern', 'hbbn', 'hzbrn', 'zbrn', 'hjrn', 'mhbrn',
                          'hbxrn', 'hbrng', 'hbrzn', 'hcrn', 'hzrn', 'hbrq', 'hban', 'hbqn', 'hbran', 'hbin', 'ahbrn',
                          'hbrnr', 'hbrnw', 'hbro', 'hbrin', 'hbrsn', 'hbrny', 'hbrnq', 'hbrno', 'phbrn', 'hmbrn',
                          'whbrn', 'hbrc', 'hbxn', 'hbrd', 'hbmn', 'zhbrn', 'ibrn', 'fbrn', 'hbrnd', 'hxrn', 'hxbrn',
                          'hbrnk', 'hbrs', 'hbon', 'thbrn', 'hbrpn', 'ohbrn', 'hbcn', 'chbrn', 'hbrna', 'hbry', 'dhbrn',
                          'hprn', 'qhbrn', 'hbsrn', 'hbrne', 'dbrn', 'hbpn', 'hurn', 'kbrn', 'hbrf', 'abrn', 'hsrn',
                          'harn', 'hbnn', 'hmrn', 'rhbrn', 'hbrx', 'hbryn', 'hbrni', 'hbrz', 'hbrv', 'hbyn', 'hbrl',
                          'hcbrn', 'hbmrn', 'cbrn', 'hbru', 'hbsn', 'hbrqn', 'xhbrn', 'hbyrn', 'hbron', 'mbrn', 'fhbrn',
                          'horn', 'hrbrn', 'vhbrn', 'hb3n', 'hb#n', 'hb$n', 'hb%n', 'hbr,', 'hbr<', 'bsename',
                          'basdname', 'lbasename', 'basenaxe', 'brasename', 'basezname', 'bbsename', 'bcsename',
                          'basenaem', 'bamename', 'bsaename', 'bwasename', 'absename', 'bysename', 'basenam',
                          'basemname', 'barsename', 'basenzame', 'baseame', 'baename', 'zasename', 'sbasename',
                          'bapename', 'babename', 'bxsename', 'baxsename', 'bfasename', 'bpasename', 'baosename',
                          'asename', 'basneame', 'basepname', 'basenarme', 'baesname', 'basenae', 'basname', 'basenage',
                          'bajename', 'basedame', 'basenme', 'basenmae', 'basenaue', 'basenamee', 'basfname',
                          'basenace', 'gasename', 'basenalme', 'basesame', 'bastename', 'basenape', 'basenvme',
                          'baxename', 'basenamei', 'baseanme', 'basenaye', 'basjname', 'basenamg', 'basgname',
                          'bashname', 'basenamwe', 'basenamie', 'basefame', 'basenafe', 'bascname', 'jasename',
                          'basenadme', 'basenamve', 'basentame', 'baeename', 'basenkme', 'basejname', 'basenamk',
                          'basenqame', 'basenamqe', 'bpsename', 'fbasename', 'busename', 'buasename', 'bagsename',
                          'bcasename', 'bazename', 'baselame', 'baszename', 'basenaie', 'bamsename', 'bosename',
                          'baskename', 'basenambe', 'basenate', 'basmename', 'badsename', 'bgasename', 'basenrame',
                          'bassname', 'basenamec', 'baseneame', 'basenfme', 'basenhme', 'basaname', 'bvsename',
                          'basenamhe', 'baswename', 'baisename', 'baseniame', 'basenamep', 'bacename', 'basenamge',
                          'baesename', 'basenamse', 'basename', 'basnname', 'basenxame', 'bassename', 'basenxme',
                          'basenamt', 'bbasename', 'baspname', 'basenavme', 'basiename', 'basenamed', 'baseoname',
                          'baseename', 'basenuame', 'vasename', 'basenamel', 'badename', 'bssename', 'basennme',
                          'pasename', 'baspename', 'tasename', 'bmsename', 'bgsename', 'basenade', 'baasename',
                          'basenamne', 'bahename', 'abasename', 'baoename', 'basentme', 'beasename', 'xasename',
                          'basenaoe', 'basenamp', 'basenamke', 'basenjme', 'baqsename', 'bxasename', 'basewame',
                          'basesname', 'basenmame', 'basenwame', 'basenfame', 'basenamze', 'basxename', 'basenamek',
                          'sasename', 'basrename', 'hbasename', 'basenave', 'bahsename', 'bkasename', 'basekname',
                          'basenabme', 'basenamq', 'basenbme', 'basepame', 'basenama', 'basegname', 'btasename',
                          'basqname', 'basenamo', 'basenamea', 'basenkame', 'basenanme', 'baskname', 'hasename',
                          'wasename', 'bksename', 'bastname', 'iasename', 'basenamz', 'basnename', 'basenwme',
                          'bisename', 'boasename', 'lasename', 'bazsename', 'basenahe', 'basehame', 'basenzme',
                          'basenamez', 'basewname', 'baseyame', 'basername', 'basmname', 'basuname', 'basbename',
                          'bvasename', 'basiname', 'bafename', 'basenake', 'basekame', 'baslename', 'basenamte',
                          'bavsename', 'basenamue', 'basecame', 'basenale', 'basenpme', 'basenami', 'ubasename',
                          'basenyme', 'oasename', 'basenlame', 'basensme', 'casename', 'baksename', 'basoename',
                          'basenrme', 'basenamxe', 'basenakme', 'basenasme', 'rasename', 'baaename', 'baseeame',
                          'basenvame', 'rbasename', 'basenamx', 'bmasename', 'banename', 'bashename', 'basenames',
                          'basvename', 'bauename', 'basfename', 'pbasename', 'basejame', 'bascename', 'basenamme',
                          'basenaame', 'kasename', 'ebasename', 'mbasename', 'basecname', 'basenahme', 'basenamu',
                          'baiename', 'nbasename', 'basenime', 'basenamoe', 'baysename', 'basuename', 'masename',
                          'baseiame', 'basemame', 'basenase', 'batename', 'baseiname', 'basenaxme', 'bhasename',
                          'bajsename', 'qbasename', 'bausename', 'basenagme', 'basaename', 'basenamfe', 'baswname',
                          'basenameg', 'btsename', 'baseaname', 'baselname', 'basrname', 'basenafme', 'basenume',
                          'basenyame', 'basenlme', 'basenamm', 'baseaame', 'bsasename', 'baslname', 'basenname',
                          'dbasename', 'basenane', 'gbasename', 'basenamem', 'basetname', 'basenamr', 'basjename',
                          'basqename', 'bhsename', 'nasename', 'bqsename', 'baszname', 'ybasename', 'basvname',
                          'basenaqe', 'basenamh', 'basenaee', 'basenaae', 'basenaml', 'bdasename', 'bzsename',
                          'basebame', 'basenamev', 'bfsename', 'basenamde', 'basenameh', 'easename', 'basenamle',
                          'basevname', 'zbasename', 'bacsename', 'bavename', 'bwsename', 'basezame', 'basenaome',
                          'basenamj', 'basendme', 'basenawme', 'bzasename', 'babsename', 'ibasename', 'basdename',
                          'fasename', 'basegame', 'balename', 'basenbame', 'bnsename', 'basenare', 'basenamer',
                          'bagename', 'bawsename', 'basenameq', 'basenamet', 'basedname', 'obasename', 'bdsename',
                          'wbasename', 'blsename', 'brsename', 'basenoame', 'basenapme', 'bqasename', 'basexname',
                          'basoname', 'basgename', 'basenamen', 'yasename', 'basengame', 'basenome', 'bjsename',
                          'basenaqme', 'basenamc', 'basefname', 'basenameu', 'basebname', 'basenaze', 'aasename',
                          'basenamje', 'kbasename', 'tbasename', 'batsename', 'basenpame', 'basexame', 'basxname',
                          'baseyname', 'baseqame', 'basenamre', 'basenawe', 'basenams', 'blasename', 'basensame',
                          'basevame', 'bayename', 'basenamae', 'basenaume', 'baseneme', 'basenamb', 'bawename',
                          'basenamce', 'basenamye', 'bapsename', 'basenmme', 'biasename', 'basenamv', 'basenameo',
                          'basenjame', 'balsename', 'bakename', 'basenamew', 'besename', 'basehname', 'bnasename',
                          'basenameb', 'basenazme', 'basenamef', 'bansename', 'qasename', 'baseoame', 'basetame',
                          'basengme', 'basencme', 'vbasename', 'basenamw', 'baqename', 'basenayme', 'basenamex',
                          'bafsename', 'basencame', 'basenhame', 'basenamn', 'basenamey', 'basenamej', 'dasename',
                          'uasename', 'basenajme', 'basyname', 'basenabe', 'bjasename', 'baseuname', 'basenacme',
                          'baseuame', 'basenamf', 'basbname', 'basenampe', 'jbasename', 'basenqme', 'cbasename',
                          'basenaime', 'byasename', 'xbasename', 'basenatme', 'basendame', 'baseqname', 'basenaeme',
                          'basyename', 'baserame', 'basenamd', 'basenamy', 'basenaje', 'barename', 'bas4name',
                          'bas3name', 'bas2name', 'bas$name', 'bas#name', 'bas@name', 'base,ame', 'base<ame',
                          'basena,e', 'basena<e', 'basenam4', 'basenam3', 'basenam2', 'basenam$', 'basenam#',
                          'basenam@', 'renmae', 'renami', 'ename', 'renaem', 'renamea', 'riname', 'reame', 'reanme',
                          'renae', 'pename', 'renme', 'ername', 'rerame', 'nrename', 'rwname', 'rname', 'renamie',
                          'renxme', 'renabme', 'repame', 'renaie', 'rrename', 'rbname', 'renamt', 'cename', 'erename',
                          'renkme', 'reqame', 'renamm', 'yename', 'renamge', 'rencme', 'roname', 'reyname', 'renam',
                          'rneame', 'renare', 'rejame', 'renaxe', 'renyme', 'renlme', 'renamet', 'renamye', 'raename',
                          'bename', 'rrname', 'renzme', 'krename', 'renafe', 'revname', 'urename', 'renade', 'renamw',
                          'rlname', 'renamne', 'renbme', 'renamez', 'recname', 'renalme', 'renamke', 'rqename',
                          'renamek', 'frename', 'renuame', 'renawe', 'renameg', 'renfme', 'irename', 'renaze',
                          'renampe', 'renatme', 'reneame', 'renaeme', 'rezame', 'rennme', 'renaxme', 'renmme', 'renamf',
                          'rehame', 'rsename', 'renyame', 'fename', 'renzame', 'rhname', 'retame', 'renamxe', 'tename',
                          'grename', 'renahe', 'rewname', 'renome', 'renaqe', 'renpame', 'renamj', 'renamr', 'reoname',
                          'rzname', 'renamed', 'reiname', 'renaqme', 'rencame', 'renfame', 'lename', 'renoame',
                          'renjame', 'rxename', 'renafme', 'orename', 'renale', 'renapme', 'renambe', 'xrename',
                          'drename', 'renabe', 'reeame', 'renase', 'rzename', 'repname', 'rengame', 'mename', 'renamue',
                          'renamo', 'reneme', 'riename', 'renamme', 'renajme', 'renacme', 'rejname', 'rmname', 'resame',
                          'renamte', 'rxname', 'vename', 'renahme', 'renape', 'rexname', 'renamee', 'renamex', 'renake',
                          'sename', 'renamz', 'renamve', 'zrename', 'rsname', 'renamu', 'rvename', 'redname', 'renqme',
                          'rbename', 'renvme', 'ryname', 'renwme', 'rfname', 'qrename', 'reename', 'renwame', 'prename',
                          'renamen', 'rpname', 'rjname', 'qename', 'zename', 'renamde', 'kename', 'renamq', 'renamc',
                          'rtname', 'aename', 'renlame', 'rgename', 'rekame', 'revame', 'renkame', 'renaame', 'reyame',
                          'uename', 'relname', 'renime', 'renamew', 'reaame', 'remame', 'renadme', 'srename', 'renamze',
                          'renate', 'rewame', 'rhename', 'jrename', 'remname', 'renamb', 'renamae', 'renaml', 'ryename',
                          'rensame', 'rentame', 'refame', 'renamn', 'regame', 'renamej', 'gename', 'retname', 'runame',
                          'rebname', 'renace', 'reuame', 'xename', 'trename', 'renname', 'rmename', 'rername', 'rendme',
                          'renamje', 'reoame', 'rqname', 'renameh', 'renave', 'reiame', 'iename', 'jename', 'arename',
                          'reuname', 'renaje', 'renaue', 'renamd', 'renqame', 'rfename', 'renamfe', 'renaoe', 'ruename',
                          'renume', 'renage', 'renamey', 'rkname', 'rehname', 'rgname', 'renarme', 'rekname', 'renaime',
                          'rpename', 'yrename', 'renane', 'rexame', 'renams', 'renakme', 'nename', 'renaae', 'renamp',
                          'resname', 'eename', 'renamg', 'renaee', 'regname', 'reqname', 'renameo', 'renamse', 'hename',
                          'renayme', 'raname', 'rebame', 'renamev', 'rwename', 'renxame', 'renjme', 'renawme',
                          'renmame', 'renameb', 'renamep', 'renamh', 'renamk', 'rtename', 'renamle', 'rlename',
                          'renaume', 'rensme', 'renamhe', 'renazme', 'reniame', 'renaye', 'renamqe', 'rentme',
                          'renameu', 'renamy', 'rnname', 'renpme', 'rdname', 'rengme', 'dename', 'renagme', 'rvname',
                          'renamx', 'renvame', 'relame', 'reaname', 'roename', 'renamem', 'wename', 'rendame',
                          'renamre', 'wrename', 'rcename', 'renamei', 'renrme', 'oename', 'rezname', 'rdename',
                          'renamer', 'renamoe', 'rnename', 'mrename', 'rcname', 'renbame', 'lrename', 'renasme',
                          'rjename', 'redame', 'renaome', 'renhme', 'renamwe', 'refname', 'renameq', 'renama',
                          'renamce', 'rkename', 'crename', 'renanme', 'renavme', 'renamec', 'renamv', 'renamef',
                          'vrename', 'renamel', 'renhame', 'renrame', 'renames', 'recame', '3ename', '4ename', '5ename',
                          '#ename', '$ename', '%ename', 'r4name', 'r3name', 'r2name', 'r$name', 'r#name', 'r@name',
                          're,ame', 're<ame', 'rena,e', 'rena<e', 'renam4', 'renam3', 'renam2', 'renam$', 'renam#',
                          'renam@', 'hbrenyme', 'hbrenamce', 'hbrlname', 'khbrename', 'hbrenpme', 'hbvename',
                          'cbrename', 'hbsrename', 'hbrenamge', 'hbrenamae', 'hbnename', 'rbrename', 'hbrenvame',
                          'hbrenamj', 'phbrename', 'ibrename', 'hzbrename', 'hbrjname', 'ehbrename', 'hbrenume',
                          'lhbrename', 'hburename', 'thbrename', 'fbrename', 'hbrenameo', 'hbrenamxe', 'hbrezame',
                          'hbrenamy', 'mbrename', 'hbzrename', 'hirename', 'hbreuname', 'hbrenbme', 'hbrenamle',
                          'hbrenabme', 'hbrmename', 'hsrename', 'hbrenfame', 'hbrenamye', 'hbrenamue', 'hbrexame',
                          'hbrenameu', 'sbrename', 'hbrewame', 'hpbrename', 'hbrenase', 'hbryname', 'hbrenamz',
                          'hfbrename', 'hbrtname', 'hbrenare', 'hbrenamek', 'hbrkename', 'hbjename', 'hbrenamb',
                          'hbrenacme', 'hxrename', 'hkbrename', 'hbrenamn', 'hbrenaume', 'hbreiame', 'hbrenaae',
                          'hbrenyame', 'hbreiname', 'hmbrename', 'hbriname', 'hbregname', 'hzrename', 'hbrenamez',
                          'vbrename', 'hbrefame', 'hxbrename', 'hbwrename', 'hbrenamze', 'hbreuame', 'wbrename',
                          'hbreneme', 'hbrlename', 'hbrxname', 'hbmrename', 'hbrenmme', 'hbrenvme', 'hbarename',
                          'hbrenuame', 'hbrenarme', 'hbrenaml', 'hcbrename', 'hbreqame', 'hbwename', 'hbraename',
                          'hbrpename', 'hmrename', 'hbrcname', 'hbredame', 'hbcename', 'hbraname', 'htbrename',
                          'hyrename', 'hbrenalme', 'hbrenrme', 'hbrenama', 'hbrnname', 'hrrename', 'hbrenkame',
                          'hbxrename', 'hbuename', 'hbrvename', 'hbrenamh', 'hbrenaome', 'hbreyame', 'hbrenamen',
                          'hbrentame', 'hbrendame', 'hbreoname', 'hbrenamk', 'hwrename', 'hbrmname', 'zhbrename',
                          'hbruename', 'htrename', 'hprename', 'hobrename', 'hebrename', 'hbrenamte', 'hbrenate',
                          'hbreniame', 'hbxename', 'hbrenamc', 'hbkename', 'hbrenameg', 'hbrepname', 'hbrevname',
                          'hbiename', 'hbreoame', 'hbmename', 'hrbrename', 'hbruname', 'hbqrename', 'hbrqname',
                          'hbrbname', 'hurename', 'hbrerame', 'hbrenamx', 'ohbrename', 'hbrenlme', 'hbrentme',
                          'hbriename', 'hbrengme', 'xbrename', 'hbroename', 'hbrenamv', 'hbrvname', 'ebrename',
                          'hbregame', 'hbrenami', 'hbrendme', 'hbrenamqe', 'hbrenabe', 'hbrenamea', 'kbrename',
                          'dbrename', 'hbrenaime', 'whbrename', 'hbrenale', 'hbrenaqe', 'shbrename', 'ahbrename',
                          'hwbrename', 'hblename', 'hbrenome', 'hbrelame', 'hbrelname', 'hkrename', 'hbrenamei',
                          'hbrenahe', 'hbrenatme', 'hbretame', 'hbrenaie', 'hbrenaee', 'hbryename', 'hbrenafme',
                          'hbbename', 'hbrepame', 'hbrenade', 'hborename', 'hdbrename', 'harename', 'hbyrename',
                          'hbrenameq', 'hbaename', 'hbrenamey', 'hbrencme', 'hbrencame', 'hbrenhme', 'hbrenkme',
                          'hbirename', 'hbrengame', 'hbrenape', 'hbrenamec', 'herename', 'hbrekame', 'zbrename',
                          'hbrenamex', 'pbrename', 'hbrenamev', 'hbpename', 'hbrenamet', 'hjrename', 'hbrenaxe',
                          'hbrnename', 'hbrenamve', 'hbrpname', 'hbzename', 'hboename', 'hbrezname', 'horename',
                          'hbyename', 'hbrenaoe', 'hbrenaeme', 'hbrenadme', 'hbrenamej', 'tbrename', 'obrename',
                          'hbrenameb', 'qbrename', 'hbrenamhe', 'hbkrename', 'hbrenafe', 'hbrecame', 'lbrename',
                          'hbrevame', 'hbrenaye', 'hfrename', 'hbrenagme', 'vhbrename', 'hbjrename', 'hbreeame',
                          'hbrenace', 'hqrename', 'hbrenfme', 'rhbrename', 'hbrhename', 'hbroname', 'hbreaame',
                          'hbrexname', 'hbrbename', 'hbrekname', 'hbrenamel', 'hbrenaze', 'hsbrename', 'hbrenpame',
                          'hbprename', 'hbrqename', 'hbrenayme', 'hibrename', 'hbcrename', 'hbrenamm', 'abrename',
                          'hbrenamie', 'hbrenamep', 'hbretname', 'hbrzname', 'hlbrename', 'fhbrename', 'mhbrename',
                          'hbrenamu', 'hcrename', 'qhbrename', 'hbsename', 'hbrenamoe', 'hbrennme', 'hbrenambe',
                          'hqbrename', 'hbrenime', 'hbrenamq', 'hbrenamt', 'hbresame', 'hbrenrame', 'hbrenoame',
                          'hbrzename', 'hbrxename', 'habrename', 'hbrenamo', 'hbrenjme', 'hbrenamp', 'hbrkname',
                          'hbrcename', 'hbreaname', 'hbreqname', 'hbqename', 'ihbrename', 'hbrgname', 'hbreneame',
                          'hbrenampe', 'dhbrename', 'hbrenaue', 'hbrenave', 'hbrenlame', 'hbrenamg', 'hlrename',
                          'hbrenawe', 'hbrenage', 'hdrename', 'hbhename', 'hbrenahme', 'hbrecname', 'hbrhname',
                          'hbrenapme', 'hbrjename', 'hblrename', 'hbrenameh', 'hbrenavme', 'chbrename', 'xhbrename',
                          'hbreyname', 'hbrenamem', 'hb3ename', 'hb#ename', 'hb$ename', 'hb%ename', 'hbr2name',
                          'hbr$name', 'hbr#name', 'hbr@name', 'hbre,ame', 'hbre<ame', 'hbrena,e', 'hbrena<e',
                          'hbrenam2', 'hbrenam$', 'hbrenam#', 'hbrenam@', '/basename'],
                 extras={'emoji': "storm_shield", "args": {
                     'homebase.meta.args.name': ['homebase.meta.args.name.description', True],
                     'generic.meta.args.authcode': ['generic.slash.token', True],
                     'generic.meta.args.optout': ['generic.meta.args.optout.description', True]},
                         'dev': False,
                         "description_keys": ['homebase.meta.description.main', 'homebase.meta.description.list',
                                              'homebase.meta.description.list.item1',
                                              'homebase.meta.description.list.item2',
                                              'homebase.meta.description.list.item3',
                                              'homebase.meta.description.list.item4',
                                              'homebase.meta.description.list.item5'], "experimental": True,
                         "name_key": "homebase.slash.name"},
                 brief="homebase.meta.brief",
                 description="{0}\n\u200b\n{1}\n⦾ {2}\n⦾ {3}\n⦾ {4}\n⦾ {5}\n⦾ {6}\n")
    async def hbrename(self, ctx, name='', authcode='', optout=None):
        """
        This is the entry point for the homebase command when called traditionally

        Args:
            ctx: The context of the command
            name: The new name for the homebase
            authcode: The authcode for the account
            optout: Any text given will opt out of starting an auth session
        """
        if optout is not None:
            optout = True
        else:
            optout = False

        await self.hbrename_command(ctx, name, authcode, not optout)


def setup(client):
    """
    This function is called when the cog is loaded via load_extension

    Args:
        client: The bot client
    """
    client.add_cog(Homebase(client))
