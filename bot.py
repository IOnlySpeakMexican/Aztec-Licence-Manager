import discord
from discord import  Guild, Interaction, Role, ui, app_commands
from datetime import datetime
import requests
import secrets
import sqlite3
import datetime
from discord.ext import commands, tasks
import discord
from datetime import *
import random
import os
import string
from discord.utils import get
connection = sqlite3.connect("Users.db")
cur = connection.cursor()
connection.row_factory = lambda cursor, row: row[0]
intents = discord.Intents.all()  
intents.members = True


class client(discord.Client):
    def __init__(self) -> None:
        super().__init__(intents = intents)
        self.synced = False
    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            await tree.sync(guild = discord.Object(id=YOURSERVERIDHERE))
            self.synced = True
        license_check.start()
        print("Logged on")


def generate_Licence(plan, RoleID, Time):
    licence = f"AZTEC-{''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))}-{''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))}-{''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))}"
    cur.execute(f"INSERT INTO Keys (Licence, Plan, RoleID, Time) VALUES ('{licence}','{plan}','{RoleID}','{Time}')")
    connection.commit()
    return licence

@tasks.loop(seconds=10.0)
async def license_check():
    res = cur.execute(f"SELECT * FROM Users WHERE Users.Expire = '{datetime.now().strftime('%d-%m-%Y')}'")
    res = res.fetchone()
    if res:
        cur.execute(f"DELETE FROM Users WHERE Users.Userid = '{int(res[1])}'")
        connection.commit()
        guild = aclient.get_guild(YOURSERVERIDHERE)
        member = guild.get_member(int(res[1]))
        role = get(guild.roles, id=int(res[3]))
        await member.remove_roles(role)
        print("Removed User: " + res[0])
    else:
        print("Removed No Users")


aclient = client()
tree = app_commands.CommandTree(aclient)

@tree.command(guild = discord.Object(id=YOURSERVERIDHERE), name = 'generate', description='Generate Licence Keys') 
async def slash3(interaction: discord.Interaction, plan: str, amount: int, roleid: str, time: int): 
    role = discord.utils.find(lambda r: r.name == 'Owner', interaction.guild.roles)
    if role in interaction.user.roles:
        open(f"Data/Keys{interaction.user.display_name}.txt", "x", encoding="utf-8").close()
        with open(f"Data/Keys{interaction.user.display_name}.txt", "r+", encoding="utf-8") as f2:
            for i in range(int(amount)):
                Licence = generate_Licence(plan,roleid,time)
                f2.write(f"{Licence}\n")
        file = discord.File(f"Data/Keys{interaction.user.display_name}.txt", filename=f"Data/Keys{interaction.user.display_name}.txt")
        embed = discord.Embed(title="Aztec Licence Handler", colour=discord.Colour(0xfa8c68))
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/988618112024871004/1072739850018639912/pngtree-a-logo-simple-and-minimalistic-image_301991.png")
        embed.set_footer(text="Aztec", icon_url="https://cdn.discordapp.com/attachments/988618112024871004/1072739850018639912/pngtree-a-logo-simple-and-minimalistic-image_301991.png")
        embed.add_field(name="Plan", value=plan, inline=True)
        embed.add_field(name="Amount", value=amount, inline=True)
        embed.add_field(name="Role ID", value=roleid, inline=True)
        embed.add_field(name="Time", value=time, inline=True)
        channel = await interaction.user.create_dm()
        await channel.send(file=file)
        os.remove(f"Data/Keys{interaction.user.display_name}.txt")
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(title="Aztec Licence Handler", description="**Invalid** Permissions", colour=discord.Colour(0xfa8c68))
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/988618112024871004/1072739850018639912/pngtree-a-logo-simple-and-minimalistic-image_301991.png")
        embed.set_footer(text="Aztec", icon_url="https://cdn.discordapp.com/attachments/988618112024871004/1072739850018639912/pngtree-a-logo-simple-and-minimalistic-image_301991.png")
        await interaction.response.send_message(embed=embed)

@tree.command(guild = discord.Object(id=YOURSERVERIDHERE), name = 'redeem', description='Redeem Licence Key') 
async def slash3(interaction: discord.Interaction, licence: str): 
    res = cur.execute(f"SELECT * FROM Keys WHERE Keys.Licence = '{licence}'")
    res = res.fetchone()
    if res:
        date = datetime.now() + timedelta(days=int(res[3]))
        date = date.strftime('%d-%m-%Y')
        cur.execute(f"DELETE FROM Keys WHERE Keys.Licence = '{licence}'")
        cur.execute(f"INSERT INTO Users (Username,UserID,Plan,RoleID,Expire) VALUES ('{interaction.user.display_name}','{interaction.user.id}','{res[1]}','{res[2]}','{date}')")
        connection.commit()
        role = discord.utils.get(interaction.user.guild.roles, id=int(res[2]))
        embed = discord.Embed(title="Aztec Licence Handler", description="**Successfully** Redeemed Licence Key!", colour=discord.Colour(0xfa8c68))
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/988618112024871004/1072739850018639912/pngtree-a-logo-simple-and-minimalistic-image_301991.png")
        embed.set_footer(text="Aztec", icon_url="https://cdn.discordapp.com/attachments/988618112024871004/1072739850018639912/pngtree-a-logo-simple-and-minimalistic-image_301991.png")
        embed.add_field(name="Plan", value=res[1], inline=True)
        embed.add_field(name="Role ID", value=res[2], inline=True)
        embed.add_field(name="Time", value=res[3], inline=True)
        await interaction.user.add_roles(role)
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(title="Aztec Licence Handler", description="Licence Key Not **Found**", colour=discord.Colour(0xfa8c68))
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/988618112024871004/1072739850018639912/pngtree-a-logo-simple-and-minimalistic-image_301991.png")
        embed.set_footer(text="Aztec", icon_url="https://cdn.discordapp.com/attachments/988618112024871004/1072739850018639912/pngtree-a-logo-simple-and-minimalistic-image_301991.png")
        await interaction.response.send_message(embed=embed)

@tree.command(guild = discord.Object(id=YOURSERVERIDHERE), name = 'info', description='Get User Info') 
async def slash3(interaction: discord.Interaction, userid: str): 
    res = cur.execute(f"SELECT * FROM Users WHERE Users.UserID = '{userid}'")
    res = res.fetchone()
    if res:
        embed = discord.Embed(title="Aztec Licence Handler", description="**Successfully** Found User", colour=discord.Colour(0xfa8c68))
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/988618112024871004/1072739850018639912/pngtree-a-logo-simple-and-minimalistic-image_301991.png")
        embed.set_footer(text="Aztec", icon_url="https://cdn.discordapp.com/attachments/988618112024871004/1072739850018639912/pngtree-a-logo-simple-and-minimalistic-image_301991.png")
        embed.add_field(name="Plan", value=res[1], inline=True)
        embed.add_field(name="Username", value=res[0], inline=True)
        embed.add_field(name="Role ID", value=res[2], inline=True)
        embed.add_field(name="Time", value=res[3], inline=True)
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(title="Aztec Licence Handler", description="User Not **Found**", colour=discord.Colour(0xfa8c68))
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/988618112024871004/1072739850018639912/pngtree-a-logo-simple-and-minimalistic-image_301991.png")
        embed.set_footer(text="Aztec", icon_url="https://cdn.discordapp.com/attachments/988618112024871004/1072739850018639912/pngtree-a-logo-simple-and-minimalistic-image_301991.png")
        await interaction.response.send_message(embed=embed)

aclient.run("")
