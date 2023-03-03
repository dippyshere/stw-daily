"""
STW Daily Discord bot Copyright 2023 by the STW Daily team.
Please do not skid our hard work.
https://github.com/dippyshere/stw-daily

This file is the cog for the how2 command. Displays the how to use embed + gif
"""

import discord
import discord.ext.commands as ext
from discord.commands import (  # Importing the decorator that makes slash commands.
    slash_command,
)

import stwutil as stw


# view for the invite command.
class HowToUseView(discord.ui.View):
    """
    discord UI View for the how to use command.
    """

    def __init__(self, client, author, ctx, desired_lang):
        super().__init__(timeout=None)
        self.client = client
        self.ctx = ctx
        self.author = author
        self.desired_lang = desired_lang

        self.add_item(discord.ui.Button(label=stw.I18n.get("how2.view.getcode", desired_lang),
                                        style=discord.ButtonStyle.link,
                                        url=self.client.config["login_links"]["login_fortnite_pc"],
                                        emoji=self.client.config["emojis"]["link_icon"]))
        self.add_item(discord.ui.Button(label=stw.I18n.get("how2.view.button.morehelp", desired_lang),
                                        style=discord.ButtonStyle.link,
                                        url="https://github.com/dippyshere/stw-daily/wiki",
                                        emoji=self.client.config["emojis"]["info"]))


