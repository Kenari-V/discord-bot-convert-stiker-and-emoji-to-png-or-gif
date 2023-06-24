import discord
import os
import dotenv
import requests
from discord.ext import commands
from settingtoken import token
from PIL import Image, ImageSequence
import io
import aiohttp
import re

bot = commands.Bot(command_prefix='$A ', intents = discord.Intents.all())
intents = discord.Intents.default()
intents.message_content = True

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Kenari-V Github"))
    print('Login {0.user}'.format(bot))


#convert emoji to png or gif
headers = {
    'Authorization': 'Your Bot Token',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

@bot.command()
async def convertemoji(ctx):
    if ctx.message.reference and ctx.message.reference.resolved:
        reply_message = ctx.message.reference.resolved
        emojis = re.findall(r'<a?:(.+?):(\d+)>', reply_message.content)
        if emojis:
            for emoji_name, emoji_id in emojis:
                emoji_url = f'https://cdn.discordapp.com/emojis/{emoji_id}'

                response = requests.get(emoji_url, headers=headers)
                if response.status_code == 200:
                    file_extension = response.headers.get('Content-Type').split('/')[1]
                    if file_extension == 'gif':
                        emoji_data = response.content
                        image = Image.open(io.BytesIO(emoji_data))

                        # change format to gif, if not animation convert to png
                        if not image.is_animated:
                            image.seek(0)
                            image.save(f'{emoji_name}.gif')
                            with open(f'{emoji_name}.gif', 'rb') as f:
                                await ctx.send(file=discord.File(f))
                            os.remove(f'{emoji_name}.gif')
                        else:
                            await ctx.send(file=discord.File(io.BytesIO(emoji_data), filename=f'{emoji_name}.gif'))
                    else:
                        with open(f'{emoji_name}.png', 'wb') as f:
                            f.write(response.content)

                        with open(f'{emoji_name}.png', 'rb') as f:
                            await ctx.send(file=discord.File(f))
                    
                    # delete file after send to discord
                    if os.path.exists(f'{emoji_name}.png'):
                        os.remove(f'{emoji_name}.png')
                else:
                    await ctx.send(f'failed to get emoji with ID: {emoji_id}')
        else:
            await ctx.send('no emoji in message')
    else:
        await ctx.send('use this command with a reply containing emoji.')

#convert stiker to gif or png
@bot.command()
async def convertstiker(ctx):
    replied_message = await ctx.fetch_message(ctx.message.reference.message_id)

    if replied_message.stickers:
        async with aiohttp.ClientSession() as session:
            for sticker in replied_message.stickers:
                sticker_url = sticker.url

                async with session.get(sticker_url) as response:
                    if response.status == 200:
                        sticker_bytes = await response.read()
                        sticker_image = Image.open(io.BytesIO(sticker_bytes))

                    # Convert animated Sticker to gif
                    if sticker_image.is_animated:
                        frames = [frame.copy() for frame in ImageSequence.Iterator(sticker_image)]
                        gif_bytes = io.BytesIO()
                        frames[0].save(
                             gif_bytes,
                             format='GIF',
                             save_all=True,
                             append_images=frames[1:],
                             loop=0
                        )
                        gif_bytes.seek(0)
                        await ctx.send(file=discord.File(gif_bytes, filename='sticker.gif'))

                    # convert normal stiker to png
                    else:
                        png_bytes = io.BytesIO()
                        sticker_image.save(png_bytes, format='PNG')
                        png_bytes.seek(0)
                        await ctx.send(file=discord.File(png_bytes, filename='sticker.png'))
    
bot.run(token)