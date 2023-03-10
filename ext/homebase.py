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
                homebase_colour = "defaultcolor1"
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
                        homebase_colour = "defaultcolor1"
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
                            homebase_colour = "defaultcolor1"
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
                          'গৃহভিত্তিক', "base d'inici", 'domovská základna', 'έδρα', 'base', 'kodubaas',
                          'پایگاه خانگی', 'kotipesä', 'ઘર આધાર', 'gidan gida', 'בסיס בית', 'घर आधार', 'hazai bázis',
                          'ホームベース', '홈베이스', 'namų bazė', 'mājas bāze', 'घर बसल्या', 'hjemmebase', 'ਹੋਮਬੇਸ',
                          'bazę główną', 'baza de acasă', 'домашняя база', 'domáca základňa', 'база',
                          'msingi wa nyumbani', 'வீட்டுத்தளம்', 'ఇంటి బేస్', 'ana üs', 'گھریلو', '本垒', '本壘',
                          "based'inici", 'basedinici', 'domovskázákladna', 'پایگاهخانگی', 'ઘરઆધાર', 'આધાર',
                          'gidangida', 'בסיסבית', 'घरआधार', 'आधार', 'hazaibázis', 'namųbazė', 'mājasbāze',
                          'घरबसल्या', 'bazęgłówną', 'bazadeacasă', 'домашняябаза', 'domácazákladňa', 'msingiwanyumbani',
                          'anaüs'],
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