class HowTo(ext.Cog):
    """
    The how to command.
    """

    def __init__(self, client):
        self.client = client
        self.emojis = client.config["emojis"]

    async def how_to_command(self, ctx):
        """
        The main function for the how to use command.

        Args:
            ctx: The context of the command.

        Returns:
            None
        """

        desired_lang = await stw.I18n.get_desired_lang(self.client, ctx)

        embed_colour = self.client.colours["generic_blue"]

        token_arg = stw.I18n.get("generic.meta.args.token", desired_lang)

        embed = discord.Embed(
            title=await stw.add_emoji_title(self.client, stw.I18n.get("how2.embed.title", desired_lang), "info"),
            description=f'\u200b\n{stw.I18n.get("how2.embed.description1", desired_lang, "https://github.com/dippyshere/stw-daily/wiki", "https://github.com/dippyshere/stw-daily/wiki")}\n'
                        f'\n{stw.I18n.get("how2.embed.description2", desired_lang)}\n'
                        f'{stw.I18n.get("how2.embed.description3", desired_lang, self.client.config["login_links"]["login_fortnite_pc"])}\n'
                        f'\n{stw.I18n.get("how2.embed.description4", desired_lang)}\n'
                        f'{stw.I18n.get("how2.embed.description5", desired_lang)}\n'
                        f'{stw.I18n.get("how2.embed.description6", desired_lang, "  •", f"</daily:1057120945522876473> `{token_arg}`")}\n'
                        f'{stw.I18n.get("how2.embed.description6", desired_lang, "  •", f"<@757776996418715651> daily `{token_arg}`")}\n'
                        f'\n{stw.I18n.get("how2.embed.description7", desired_lang)}\n'
                        f'*<@757776996418715651> `d a51c1f4d35b1457c8e34a1f6026faa35`*'
                        f'\n\u200b',
            color=embed_colour)

        embed = await stw.set_thumbnail(self.client, embed, "help")
        # embed = await stw.add_requested_footer(ctx, embed)
        embed = await stw.set_embed_image(embed, "https://cdn.discordapp.com/attachments/757768060810559541"
                                                 "/1050461779991474266/stw_daily_noob_tutorial_render_2_hd.gif")

        # # get channel from id
        # channel = self.client.get_channel(758561253156847629)
        # # get message from id
        # message = await channel.fetch_message(813715483928559656)
        # # edit message
        # await message.edit(embed=embed, view=HowToUseView(self.client, ctx.author, ctx))
        # # get channel from id
        # channel = self.client.get_channel(757768833946877992)
        # # get message from id
        # message = await channel.fetch_message(1050835103179341960)
        # # edit message
        # await message.edit(embed=embed, view=HowToUseView(self.client, ctx.author, ctx))
        # await ctx.channel.send(
        #     f"{ctx.author.mention} I've updated the how to use embed in <#758561253156847629> and <#757768833946877992>.")

        invite_view = HowToUseView(self.client, ctx.author, ctx, desired_lang)
        await stw.slash_send_embed(ctx, self.client, embed, invite_view)
        return

    @ext.command(name='how2',
                 aliases=['howto', 'howtouse', 'how2use', 'how2usebot', 'how2usestwdaily', 'howtousestwdaily',
                          'instruction', 'inst', '/how2', '/howto', '/howtouse', '/how2use', '/how2usebot',
                          '/instruction', '/inst', 'morehelp', 'plshelp', 'tutorial', '/tutorial', 'how',
                          'owto', 'hwto', 'hoto', 'howo', 'howt', 'hhowto', 'hoowto', 'howwto', 'howtto', 'howtoo',
                          'ohwto', 'hwoto', 'hotwo', 'howot', 'gowto', 'yowto', 'uowto', 'jowto', 'nowto', 'bowto',
                          'hiwto', 'h9wto', 'h0wto', 'hpwto', 'hlwto', 'hkwto', 'hoqto', 'ho2to', 'ho3to', 'hoeto',
                          'hodto', 'hosto', 'hoato', 'howro', 'how5o', 'how6o', 'howyo', 'howho', 'howgo', 'howfo',
                          'howti', 'howt9', 'howt0', 'howtp', 'howtl', 'howtk', 'ghowto', 'hgowto', 'yhowto', 'hyowto',
                          'uhowto', 'huowto', 'jhowto', 'hjowto', 'nhowto', 'hnowto', 'bhowto', 'hbowto', 'hiowto',
                          'hoiwto', 'h9owto', 'ho9wto', 'h0owto', 'ho0wto', 'hpowto', 'hopwto', 'hlowto', 'holwto',
                          'hkowto', 'hokwto', 'hoqwto', 'howqto', 'ho2wto', 'how2to', 'ho3wto', 'how3to', 'hoewto',
                          'howeto', 'hodwto', 'howdto', 'hoswto', 'howsto', 'hoawto', 'howato', 'howrto', 'howtro',
                          'how5to', 'howt5o', 'how6to', 'howt6o', 'howyto', 'howtyo', 'howhto', 'howtho', 'howgto',
                          'howtgo', 'howfto', 'howtfo', 'howtio', 'howtoi', 'howt9o', 'howto9', 'howt0o', 'howto0',
                          'howtpo', 'howtop', 'howtlo', 'howtol', 'howtko', 'howtok', 'owtouse', 'hwtouse', 'hotouse',
                          'howouse', 'howtuse', 'howtose', 'howtoue', 'howtous', 'hhowtouse', 'hoowtouse', 'howwtouse',
                          'howttouse', 'howtoouse', 'howtouuse', 'howtousse', 'howtousee', 'ohwtouse', 'hwotouse',
                          'hotwouse', 'howotuse', 'howtuose', 'howtosue', 'howtoues', 'gowtouse', 'yowtouse',
                          'uowtouse', 'jowtouse', 'nowtouse', 'bowtouse', 'hiwtouse', 'h9wtouse', 'h0wtouse',
                          'hpwtouse', 'hlwtouse', 'hkwtouse', 'hoqtouse', 'ho2touse', 'ho3touse', 'hoetouse',
                          'hodtouse', 'hostouse', 'hoatouse', 'howrouse', 'how5ouse', 'how6ouse', 'howyouse',
                          'howhouse', 'howgouse', 'howfouse', 'howtiuse', 'howt9use', 'howt0use', 'howtpuse',
                          'howtluse', 'howtkuse', 'howtoyse', 'howto7se', 'howto8se', 'howtoise', 'howtokse',
                          'howtojse', 'howtohse', 'howtouae', 'howtouwe', 'howtouee', 'howtoude', 'howtouxe',
                          'howtouze', 'howtousw', 'howtous3', 'howtous4', 'howtousr', 'howtousf', 'howtousd',
                          'howtouss', 'ghowtouse', 'hgowtouse', 'yhowtouse', 'hyowtouse', 'uhowtouse', 'huowtouse',
                          'jhowtouse', 'hjowtouse', 'nhowtouse', 'hnowtouse', 'bhowtouse', 'hbowtouse', 'hiowtouse',
                          'hoiwtouse', 'h9owtouse', 'ho9wtouse', 'h0owtouse', 'ho0wtouse', 'hpowtouse', 'hopwtouse',
                          'hlowtouse', 'holwtouse', 'hkowtouse', 'hokwtouse', 'hoqwtouse', 'howqtouse', 'ho2wtouse',
                          'how2touse', 'ho3wtouse', 'how3touse', 'hoewtouse', 'howetouse', 'hodwtouse', 'howdtouse',
                          'hoswtouse', 'howstouse', 'hoawtouse', 'howatouse', 'howrtouse', 'howtrouse', 'how5touse',
                          'howt5ouse', 'how6touse', 'howt6ouse', 'howytouse', 'howtyouse', 'howhtouse', 'howthouse',
                          'howgtouse', 'howtgouse', 'howftouse', 'howtfouse', 'howtiouse', 'howtoiuse', 'howt9ouse',
                          'howto9use', 'howt0ouse', 'howto0use', 'howtpouse', 'howtopuse', 'howtlouse', 'howtoluse',
                          'howtkouse', 'howtokuse', 'howtoyuse', 'howtouyse', 'howto7use', 'howtou7se', 'howto8use',
                          'howtou8se', 'howtouise', 'howtoukse', 'howtojuse', 'howtoujse', 'howtohuse', 'howtouhse',
                          'howtouase', 'howtousae', 'howtouwse', 'howtouswe', 'howtouese', 'howtoudse', 'howtousde',
                          'howtouxse', 'howtousxe', 'howtouzse', 'howtousze', 'howtousew', 'howtous3e', 'howtouse3',
                          'howtous4e', 'howtouse4', 'howtousre', 'howtouser', 'howtousfe', 'howtousef', 'howtoused',
                          'howtouses', 'ow2', 'hw2', 'ho2', 'hhow2', 'hoow2', 'howw2', 'how22', 'ohw2', 'hwo2',
                          'ho2w', 'gow2', 'yow2', 'uow2', 'jow2', 'now2', 'bow2', 'hiw2', 'h9w2', 'h0w2', 'hpw2',
                          'hlw2', 'hkw2', 'hoq2', 'ho22', 'ho32', 'hoe2', 'hod2', 'hos2', 'hoa2', 'ghow2', 'hgow2',
                          'yhow2', 'hyow2', 'uhow2', 'huow2', 'jhow2', 'hjow2', 'nhow2', 'hnow2', 'bhow2', 'hbow2',
                          'hiow2', 'hoiw2', 'h9ow2', 'ho9w2', 'h0ow2', 'ho0w2', 'hpow2', 'hopw2', 'hlow2', 'holw2',
                          'hkow2', 'hokw2', 'hoqw2', 'howq2', 'ho2w2', 'ho3w2', 'how32', 'hoew2', 'howe2', 'hodw2',
                          'howd2', 'hosw2', 'hows2', 'hoaw2', 'howa2', 'ow2use', 'hw2use', 'ho2use', 'howuse', 'how2se',
                          'how2ue', 'how2us', 'hhow2use', 'hoow2use', 'howw2use', 'how22use', 'how2uuse', 'how2usse',
                          'how2usee', 'ohw2use', 'hwo2use', 'ho2wuse', 'howu2se', 'how2sue', 'how2ues', 'gow2use',
                          'yow2use', 'uow2use', 'jow2use', 'now2use', 'bow2use', 'hiw2use', 'h9w2use', 'h0w2use',
                          'hpw2use', 'hlw2use', 'hkw2use', 'hoq2use', 'ho22use', 'ho32use', 'hoe2use', 'hod2use',
                          'hos2use', 'hoa2use', 'how2yse', 'how27se', 'how28se', 'how2ise', 'how2kse', 'how2jse',
                          'how2hse', 'how2uae', 'how2uwe', 'how2uee', 'how2ude', 'how2uxe', 'how2uze', 'how2usw',
                          'how2us3', 'how2us4', 'how2usr', 'how2usf', 'how2usd', 'how2uss', 'ghow2use', 'hgow2use',
                          'yhow2use', 'hyow2use', 'uhow2use', 'huow2use', 'jhow2use', 'hjow2use', 'nhow2use',
                          'hnow2use', 'bhow2use', 'hbow2use', 'hiow2use', 'hoiw2use', 'h9ow2use', 'ho9w2use',
                          'h0ow2use', 'ho0w2use', 'hpow2use', 'hopw2use', 'hlow2use', 'holw2use', 'hkow2use',
                          'hokw2use', 'hoqw2use', 'howq2use', 'ho2w2use', 'ho3w2use', 'how32use', 'hoew2use',
                          'howe2use', 'hodw2use', 'howd2use', 'hosw2use', 'hows2use', 'hoaw2use', 'howa2use',
                          'how2yuse', 'how2uyse', 'how27use', 'how2u7se', 'how28use', 'how2u8se', 'how2iuse',
                          'how2uise', 'how2kuse', 'how2ukse', 'how2juse', 'how2ujse', 'how2huse', 'how2uhse',
                          'how2uase', 'how2usae', 'how2uwse', 'how2uswe', 'how2uese', 'how2udse', 'how2usde',
                          'how2uxse', 'how2usxe', 'how2uzse', 'how2usze', 'how2usew', 'how2us3e', 'how2use3',
                          'how2us4e', 'how2use4', 'how2usre', 'how2user', 'how2usfe', 'how2usef', 'how2used',
                          'how2uses', 'owtousebot', 'hwtousebot', 'hotousebot', 'howousebot', 'howtusebot',
                          'howtosebot', 'howtouebot', 'howtousbot', 'howtouseot', 'howtousebt', 'howtousebo',
                          'hhowtousebot', 'hoowtousebot', 'howwtousebot', 'howttousebot', 'howtoousebot',
                          'howtouusebot', 'howtoussebot', 'howtouseebot', 'howtousebbot', 'howtouseboot',
                          'howtousebott', 'ohwtousebot', 'hwotousebot', 'hotwousebot', 'howotusebot', 'howtuosebot',
                          'howtosuebot', 'howtouesbot', 'howtousbeot', 'howtouseobt', 'howtousebto', 'gowtousebot',
                          'yowtousebot', 'uowtousebot', 'jowtousebot', 'nowtousebot', 'bowtousebot', 'hiwtousebot',
                          'h9wtousebot', 'h0wtousebot', 'hpwtousebot', 'hlwtousebot', 'hkwtousebot', 'hoqtousebot',
                          'ho2tousebot', 'ho3tousebot', 'hoetousebot', 'hodtousebot', 'hostousebot', 'hoatousebot',
                          'howrousebot', 'how5ousebot', 'how6ousebot', 'howyousebot', 'howhousebot', 'howgousebot',
                          'howfousebot', 'howtiusebot', 'howt9usebot', 'howt0usebot', 'howtpusebot', 'howtlusebot',
                          'howtkusebot', 'howtoysebot', 'howto7sebot', 'howto8sebot', 'howtoisebot', 'howtoksebot',
                          'howtojsebot', 'howtohsebot', 'howtouaebot', 'howtouwebot', 'howtoueebot', 'howtoudebot',
                          'howtouxebot', 'howtouzebot', 'howtouswbot', 'howtous3bot', 'howtous4bot', 'howtousrbot',
                          'howtousfbot', 'howtousdbot', 'howtoussbot', 'howtousevot', 'howtousegot', 'howtousehot',
                          'howtousenot', 'howtousebit', 'howtouseb9t', 'howtouseb0t', 'howtousebpt', 'howtouseblt',
                          'howtousebkt', 'howtousebor', 'howtousebo5', 'howtousebo6', 'howtouseboy', 'howtouseboh',
                          'howtousebog', 'howtousebof', 'ghowtousebot', 'hgowtousebot', 'yhowtousebot', 'hyowtousebot',
                          'uhowtousebot', 'huowtousebot', 'jhowtousebot', 'hjowtousebot', 'nhowtousebot',
                          'hnowtousebot', 'bhowtousebot', 'hbowtousebot', 'hiowtousebot', 'hoiwtousebot',
                          'h9owtousebot', 'ho9wtousebot', 'h0owtousebot', 'ho0wtousebot', 'hpowtousebot',
                          'hopwtousebot', 'hlowtousebot', 'holwtousebot', 'hkowtousebot', 'hokwtousebot',
                          'hoqwtousebot', 'howqtousebot', 'ho2wtousebot', 'how2tousebot', 'ho3wtousebot',
                          'how3tousebot', 'hoewtousebot', 'howetousebot', 'hodwtousebot', 'howdtousebot',
                          'hoswtousebot', 'howstousebot', 'hoawtousebot', 'howatousebot', 'howrtousebot',
                          'howtrousebot', 'how5tousebot', 'howt5ousebot', 'how6tousebot', 'howt6ousebot',
                          'howytousebot', 'howtyousebot', 'howhtousebot', 'howthousebot', 'howgtousebot',
                          'howtgousebot', 'howftousebot', 'howtfousebot', 'howtiousebot', 'howtoiusebot',
                          'howt9ousebot', 'howto9usebot', 'howt0ousebot', 'howto0usebot', 'howtpousebot',
                          'howtopusebot', 'howtlousebot', 'howtolusebot', 'howtkousebot', 'howtokusebot',
                          'howtoyusebot', 'howtouysebot', 'howto7usebot', 'howtou7sebot', 'howto8usebot',
                          'howtou8sebot', 'howtouisebot', 'howtouksebot', 'howtojusebot', 'howtoujsebot',
                          'howtohusebot', 'howtouhsebot', 'howtouasebot', 'howtousaebot', 'howtouwsebot',
                          'howtouswebot', 'howtouesebot', 'howtoudsebot', 'howtousdebot', 'howtouxsebot',
                          'howtousxebot', 'howtouzsebot', 'howtouszebot', 'howtousewbot', 'howtous3ebot',
                          'howtouse3bot', 'howtous4ebot', 'howtouse4bot', 'howtousrebot', 'howtouserbot',
                          'howtousfebot', 'howtousefbot', 'howtousedbot', 'howtousesbot', 'howtousevbot',
                          'howtousebvot', 'howtousegbot', 'howtousebgot', 'howtousehbot', 'howtousebhot',
                          'howtousenbot', 'howtousebnot', 'howtousebiot', 'howtouseboit', 'howtouseb9ot',
                          'howtousebo9t', 'howtouseb0ot', 'howtousebo0t', 'howtousebpot', 'howtousebopt',
                          'howtouseblot', 'howtousebolt', 'howtousebkot', 'howtousebokt', 'howtousebort',
                          'howtousebotr', 'howtousebo5t', 'howtousebot5', 'howtousebo6t', 'howtousebot6',
                          'howtouseboyt', 'howtouseboty', 'howtouseboht', 'howtouseboth', 'howtousebogt',
                          'howtousebotg', 'howtouseboft', 'howtousebotf', 'ow2usebot', 'hw2usebot', 'ho2usebot',
                          'howusebot', 'how2sebot', 'how2uebot', 'how2usbot', 'how2useot', 'how2usebt', 'how2usebo',
                          'hhow2usebot', 'hoow2usebot', 'howw2usebot', 'how22usebot', 'how2uusebot', 'how2ussebot',
                          'how2useebot', 'how2usebbot', 'how2useboot', 'how2usebott', 'ohw2usebot', 'hwo2usebot',
                          'ho2wusebot', 'howu2sebot', 'how2suebot', 'how2uesbot', 'how2usbeot', 'how2useobt',
                          'how2usebto', 'gow2usebot', 'yow2usebot', 'uow2usebot', 'jow2usebot', 'now2usebot',
                          'bow2usebot', 'hiw2usebot', 'h9w2usebot', 'h0w2usebot', 'hpw2usebot', 'hlw2usebot',
                          'hkw2usebot', 'hoq2usebot', 'ho22usebot', 'ho32usebot', 'hoe2usebot', 'hod2usebot',
                          'hos2usebot', 'hoa2usebot', 'how2ysebot', 'how27sebot', 'how28sebot', 'how2isebot',
                          'how2ksebot', 'how2jsebot', 'how2hsebot', 'how2uaebot', 'how2uwebot', 'how2ueebot',
                          'how2udebot', 'how2uxebot', 'how2uzebot', 'how2uswbot', 'how2us3bot', 'how2us4bot',
                          'how2usrbot', 'how2usfbot', 'how2usdbot', 'how2ussbot', 'how2usevot', 'how2usegot',
                          'how2usehot', 'how2usenot', 'how2usebit', 'how2useb9t', 'how2useb0t', 'how2usebpt',
                          'how2useblt', 'how2usebkt', 'how2usebor', 'how2usebo5', 'how2usebo6', 'how2useboy',
                          'how2useboh', 'how2usebog', 'how2usebof', 'ghow2usebot', 'hgow2usebot', 'yhow2usebot',
                          'hyow2usebot', 'uhow2usebot', 'huow2usebot', 'jhow2usebot', 'hjow2usebot', 'nhow2usebot',
                          'hnow2usebot', 'bhow2usebot', 'hbow2usebot', 'hiow2usebot', 'hoiw2usebot', 'h9ow2usebot',
                          'ho9w2usebot', 'h0ow2usebot', 'ho0w2usebot', 'hpow2usebot', 'hopw2usebot', 'hlow2usebot',
                          'holw2usebot', 'hkow2usebot', 'hokw2usebot', 'hoqw2usebot', 'howq2usebot', 'ho2w2usebot',
                          'ho3w2usebot', 'how32usebot', 'hoew2usebot', 'howe2usebot', 'hodw2usebot', 'howd2usebot',
                          'hosw2usebot', 'hows2usebot', 'hoaw2usebot', 'howa2usebot', 'how2yusebot', 'how2uysebot',
                          'how27usebot', 'how2u7sebot', 'how28usebot', 'how2u8sebot', 'how2iusebot', 'how2uisebot',
                          'how2kusebot', 'how2uksebot', 'how2jusebot', 'how2ujsebot', 'how2husebot', 'how2uhsebot',
                          'how2uasebot', 'how2usaebot', 'how2uwsebot', 'how2uswebot', 'how2uesebot', 'how2udsebot',
                          'how2usdebot', 'how2uxsebot', 'how2usxebot', 'how2uzsebot', 'how2uszebot', 'how2usewbot',
                          'how2us3ebot', 'how2use3bot', 'how2us4ebot', 'how2use4bot', 'how2usrebot', 'how2userbot',
                          'how2usfebot', 'how2usefbot', 'how2usedbot', 'how2usesbot', 'how2usevbot', 'how2usebvot',
                          'how2usegbot', 'how2usebgot', 'how2usehbot', 'how2usebhot', 'how2usenbot', 'how2usebnot',
                          'how2usebiot', 'how2useboit', 'how2useb9ot', 'how2usebo9t', 'how2useb0ot', 'how2usebo0t',
                          'how2usebpot', 'how2usebopt', 'how2useblot', 'how2usebolt', 'how2usebkot', 'how2usebokt',
                          'how2usebort', 'how2usebotr', 'how2usebo5t', 'how2usebot5', 'how2usebo6t', 'how2usebot6',
                          'how2useboyt', 'how2useboty', 'how2useboht', 'how2useboth', 'how2usebogt', 'how2usebotg',
                          'how2useboft', 'how2usebotf', 'owtousestwdaily', 'hwtousestwdaily', 'hotousestwdaily',
                          'howousestwdaily', 'howtusestwdaily', 'howtosestwdaily', 'howtouestwdaily', 'howtousstwdaily',
                          'howtousetwdaily', 'howtouseswdaily', 'howtousestdaily', 'howtousestwaily', 'howtousestwdily',
                          'howtousestwdaly', 'howtousestwdaiy', 'howtousestwdail', 'hhowtousestwdaily',
                          'hoowtousestwdaily', 'howwtousestwdaily', 'howttousestwdaily', 'howtoousestwdaily',
                          'howtouusestwdaily', 'howtoussestwdaily', 'howtouseestwdaily', 'howtousesstwdaily',
                          'howtousesttwdaily', 'howtousestwwdaily', 'howtousestwddaily', 'howtousestwdaaily',
                          'howtousestwdaiily', 'howtousestwdailly', 'howtousestwdailyy', 'ohwtousestwdaily',
                          'hwotousestwdaily', 'hotwousestwdaily', 'howotusestwdaily', 'howtuosestwdaily',
                          'howtosuestwdaily', 'howtouesstwdaily', 'howtoussetwdaily', 'howtousetswdaily',
                          'howtouseswtdaily', 'howtousestdwaily', 'howtousestwadily', 'howtousestwdialy',
                          'howtousestwdaliy', 'howtousestwdaiyl', 'gowtousestwdaily', 'yowtousestwdaily',
                          'uowtousestwdaily', 'jowtousestwdaily', 'nowtousestwdaily', 'bowtousestwdaily',
                          'hiwtousestwdaily', 'h9wtousestwdaily', 'h0wtousestwdaily', 'hpwtousestwdaily',
                          'hlwtousestwdaily', 'hkwtousestwdaily', 'hoqtousestwdaily', 'ho2tousestwdaily',
                          'ho3tousestwdaily', 'hoetousestwdaily', 'hodtousestwdaily', 'hostousestwdaily',
                          'hoatousestwdaily', 'howrousestwdaily', 'how5ousestwdaily', 'how6ousestwdaily',
                          'howyousestwdaily', 'howhousestwdaily', 'howgousestwdaily', 'howfousestwdaily',
                          'howtiusestwdaily', 'howt9usestwdaily', 'howt0usestwdaily', 'howtpusestwdaily',
                          'howtlusestwdaily', 'howtkusestwdaily', 'howtoysestwdaily', 'howto7sestwdaily',
                          'howto8sestwdaily', 'howtoisestwdaily', 'howtoksestwdaily', 'howtojsestwdaily',
                          'howtohsestwdaily', 'howtouaestwdaily', 'howtouwestwdaily', 'howtoueestwdaily',
                          'howtoudestwdaily', 'howtouxestwdaily', 'howtouzestwdaily', 'howtouswstwdaily',
                          'howtous3stwdaily', 'howtous4stwdaily', 'howtousrstwdaily', 'howtousfstwdaily',
                          'howtousdstwdaily', 'howtoussstwdaily', 'howtouseatwdaily', 'howtousewtwdaily',
                          'howtouseetwdaily', 'howtousedtwdaily', 'howtousextwdaily', 'howtouseztwdaily',
                          'howtousesrwdaily', 'howtouses5wdaily', 'howtouses6wdaily', 'howtousesywdaily',
                          'howtouseshwdaily', 'howtousesgwdaily', 'howtousesfwdaily', 'howtousestqdaily',
                          'howtousest2daily', 'howtousest3daily', 'howtousestedaily', 'howtousestddaily',
                          'howtousestsdaily', 'howtousestadaily', 'howtousestwsaily', 'howtousestweaily',
                          'howtousestwraily', 'howtousestwfaily', 'howtousestwcaily', 'howtousestwxaily',
                          'howtousestwdqily', 'howtousestwdwily', 'howtousestwdsily', 'howtousestwdxily',
                          'howtousestwdzily', 'howtousestwdauly', 'howtousestwda8ly', 'howtousestwda9ly',
                          'howtousestwdaoly', 'howtousestwdally', 'howtousestwdakly', 'howtousestwdajly',
                          'howtousestwdaiky', 'howtousestwdaioy', 'howtousestwdaipy', 'howtousestwdailt',
                          'howtousestwdail6', 'howtousestwdail7', 'howtousestwdailu', 'howtousestwdailj',
                          'howtousestwdailh', 'howtousestwdailg', 'ghowtousestwdaily', 'hgowtousestwdaily',
                          'yhowtousestwdaily', 'hyowtousestwdaily', 'uhowtousestwdaily', 'huowtousestwdaily',
                          'jhowtousestwdaily', 'hjowtousestwdaily', 'nhowtousestwdaily', 'hnowtousestwdaily',
                          'bhowtousestwdaily', 'hbowtousestwdaily', 'hiowtousestwdaily', 'hoiwtousestwdaily',
                          'h9owtousestwdaily', 'ho9wtousestwdaily', 'h0owtousestwdaily', 'ho0wtousestwdaily',
                          'hpowtousestwdaily', 'hopwtousestwdaily', 'hlowtousestwdaily', 'holwtousestwdaily',
                          'hkowtousestwdaily', 'hokwtousestwdaily', 'hoqwtousestwdaily', 'howqtousestwdaily',
                          'ho2wtousestwdaily', 'how2tousestwdaily', 'ho3wtousestwdaily', 'how3tousestwdaily',
                          'hoewtousestwdaily', 'howetousestwdaily', 'hodwtousestwdaily', 'howdtousestwdaily',
                          'hoswtousestwdaily', 'howstousestwdaily', 'hoawtousestwdaily', 'howatousestwdaily',
                          'howrtousestwdaily', 'howtrousestwdaily', 'how5tousestwdaily', 'howt5ousestwdaily',
                          'how6tousestwdaily', 'howt6ousestwdaily', 'howytousestwdaily', 'howtyousestwdaily',
                          'howhtousestwdaily', 'howthousestwdaily', 'howgtousestwdaily', 'howtgousestwdaily',
                          'howftousestwdaily', 'howtfousestwdaily', 'howtiousestwdaily', 'howtoiusestwdaily',
                          'howt9ousestwdaily', 'howto9usestwdaily', 'howt0ousestwdaily', 'howto0usestwdaily',
                          'howtpousestwdaily', 'howtopusestwdaily', 'howtlousestwdaily', 'howtolusestwdaily',
                          'howtkousestwdaily', 'howtokusestwdaily', 'howtoyusestwdaily', 'howtouysestwdaily',
                          'howto7usestwdaily', 'howtou7sestwdaily', 'howto8usestwdaily', 'howtou8sestwdaily',
                          'howtouisestwdaily', 'howtouksestwdaily', 'howtojusestwdaily', 'howtoujsestwdaily',
                          'howtohusestwdaily', 'howtouhsestwdaily', 'howtouasestwdaily', 'howtousaestwdaily',
                          'howtouwsestwdaily', 'howtouswestwdaily', 'howtouesestwdaily', 'howtoudsestwdaily',
                          'howtousdestwdaily', 'howtouxsestwdaily', 'howtousxestwdaily', 'howtouzsestwdaily',
                          'howtouszestwdaily', 'howtousewstwdaily', 'howtous3estwdaily', 'howtouse3stwdaily',
                          'howtous4estwdaily', 'howtouse4stwdaily', 'howtousrestwdaily', 'howtouserstwdaily',
                          'howtousfestwdaily', 'howtousefstwdaily', 'howtousedstwdaily', 'howtouseastwdaily',
                          'howtousesatwdaily', 'howtouseswtwdaily', 'howtousesetwdaily', 'howtousesdtwdaily',
                          'howtousexstwdaily', 'howtousesxtwdaily', 'howtousezstwdaily', 'howtousesztwdaily',
                          'howtousesrtwdaily', 'howtousestrwdaily', 'howtouses5twdaily', 'howtousest5wdaily',
                          'howtouses6twdaily', 'howtousest6wdaily', 'howtousesytwdaily', 'howtousestywdaily',
                          'howtouseshtwdaily', 'howtousesthwdaily', 'howtousesgtwdaily', 'howtousestgwdaily',
                          'howtousesftwdaily', 'howtousestfwdaily', 'howtousestqwdaily', 'howtousestwqdaily',
                          'howtousest2wdaily', 'howtousestw2daily', 'howtousest3wdaily', 'howtousestw3daily',
                          'howtousestewdaily', 'howtousestwedaily', 'howtousestdwdaily', 'howtousestswdaily',
                          'howtousestwsdaily', 'howtousestawdaily', 'howtousestwadaily', 'howtousestwdsaily',
                          'howtousestwdeaily', 'howtousestwrdaily', 'howtousestwdraily', 'howtousestwfdaily',
                          'howtousestwdfaily', 'howtousestwcdaily', 'howtousestwdcaily', 'howtousestwxdaily',
                          'howtousestwdxaily', 'howtousestwdqaily', 'howtousestwdaqily', 'howtousestwdwaily',
                          'howtousestwdawily', 'howtousestwdasily', 'howtousestwdaxily', 'howtousestwdzaily',
                          'howtousestwdazily', 'howtousestwdauily', 'howtousestwdaiuly', 'howtousestwda8ily',
                          'howtousestwdai8ly', 'howtousestwda9ily', 'howtousestwdai9ly', 'howtousestwdaoily',
                          'howtousestwdaioly', 'howtousestwdalily', 'howtousestwdakily', 'howtousestwdaikly',
                          'howtousestwdajily', 'howtousestwdaijly', 'howtousestwdailky', 'howtousestwdailoy',
                          'howtousestwdaiply', 'howtousestwdailpy', 'howtousestwdailty', 'howtousestwdailyt',
                          'howtousestwdail6y', 'howtousestwdaily6', 'howtousestwdail7y', 'howtousestwdaily7',
                          'howtousestwdailuy', 'howtousestwdailyu', 'howtousestwdailjy', 'howtousestwdailyj',
                          'howtousestwdailhy', 'howtousestwdailyh', 'howtousestwdailgy', 'howtousestwdailyg',
                          'ow2usestwdaily', 'hw2usestwdaily', 'ho2usestwdaily', 'howusestwdaily', 'how2sestwdaily',
                          'how2uestwdaily', 'how2usstwdaily', 'how2usetwdaily', 'how2useswdaily', 'how2usestdaily',
                          'how2usestwaily', 'how2usestwdily', 'how2usestwdaly', 'how2usestwdaiy', 'how2usestwdail',
                          'hhow2usestwdaily', 'hoow2usestwdaily', 'howw2usestwdaily', 'how22usestwdaily',
                          'how2uusestwdaily', 'how2ussestwdaily', 'how2useestwdaily', 'how2usesstwdaily',
                          'how2usesttwdaily', 'how2usestwwdaily', 'how2usestwddaily', 'how2usestwdaaily',
                          'how2usestwdaiily', 'how2usestwdailly', 'how2usestwdailyy', 'ohw2usestwdaily',
                          'hwo2usestwdaily', 'ho2wusestwdaily', 'howu2sestwdaily', 'how2suestwdaily', 'how2uesstwdaily',
                          'how2ussetwdaily', 'how2usetswdaily', 'how2useswtdaily', 'how2usestdwaily', 'how2usestwadily',
                          'how2usestwdialy', 'how2usestwdaliy', 'how2usestwdaiyl', 'gow2usestwdaily', 'yow2usestwdaily',
                          'uow2usestwdaily', 'jow2usestwdaily', 'now2usestwdaily', 'bow2usestwdaily', 'hiw2usestwdaily',
                          'h9w2usestwdaily', 'h0w2usestwdaily', 'hpw2usestwdaily', 'hlw2usestwdaily', 'hkw2usestwdaily',
                          'hoq2usestwdaily', 'ho22usestwdaily', 'ho32usestwdaily', 'hoe2usestwdaily', 'hod2usestwdaily',
                          'hos2usestwdaily', 'hoa2usestwdaily', 'how2ysestwdaily', 'how27sestwdaily', 'how28sestwdaily',
                          'how2isestwdaily', 'how2ksestwdaily', 'how2jsestwdaily', 'how2hsestwdaily', 'how2uaestwdaily',
                          'how2uwestwdaily', 'how2ueestwdaily', 'how2udestwdaily', 'how2uxestwdaily', 'how2uzestwdaily',
                          'how2uswstwdaily', 'how2us3stwdaily', 'how2us4stwdaily', 'how2usrstwdaily', 'how2usfstwdaily',
                          'how2usdstwdaily', 'how2ussstwdaily', 'how2useatwdaily', 'how2usewtwdaily', 'how2useetwdaily',
                          'how2usedtwdaily', 'how2usextwdaily', 'how2useztwdaily', 'how2usesrwdaily', 'how2uses5wdaily',
                          'how2uses6wdaily', 'how2usesywdaily', 'how2useshwdaily', 'how2usesgwdaily', 'how2usesfwdaily',
                          'how2usestqdaily', 'how2usest2daily', 'how2usest3daily', 'how2usestedaily', 'how2usestddaily',
                          'how2usestsdaily', 'how2usestadaily', 'how2usestwsaily', 'how2usestweaily', 'how2usestwraily',
                          'how2usestwfaily', 'how2usestwcaily', 'how2usestwxaily', 'how2usestwdqily', 'how2usestwdwily',
                          'how2usestwdsily', 'how2usestwdxily', 'how2usestwdzily', 'how2usestwdauly', 'how2usestwda8ly',
                          'how2usestwda9ly', 'how2usestwdaoly', 'how2usestwdally', 'how2usestwdakly', 'how2usestwdajly',
                          'how2usestwdaiky', 'how2usestwdaioy', 'how2usestwdaipy', 'how2usestwdailt', 'how2usestwdail6',
                          'how2usestwdail7', 'how2usestwdailu', 'how2usestwdailj', 'how2usestwdailh', 'how2usestwdailg',
                          'ghow2usestwdaily', 'hgow2usestwdaily', 'yhow2usestwdaily', 'hyow2usestwdaily',
                          'uhow2usestwdaily', 'huow2usestwdaily', 'jhow2usestwdaily', 'hjow2usestwdaily',
                          'nhow2usestwdaily', 'hnow2usestwdaily', 'bhow2usestwdaily', 'hbow2usestwdaily',
                          'hiow2usestwdaily', 'hoiw2usestwdaily', 'h9ow2usestwdaily', 'ho9w2usestwdaily',
                          'h0ow2usestwdaily', 'ho0w2usestwdaily', 'hpow2usestwdaily', 'hopw2usestwdaily',
                          'hlow2usestwdaily', 'holw2usestwdaily', 'hkow2usestwdaily', 'hokw2usestwdaily',
                          'hoqw2usestwdaily', 'howq2usestwdaily', 'ho2w2usestwdaily', 'ho3w2usestwdaily',
                          'how32usestwdaily', 'hoew2usestwdaily', 'howe2usestwdaily', 'hodw2usestwdaily',
                          'howd2usestwdaily', 'hosw2usestwdaily', 'hows2usestwdaily', 'hoaw2usestwdaily',
                          'howa2usestwdaily', 'how2yusestwdaily', 'how2uysestwdaily', 'how27usestwdaily',
                          'how2u7sestwdaily', 'how28usestwdaily', 'how2u8sestwdaily', 'how2iusestwdaily',
                          'how2uisestwdaily', 'how2kusestwdaily', 'how2uksestwdaily', 'how2jusestwdaily',
                          'how2ujsestwdaily', 'how2husestwdaily', 'how2uhsestwdaily', 'how2uasestwdaily',
                          'how2usaestwdaily', 'how2uwsestwdaily', 'how2uswestwdaily', 'how2uesestwdaily',
                          'how2udsestwdaily', 'how2usdestwdaily', 'how2uxsestwdaily', 'how2usxestwdaily',
                          'how2uzsestwdaily', 'how2uszestwdaily', 'how2usewstwdaily', 'how2us3estwdaily',
                          'how2use3stwdaily', 'how2us4estwdaily', 'how2use4stwdaily', 'how2usrestwdaily',
                          'how2userstwdaily', 'how2usfestwdaily', 'how2usefstwdaily', 'how2usedstwdaily',
                          'how2useastwdaily', 'how2usesatwdaily', 'how2useswtwdaily', 'how2usesetwdaily',
                          'how2usesdtwdaily', 'how2usexstwdaily', 'how2usesxtwdaily', 'how2usezstwdaily',
                          'how2usesztwdaily', 'how2usesrtwdaily', 'how2usestrwdaily', 'how2uses5twdaily',
                          'how2usest5wdaily', 'how2uses6twdaily', 'how2usest6wdaily', 'how2usesytwdaily',
                          'how2usestywdaily', 'how2useshtwdaily', 'how2usesthwdaily', 'how2usesgtwdaily',
                          'how2usestgwdaily', 'how2usesftwdaily', 'how2usestfwdaily', 'how2usestqwdaily',
                          'how2usestwqdaily', 'how2usest2wdaily', 'how2usestw2daily', 'how2usest3wdaily',
                          'how2usestw3daily', 'how2usestewdaily', 'how2usestwedaily', 'how2usestdwdaily',
                          'how2usestswdaily', 'how2usestwsdaily', 'how2usestawdaily', 'how2usestwadaily',
                          'how2usestwdsaily', 'how2usestwdeaily', 'how2usestwrdaily', 'how2usestwdraily',
                          'how2usestwfdaily', 'how2usestwdfaily', 'how2usestwcdaily', 'how2usestwdcaily',
                          'how2usestwxdaily', 'how2usestwdxaily', 'how2usestwdqaily', 'how2usestwdaqily',
                          'how2usestwdwaily', 'how2usestwdawily', 'how2usestwdasily', 'how2usestwdaxily',
                          'how2usestwdzaily', 'how2usestwdazily', 'how2usestwdauily', 'how2usestwdaiuly',
                          'how2usestwda8ily', 'how2usestwdai8ly', 'how2usestwda9ily', 'how2usestwdai9ly',
                          'how2usestwdaoily', 'how2usestwdaioly', 'how2usestwdalily', 'how2usestwdakily',
                          'how2usestwdaikly', 'how2usestwdajily', 'how2usestwdaijly', 'how2usestwdailky',
                          'how2usestwdailoy', 'how2usestwdaiply', 'how2usestwdailpy', 'how2usestwdailty',
                          'how2usestwdailyt', 'how2usestwdail6y', 'how2usestwdaily6', 'how2usestwdail7y',
                          'how2usestwdaily7', 'how2usestwdailuy', 'how2usestwdailyu', 'how2usestwdailjy',
                          'how2usestwdailyj', 'how2usestwdailhy', 'how2usestwdailyh', 'how2usestwdailgy',
                          'how2usestwdailyg', 'nstruction', 'istruction', 'intruction', 'insruction', 'instuction',
                          'instrction', 'instrution', 'instrucion', 'instructon', 'instructin', 'instructio',
                          'iinstruction', 'innstruction', 'insstruction', 'insttruction', 'instrruction',
                          'instruuction', 'instrucction', 'instructtion', 'instructiion', 'instructioon',
                          'instructionn', 'nistruction', 'isntruction', 'intsruction', 'insrtuction', 'insturction',
                          'instrcution', 'instrutcion', 'instruciton', 'instructoin', 'instructino', 'unstruction',
                          '8nstruction', '9nstruction', 'onstruction', 'lnstruction', 'knstruction', 'jnstruction',
                          'ibstruction', 'ihstruction', 'ijstruction', 'imstruction', 'inatruction', 'inwtruction',
                          'inetruction', 'indtruction', 'inxtruction', 'inztruction', 'insrruction', 'ins5ruction',
                          'ins6ruction', 'insyruction', 'inshruction', 'insgruction', 'insfruction', 'insteuction',
                          'inst4uction', 'inst5uction', 'insttuction', 'instguction', 'instfuction', 'instduction',
                          'instryction', 'instr7ction', 'instr8ction', 'instriction', 'instrkction', 'instrjction',
                          'instrhction', 'instruxtion', 'instrudtion', 'instruftion', 'instruvtion', 'instrucrion',
                          'instruc5ion', 'instruc6ion', 'instrucyion', 'instruchion', 'instrucgion', 'instrucfion',
                          'instructuon', 'instruct8on', 'instruct9on', 'instructoon', 'instructlon', 'instructkon',
                          'instructjon', 'instructiin', 'instructi9n', 'instructi0n', 'instructipn', 'instructiln',
                          'instructikn', 'instructiob', 'instructioh', 'instructioj', 'instructiom', 'uinstruction',
                          'iunstruction', '8instruction', 'i8nstruction', '9instruction', 'i9nstruction',
                          'oinstruction', 'ionstruction', 'linstruction', 'ilnstruction', 'kinstruction',
                          'iknstruction', 'jinstruction', 'ijnstruction', 'ibnstruction', 'inbstruction',
                          'ihnstruction', 'inhstruction', 'injstruction', 'imnstruction', 'inmstruction',
                          'inastruction', 'insatruction', 'inwstruction', 'inswtruction', 'inestruction',
                          'insetruction', 'indstruction', 'insdtruction', 'inxstruction', 'insxtruction',
                          'inzstruction', 'insztruction', 'insrtruction', 'ins5truction', 'inst5ruction',
                          'ins6truction', 'inst6ruction', 'insytruction', 'instyruction', 'inshtruction',
                          'insthruction', 'insgtruction', 'instgruction', 'insftruction', 'instfruction',
                          'insteruction', 'instreuction', 'inst4ruction', 'instr4uction', 'instr5uction',
                          'instrtuction', 'instrguction', 'instrfuction', 'instdruction', 'instrduction',
                          'instryuction', 'instruyction', 'instr7uction', 'instru7ction', 'instr8uction',
                          'instru8ction', 'instriuction', 'instruiction', 'instrkuction', 'instrukction',
                          'instrjuction', 'instrujction', 'instrhuction', 'instruhction', 'instruxction',
                          'instrucxtion', 'instrudction', 'instrucdtion', 'instrufction', 'instrucftion',
                          'instruvction', 'instrucvtion', 'instrucrtion', 'instructrion', 'instruc5tion',
                          'instruct5ion', 'instruc6tion', 'instruct6ion', 'instrucytion', 'instructyion',
                          'instruchtion', 'instructhion', 'instrucgtion', 'instructgion', 'instructfion',
                          'instructuion', 'instructiuon', 'instruct8ion', 'instructi8on', 'instruct9ion',
                          'instructi9on', 'instructoion', 'instructlion', 'instructilon', 'instructkion',
                          'instructikon', 'instructjion', 'instructijon', 'instructioin', 'instructio9n',
                          'instructi0on', 'instructio0n', 'instructipon', 'instructiopn', 'instructioln',
                          'instructiokn', 'instructiobn', 'instructionb', 'instructiohn', 'instructionh',
                          'instructiojn', 'instructionj', 'instructiomn', 'instructionm', 'nst', 'ist', 'int', 'ins',
                          'iinst', 'innst', 'insst', 'instt', 'nist', 'isnt', 'ints', 'unst', '8nst', '9nst', 'onst',
                          'lnst', 'knst', 'jnst', 'ibst', 'ihst', 'ijst', 'imst', 'inat', 'inwt', 'inet', 'indt',
                          'inxt', 'inzt', 'insr', 'ins5', 'ins6', 'insy', 'insh', 'insg', 'insf', 'uinst', 'iunst',
                          '8inst', 'i8nst', '9inst', 'i9nst', 'oinst', 'ionst', 'linst', 'ilnst', 'kinst', 'iknst',
                          'jinst', 'ijnst', 'ibnst', 'inbst', 'ihnst', 'inhst', 'injst', 'imnst', 'inmst', 'inast',
                          'insat', 'inwst', 'inswt', 'inest', 'inset', 'indst', 'insdt', 'inxst', 'insxt', 'inzst',
                          'inszt', 'insrt', 'instr', 'ins5t', 'inst5', 'ins6t', 'inst6', 'insyt', 'insty', 'insht',
                          'insth', 'insgt', 'instg', 'insft', 'instf', 'orehelp', 'mrehelp', 'moehelp', 'morhelp',
                          'moreelp', 'morehlp', 'morehep', 'morehel', 'mmorehelp', 'moorehelp', 'morrehelp',
                          'moreehelp', 'morehhelp', 'moreheelp', 'morehellp', 'morehelpp', 'omrehelp', 'mroehelp',
                          'moerhelp', 'morheelp', 'moreehlp', 'morehlep', 'morehepl', 'norehelp', 'jorehelp',
                          'korehelp', 'mirehelp', 'm9rehelp', 'm0rehelp', 'mprehelp', 'mlrehelp', 'mkrehelp',
                          'moeehelp', 'mo4ehelp', 'mo5ehelp', 'motehelp', 'mogehelp', 'mofehelp', 'modehelp',
                          'morwhelp', 'mor3help', 'mor4help', 'morrhelp', 'morfhelp', 'mordhelp', 'morshelp',
                          'moregelp', 'moreyelp', 'moreuelp', 'morejelp', 'morenelp', 'morebelp', 'morehwlp',
                          'moreh3lp', 'moreh4lp', 'morehrlp', 'morehflp', 'morehdlp', 'morehslp', 'morehekp',
                          'moreheop', 'morehepp', 'morehelo', 'morehel0', 'morehell', 'nmorehelp', 'mnorehelp',
                          'jmorehelp', 'mjorehelp', 'kmorehelp', 'mkorehelp', 'miorehelp', 'moirehelp', 'm9orehelp',
                          'mo9rehelp', 'm0orehelp', 'mo0rehelp', 'mporehelp', 'moprehelp', 'mlorehelp', 'molrehelp',
                          'mokrehelp', 'moerehelp', 'mo4rehelp', 'mor4ehelp', 'mo5rehelp', 'mor5ehelp', 'motrehelp',
                          'mortehelp', 'mogrehelp', 'morgehelp', 'mofrehelp', 'morfehelp', 'modrehelp', 'mordehelp',
                          'morwehelp', 'morewhelp', 'mor3ehelp', 'more3help', 'more4help', 'morerhelp', 'morefhelp',
                          'moredhelp', 'morsehelp', 'moreshelp', 'moreghelp', 'morehgelp', 'moreyhelp', 'morehyelp',
                          'moreuhelp', 'morehuelp', 'morejhelp', 'morehjelp', 'morenhelp', 'morehnelp', 'morebhelp',
                          'morehbelp', 'morehwelp', 'morehewlp', 'moreh3elp', 'morehe3lp', 'moreh4elp', 'morehe4lp',
                          'morehrelp', 'moreherlp', 'morehfelp', 'moreheflp', 'morehdelp', 'morehedlp', 'morehselp',
                          'moreheslp', 'moreheklp', 'morehelkp', 'moreheolp', 'morehelop', 'moreheplp', 'morehelpo',
                          'morehel0p', 'morehelp0', 'morehelpl', 'lshelp', 'pshelp', 'plhelp', 'plselp', 'plshlp',
                          'plshep', 'plshel', 'pplshelp', 'pllshelp', 'plsshelp', 'plshhelp', 'plsheelp', 'plshellp',
                          'plshelpp', 'lpshelp', 'pslhelp', 'plhselp', 'plsehlp', 'plshlep', 'plshepl', 'olshelp',
                          '0lshelp', 'llshelp', 'pkshelp', 'poshelp', 'ppshelp', 'plahelp', 'plwhelp', 'plehelp',
                          'pldhelp', 'plxhelp', 'plzhelp', 'plsgelp', 'plsyelp', 'plsuelp', 'plsjelp', 'plsnelp',
                          'plsbelp', 'plshwlp', 'plsh3lp', 'plsh4lp', 'plshrlp', 'plshflp', 'plshdlp', 'plshslp',
                          'plshekp', 'plsheop', 'plshepp', 'plshelo', 'plshel0', 'plshell', 'oplshelp', 'polshelp',
                          '0plshelp', 'p0lshelp', 'lplshelp', 'pklshelp', 'plkshelp', 'ploshelp', 'plpshelp',
                          'plashelp', 'plsahelp', 'plwshelp', 'plswhelp', 'pleshelp', 'plsehelp', 'pldshelp',
                          'plsdhelp', 'plxshelp', 'plsxhelp', 'plzshelp', 'plszhelp', 'plsghelp', 'plshgelp',
                          'plsyhelp', 'plshyelp', 'plsuhelp', 'plshuelp', 'plsjhelp', 'plshjelp', 'plsnhelp',
                          'plshnelp', 'plsbhelp', 'plshbelp', 'plshwelp', 'plshewlp', 'plsh3elp', 'plshe3lp',
                          'plsh4elp', 'plshe4lp', 'plshrelp', 'plsherlp', 'plshfelp', 'plsheflp', 'plshdelp',
                          'plshedlp', 'plshselp', 'plsheslp', 'plsheklp', 'plshelkp', 'plsheolp', 'plshelop',
                          'plsheplp', 'plshelpo', 'plshel0p', 'plshelp0', 'plshelpl', 'utorial', 'ttorial', 'tuorial',
                          'tutrial', 'tutoial', 'tutoral', 'tutoril', 'tutoria', 'ttutorial', 'tuutorial', 'tuttorial',
                          'tutoorial', 'tutorrial', 'tutoriial', 'tutoriaal', 'tutoriall', 'uttorial', 'ttuorial',
                          'tuotrial', 'tutroial', 'tutoiral', 'tutorail', 'tutorila', 'rutorial', '5utorial',
                          '6utorial', 'yutorial', 'hutorial', 'gutorial', 'futorial', 'tytorial', 't7torial',
                          't8torial', 'titorial', 'tktorial', 'tjtorial', 'thtorial', 'turorial', 'tu5orial',
                          'tu6orial', 'tuyorial', 'tuhorial', 'tugorial', 'tuforial', 'tutirial', 'tut9rial',
                          'tut0rial', 'tutprial', 'tutlrial', 'tutkrial', 'tutoeial', 'tuto4ial', 'tuto5ial',
                          'tutotial', 'tutogial', 'tutofial', 'tutodial', 'tutorual', 'tutor8al', 'tutor9al',
                          'tutoroal', 'tutorlal', 'tutorkal', 'tutorjal', 'tutoriql', 'tutoriwl', 'tutorisl',
                          'tutorixl', 'tutorizl', 'tutoriak', 'tutoriao', 'tutoriap', 'rtutorial', 'trutorial',
                          '5tutorial', 't5utorial', '6tutorial', 't6utorial', 'ytutorial', 'tyutorial', 'htutorial',
                          'thutorial', 'gtutorial', 'tgutorial', 'ftutorial', 'tfutorial', 'tuytorial', 't7utorial',
                          'tu7torial', 't8utorial', 'tu8torial', 'tiutorial', 'tuitorial', 'tkutorial', 'tuktorial',
                          'tjutorial', 'tujtorial', 'tuhtorial', 'turtorial', 'tutrorial', 'tu5torial', 'tut5orial',
                          'tu6torial', 'tut6orial', 'tutyorial', 'tuthorial', 'tugtorial', 'tutgorial', 'tuftorial',
                          'tutforial', 'tutiorial', 'tutoirial', 'tut9orial', 'tuto9rial', 'tut0orial', 'tuto0rial',
                          'tutporial', 'tutoprial', 'tutlorial', 'tutolrial', 'tutkorial', 'tutokrial', 'tutoerial',
                          'tutoreial', 'tuto4rial', 'tutor4ial', 'tuto5rial', 'tutor5ial', 'tutotrial', 'tutortial',
                          'tutogrial', 'tutorgial', 'tutofrial', 'tutorfial', 'tutodrial', 'tutordial', 'tutoruial',
                          'tutoriual', 'tutor8ial', 'tutori8al', 'tutor9ial', 'tutori9al', 'tutoroial', 'tutorioal',
                          'tutorlial', 'tutorilal', 'tutorkial', 'tutorikal', 'tutorjial', 'tutorijal', 'tutoriqal',
                          'tutoriaql', 'tutoriwal', 'tutoriawl', 'tutorisal', 'tutoriasl', 'tutorixal', 'tutoriaxl',
                          'tutorizal', 'tutoriazl', 'tutoriakl', 'tutorialk', 'tutoriaol', 'tutorialo', 'tutoriapl',
                          'tutorialp', 'ow', 'hw', 'ho', 'hhow', 'hoow', 'howw', 'ohw', 'hwo', 'gow', 'yow', 'uow',
                          'jow', 'now', 'bow', 'hiw', 'h9w', 'h0w', 'hpw', 'hlw', 'hkw', 'hoq', 'ho3', 'hoe', 'hod',
                          'hos', 'hoa', 'ghow', 'hgow', 'yhow', 'hyow', 'uhow', 'huow', 'jhow', 'hjow', 'nhow', 'hnow',
                          'bhow', 'hbow', 'hiow', 'hoiw', 'h9ow', 'ho9w', 'h0ow', 'ho0w', 'hpow', 'hopw', 'hlow',
                          'holw', 'hkow', 'hokw', 'hoqw', 'howq', 'ho3w', 'how3', 'hoew', 'howe', 'hodw',
                          'howd', 'hosw', 'hows', 'hoaw', 'howa', 'কিভাবে2', 'com 2', 'jak 2', 'πώς2', 'cómo2',
                          'kuidas2', 'miten2', 'કેવી રીતે2', 'yadda2', 'איך 2', 'कैसे2', 'hogyan2', 'どうやって2', 'kaip2',
                          'kā2', 'कसे2', 'bagaimana2', 'jak2', 'cum2', 'как2', 'ako2', 'хов2', 'vipi2', 'எப்படி2',
                          'ఎలా2', 'nasıl2', 'کیسے 2', '怎么样2', '怎麼樣2', 'com2', 'کیسے2'],
                 extras={'emoji': "info", "args": {}, "dev": True,
                         "description_keys": ["how2.meta.description1", "how2.meta.description2",
                                              "how2.meta.description3"],
                         "name_key": "how2.slash.name"},
                 brief="how2.slash.description",
                 description="{0}\n⦾ {1}\n⦾ {2}")
    async def how2(self, ctx):
        """
        This function is the entry point for the how to use command when called traditionally

        Args:
            ctx (discord.ext.commands.Context): The context of the command call
        """
        await self.how_to_command(ctx)

    # @slash_command(name='how2', name_localizations=stw.I18n.construct_slash_dict("how2.slash.name"),
    #                description="View how to use STW Daily",
    #                description_localizations=stw.I18n.construct_slash_dict("how2.slash.description"),
    #                guild_ids=stw.guild_ids)
    # async def slashhow2(self, ctx):
    #     """
    #     This function is the entry point for the how to use command when called via slash command
    #
    #     Args:
    #         ctx: The context of the command
    #     """
    #     await self.how_to_command(ctx)


def setup(client):
    """
    This function is called when the cog is loaded via load_extension

    Args:
        client: The bot client
    """
    client.add_cog(HowTo(client))
