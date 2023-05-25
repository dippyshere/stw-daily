# Image synthesis of power level
import asyncio
import io
import math

import discord
from PIL import Image, ImageDraw, ImageFont


# example for you <3
def generate_power_level_image(power_level, author_id):
    power_level_float, power_level_int = math.modf(power_level)

    width, height = (200, 200)

    power_level_str = str(int(power_level_int))  # here
    power_level_display = Image.new(mode="RGBA",  # here
                                    size=(width, height),  # here
                                    color=(30, 30, 1, 1))  # here

    draw_image = ImageDraw.Draw(power_level_display, 'RGBA')
    burbank = ImageFont.truetype('burbank-big-condensed-black.otf', 90)

    _, _, w, _ = draw_image.textbbox((0, 0), power_level_str, font=burbank)

    draw_image.text(((width - w) / 2, 40),
                    power_level_str,
                    fill=(255, 255, 255),
                    font=burbank,
                    )

    draw_image.rounded_rectangle([20, 130, 180, 170], radius=3, outline=(255, 255, 255), width=4)

    percentage = 180 * power_level_float

    draw_image.rounded_rectangle([20, 130, percentage, 170], radius=3, fill=(255, 255, 255), outline=(255, 255, 255),
                                 width=4)
    arr = io.BytesIO()
    power_level_display.save(arr, format='PNG')
    arr.seek(0)
    return discord.File(arr, filename=f"{author_id}power_level.png")  # send this as a file lol


arr = io.BytesIO()
power_level_display.save(arr, format='PNG')
arr.seek(0)
f = discord.File(arr, filename=f"{ctx.author.id}power_level.png")
embed_colour = self.client.colours["reward_magenta"]
embed = discord.Embed(colour=embed_colour,
                      title="sup sup",
                      description="hoi")

embed.set_thumbnail(url=f"attachment://{ctx.author.id}power_level.png")
await ctx.send(file=f, embed=embed)


async def async_generate_power_level_thumbnail(power_level, user_snowflake):
    return await asyncio.gather(asyncio.to_thread(generate_power_level_image, power_level, user_snowflake))
