# mongo interaction

import asyncio
import os

import discord
import discord.ext.commands as ext
from discord import Option

import stwutil as stw

# did u install motor no :) :( :c oh lmao sorry racism
# access monogodb async

import motor.motor_asyncio


async def insert_default_document(client, user_snowflake):
    pass


# define function to read mongodb database and return a list of all the collections in the database
async def get_user_document(client, user_snowflake):
    # which one lol
    # what do u want to call the database and collection? actually we can just slap this into config too :) sure
    document = await client.stw_database.find_one({'user_snowflake': user_snowflake})
    print(document)  # need default document insertion if it cant find it hm

    if document is None:
        document = await insert_default_document(client, user_snowflake)
    return document


# create dictionary with user snowflake as keys and a list of all documents in that collection asi summon thee
# how should we make mongodb thingy ;w;
# um we should like gram their snowflake = 123456789012345678 post it on the gram? brb sending it to hayk yes ofc
#  yes yes :3 then um we make the collection or something and store some cool ggdpr whatever complaint info in it ;o
# idk what do you think we should do
# i was more asking if the function should request certain portions of the data or the entire thing per user
# so like either u grab the entire like document for the user or just like whatever u want but i think grab entire thing?
# the tables probably gonna be pretty small per user so just grab the whole thing
# also i got the localhost mongo running on that port localhost:27017

def setup(client):
    # we can add new variables and stuff to client right through setup
    # can use that with the ext stuff so we can add new functawn

    # Create the client used for communication with the mongodb on setup
    mongodb_url = os.environ[
        client.config['mango']["uri_env_var"]]  # idk lmao i forgot how toml works in python too used to rust
    client.database_client = motor.motor_asyncio.AsyncIOMotorClient(mongodb_url)
    # gotta restart the terminal or something cause it hasnt picked up u added the env var yet kk nya~
    # how the hell wooooo yeah baby
    # ill relaunch py
    # lets see who's faster, me or github copilot
    database = client.config['mango']["database"]
    collection = client.config['mango']["collection"]
    client.stw_database = client.database_client[database][collection]
    # i win <3 idk if it works tho lmao i keep forgetting u dont need to switch to the daily core.py file to run
    client.get_user_document = get_user_document
    # client.get_collections = get_collections
    # :3
    client.add_cog(BongoTest(client))


# cog for the reloading related commands.
class BongoTest(ext.Cog):

    def __init__(self, client):
        self.client = client
        # can u not unindent by ctrl shift + [ weird nanny

    async def bongo_command(self, ctx):
        embed_colour = self.client.colours["auth_white"]
        embed = discord.Embed(title=await stw.add_emoji_title(self.client, "Bongo Test", "spongebob"),
                              description=f'\u200b\n{await self.client.get_user_document(self.client, ctx.author.id)}\n\u200b',
                              color=embed_colour)
        embed = await stw.set_thumbnail(self.client, embed, "clown")
        embed = await stw.add_requested_footer(ctx, embed)
        # brb back gtg soonish
        await stw.slash_send_embed(ctx, False, embed)

    @ext.command(name='bongo',
                 extras={'emoji': "spongebob", "args": {'ext': 'what args'}},
                 brief="mango drum b",
                 description="donkey kong ooga booga's cogs to mango changes")
    async def bongo(self, ctx):
        await self.bongo_command(ctx)
