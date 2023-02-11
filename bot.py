import discord
from discord import app_commands
from datetime import datetime
import sqlite3
from discord.ext import commands, tasks
import discord
from datetime import *
import random
import os
import string
import json
from discord.utils import get

connection = sqlite3.connect("Users.db")
cur = connection.cursor()
connection.row_factory = lambda cursor, row: row[0]
intents = discord.Intents.all()  
intents.members = True

with open('config.json') as config_file:
    data = json.load(config_file)


class client(discord.Client):
    def __init__(self) -> None:
        super().__init__(intents = intents)
        self.synced = False
    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            await tree.sync(guild = discord.Object(id=int(data["ServerID"])))
            self.synced = True
        license_check.start()
        slot_check.start()
        print("Logged on")


def generate_Licence(plan, RoleID, Time, Hours):
    licence = f"AZTEC-{''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))}-{''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))}-{''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))}"
    cur.execute(f"INSERT INTO Keys (Licence, Plan, RoleID, Days, Hours) VALUES ('{licence}','{plan}','{RoleID}','{Time}','{Hours}')")
    connection.commit()
    return licence

@tasks.loop(seconds=50.0)
async def slot_check():
    res = cur.execute(f"SELECT * FROM Slots WHERE Slots.ShopTime = '{datetime.now().strftime('%d-%m-%Y')}'")
    res = res.fetchone()
    if res:
        cur.execute(f"DELETE FROM Slots WHERE Slots.ShopTime = '{datetime.now().strftime('%d-%m-%Y')}'")
        connection.commit()
        guild = aclient.get_guild(int(data["ServerID"]))
        member = guild.get_member(int(res[0]))
        channel = guild.get_channel(int(res[3]))
        await channel.delete()
        embed = discord.Embed(title="Aztec Slot Handler", description="Your License Has **Ended**", colour=discord.Colour(0xfa8c68))
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/988618112024871004/1072739850018639912/pngtree-a-logo-simple-and-minimalistic-image_301991.png")
        embed.set_footer(text="Aztec", icon_url="https://cdn.discordapp.com/attachments/988618112024871004/1072739850018639912/pngtree-a-logo-simple-and-minimalistic-image_301991.png")
        print("Removed Shop: " + res[0] + "\nShop Name: " + res[1])
    else:
        print("Removed No Shop")

@tasks.loop(seconds=50.0)
async def license_check():
    res = cur.execute(f"SELECT * FROM Users WHERE Users.Expire = '{datetime.now().strftime('%d-%m-%Y-%H')}'")
    res = res.fetchone()
    if res:
        cur.execute(f"DELETE FROM Users WHERE Users.Userid = '{int(res[1])}'")
        connection.commit()
        guild = aclient.get_guild(int(data["ServerID"]))
        member = guild.get_member(int(res[1]))
        channel = await member.create_dm()
        role = get(guild.roles, id=int(res[3]))
        embed = discord.Embed(title="Aztec Licence Handler", description="Your License Has **Ended**", colour=discord.Colour(0xfa8c68))
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/988618112024871004/1072739850018639912/pngtree-a-logo-simple-and-minimalistic-image_301991.png")
        embed.set_footer(text="Aztec", icon_url="https://cdn.discordapp.com/attachments/988618112024871004/1072739850018639912/pngtree-a-logo-simple-and-minimalistic-image_301991.png")
        await channel.send(embed=embed)
        await member.remove_roles(role)
        print("Removed User: " + res[0])
    else:
        print("Removed No Users")


aclient = client()
tree = app_commands.CommandTree(aclient)

@tree.command(guild = discord.Object(id=int(data["ServerID"])), name = 'generate', description='Generate Licence Keys') 
async def slash3(interaction: discord.Interaction, plan: str, amount: int, roleid: str, days: int, hours: str): 
    role = discord.utils.find(lambda r: r.name == data["AdminRole"], interaction.guild.roles)
    if role in interaction.user.roles:
        open(f"Data/Keys{interaction.user.display_name}.txt", "x", encoding="utf-8").close()
        with open(f"Data/Keys{interaction.user.display_name}.txt", "r+", encoding="utf-8") as f2:
            for i in range(int(amount)):
                Licence = generate_Licence(plan,roleid,days,hours)
                f2.write(f"{Licence}\n")
        file = discord.File(f"Data/Keys{interaction.user.display_name}.txt", filename=f"Data/Keys{interaction.user.display_name}.txt")
        date = datetime.now() + timedelta(days=int(days), hours=int(hours))
        date = date.strftime('%d-%m-%Y-%H')
        embed = discord.Embed(title="Aztec Licence Handler", colour=discord.Colour(0xfa8c68))
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/988618112024871004/1072739850018639912/pngtree-a-logo-simple-and-minimalistic-image_301991.png")
        embed.set_footer(text="Aztec", icon_url="https://cdn.discordapp.com/attachments/988618112024871004/1072739850018639912/pngtree-a-logo-simple-and-minimalistic-image_301991.png")
        embed.add_field(name="Plan", value=f"``{plan}``", inline=True)
        embed.add_field(name="Amount", value=f"``{amount}``", inline=True)
        embed.add_field(name="Role ID", value=f"``{roleid}``", inline=True)
        embed.add_field(name="Expiration", value=f"``In {days} Days And {hours} Hours``", inline=True)
        channel = await interaction.user.create_dm()
        await interaction.response.send_message(embed=embed)
        embed = discord.Embed(title="Aztec Licence Handler", description="**Successfully** Generated License Keys!", colour=discord.Colour(0xfa8c68))
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/988618112024871004/1072739850018639912/pngtree-a-logo-simple-and-minimalistic-image_301991.png")
        embed.set_footer(text="Aztec", icon_url="https://cdn.discordapp.com/attachments/988618112024871004/1072739850018639912/pngtree-a-logo-simple-and-minimalistic-image_301991.png")
        await channel.send(embed=embed)
        await channel.send(file=file)
        os.remove(f"Data/Keys{interaction.user.display_name}.txt")
    else:
        embed = discord.Embed(title="Aztec Licence Handler", description="**Invalid** Permissions", colour=discord.Colour(0xfa8c68))
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/988618112024871004/1072739850018639912/pngtree-a-logo-simple-and-minimalistic-image_301991.png")
        embed.set_footer(text="Aztec", icon_url="https://cdn.discordapp.com/attachments/988618112024871004/1072739850018639912/pngtree-a-logo-simple-and-minimalistic-image_301991.png")
        await interaction.response.send_message(embed=embed)

@tree.command(guild = discord.Object(id=int(data["ServerID"])), name = 'redeem', description='Redeem Licence Key') 
async def slash3(interaction: discord.Interaction, licence: str): 
    res = cur.execute(f"SELECT * FROM Keys WHERE Keys.Licence = '{licence}'")
    res = res.fetchone()
    if res:
        date = datetime.now() + timedelta(days=int(res[3]), hours=int(res[4]))
        date = date.strftime('%d-%m-%Y-%H')
        cur.execute(f"DELETE FROM Keys WHERE Keys.Licence = '{licence}'")
        cur.execute(f"INSERT INTO Users (Username,UserID,Plan,RoleID,Expire) VALUES ('{interaction.user.display_name}','{interaction.user.id}','{res[1]}','{res[2]}','{date}')")
        connection.commit()
        role = discord.utils.get(interaction.user.guild.roles, id=int(res[2]))
        embed = discord.Embed(title="Aztec Licence Handler", description="**Successfully** Redeemed Licence Key!", colour=discord.Colour(0xfa8c68))
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/988618112024871004/1072739850018639912/pngtree-a-logo-simple-and-minimalistic-image_301991.png")
        embed.set_footer(text="Aztec", icon_url="https://cdn.discordapp.com/attachments/988618112024871004/1072739850018639912/pngtree-a-logo-simple-and-minimalistic-image_301991.png")
        embed.add_field(name="Plan", value=f"``{res[1]}``", inline=True)
        embed.add_field(name="Role ID", value=f"``{res[2]}``", inline=True)
        embed.add_field(name="Time", value=f"``{date}``", inline=True)
        await interaction.user.add_roles(role)
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(title="Aztec Licence Handler", description="Licence Key Not **Found**", colour=discord.Colour(0xfa8c68))
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/988618112024871004/1072739850018639912/pngtree-a-logo-simple-and-minimalistic-image_301991.png")
        embed.set_footer(text="Aztec", icon_url="https://cdn.discordapp.com/attachments/988618112024871004/1072739850018639912/pngtree-a-logo-simple-and-minimalistic-image_301991.png")
        await interaction.response.send_message(embed=embed)

@tree.command(guild = discord.Object(id=int(data["ServerID"])), name = 'info', description='Get User Info') 
async def slash3(interaction: discord.Interaction, userid: str): 
    role = discord.utils.find(lambda r: r.name == data["AdminRole"], interaction.guild.roles)
    if role in interaction.user.roles:
        res = cur.execute(f"SELECT * FROM Users WHERE Users.UserID = '{userid}'")
        res = res.fetchone()
        if res:
            embed = discord.Embed(title="Aztec Licence Handler", description="**Successfully** Found User", colour=discord.Colour(0xfa8c68))
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/988618112024871004/1072739850018639912/pngtree-a-logo-simple-and-minimalistic-image_301991.png")
            embed.set_footer(text="Aztec", icon_url="https://cdn.discordapp.com/attachments/988618112024871004/1072739850018639912/pngtree-a-logo-simple-and-minimalistic-image_301991.png")
            embed.add_field(name="Plan", value=f"``{res[1]}``", inline=True)
            embed.add_field(name="Username", value=f"``{res[0]}``", inline=True)
            embed.add_field(name="Role ID", value=f"``{res[2]}``", inline=True)
            embed.add_field(name="Time", value=f"``{res[4]}``", inline=True)
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(title="Aztec Licence Handler", description="User Not **Found**", colour=discord.Colour(0xfa8c68))
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/988618112024871004/1072739850018639912/pngtree-a-logo-simple-and-minimalistic-image_301991.png")
            embed.set_footer(text="Aztec", icon_url="https://cdn.discordapp.com/attachments/988618112024871004/1072739850018639912/pngtree-a-logo-simple-and-minimalistic-image_301991.png")
            await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(title="Aztec Slot Handler", description="**Invalid** Permissions", colour=discord.Colour(0xfa8c68))
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/988618112024871004/1072739850018639912/pngtree-a-logo-simple-and-minimalistic-image_301991.png")
        embed.set_footer(text="Aztec", icon_url="https://cdn.discordapp.com/attachments/988618112024871004/1072739850018639912/pngtree-a-logo-simple-and-minimalistic-image_301991.png")
        await interaction.response.send_message(embed=embed)

@tree.command(guild = discord.Object(id=int(data["ServerID"])), name = 'createslot', description='Creates a slot for a user') 
async def slash3(interaction: discord.Interaction, userid: str, shopname: str, shoptime: str): 
    role = discord.utils.find(lambda r: r.name == data["AdminRole"], interaction.guild.roles)
    if role in interaction.user.roles:
        date = datetime.now() + timedelta(days=int(shoptime))
        date = date.strftime('%d-%m-%Y')
        guild = aclient.get_guild(int(data["ServerID"]))
        user = guild.get_member(int(userid))
        category = discord.utils.get(guild.categories, id=data["CateogryID"])
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(send_messages=False, view_channel=True),
            user: discord.PermissionOverwrite(send_messages=True, mention_everyone=True)
        }
        channel = await guild.create_text_channel(name=f"🎫┃ {shopname}", category=category,overwrites=overwrites)
        channelid = channel.id
        cur.execute(f"INSERT INTO Slots (UserID,ShopName,ShopTime,ChannelID) VALUES ('{userid}','{shopname}','{date}','{channelid}')")
        connection.commit()
        embed = discord.Embed(title="Aztec Slot Handler", description=f"Your Slot Has Begun 1 Ping / 24 Hours. This Channel Will Be Deleted On **{date}**", colour=discord.Colour(0xfa8c68))
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/988618112024871004/1072739850018639912/pngtree-a-logo-simple-and-minimalistic-image_301991.png")
        embed.set_footer(text="Aztec", icon_url="https://cdn.discordapp.com/attachments/988618112024871004/1072739850018639912/pngtree-a-logo-simple-and-minimalistic-image_301991.png")
        await channel.send(embed=embed)
        embed = discord.Embed(title="Aztec Slot Handler", description=f"The Slot Was Created **Successfully**", colour=discord.Colour(0xfa8c68))
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/988618112024871004/1072739850018639912/pngtree-a-logo-simple-and-minimalistic-image_301991.png")
        embed.set_footer(text="Aztec", icon_url="https://cdn.discordapp.com/attachments/988618112024871004/1072739850018639912/pngtree-a-logo-simple-and-minimalistic-image_301991.png")
        embed.add_field(name="Shop Name", value=f"``{shopname}``", inline=True)
        embed.add_field(name="Shop Time", value=f"``{date}``", inline=True)
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(title="Aztec Slot Handler", description="**Invalid** Permissions", colour=discord.Colour(0xfa8c68))
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/988618112024871004/1072739850018639912/pngtree-a-logo-simple-and-minimalistic-image_301991.png")
        embed.set_footer(text="Aztec", icon_url="https://cdn.discordapp.com/attachments/988618112024871004/1072739850018639912/pngtree-a-logo-simple-and-minimalistic-image_301991.png")
        await interaction.response.send_message(embed=embed)
    
@tree.command(guild = discord.Object(id=int(data["ServerID"])), name = 'addtime', description='Adds more time to a users key') 
async def slash3(interaction: discord.Interaction, userid: str, days: int, hours: int): 
    role = discord.utils.find(lambda r: r.name == data["AdminRole"], interaction.guild.roles)
    if role in interaction.user.roles:
        res = cur.execute(f"SELECT * FROM Users WHERE Users.UserID = '{userid}'")
        res = res.fetchone()
        if res:
            expire = str(res[4]).split("-")
            day = int(expire[0])
            month = int(expire[1])
            year = int(expire[2])
            hour = int(expire[3])

            hour = hour + int(hours)
            day = day + int(days)

            finaltime = f"{day}-{month}-{year}-{hour}"
            cur.execute(f"UPDATE Users SET Expire = '{finaltime}' WHERE Users.UserID = '{userid}'")
            connection.commit()
            embed = discord.Embed(title="Aztec Slot Handler", description=f"**Successfully** added more time to <@{userid}>", colour=discord.Colour(0xfa8c68))
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/988618112024871004/1072739850018639912/pngtree-a-logo-simple-and-minimalistic-image_301991.png")
            embed.set_footer(text="Aztec", icon_url="https://cdn.discordapp.com/attachments/988618112024871004/1072739850018639912/pngtree-a-logo-simple-and-minimalistic-image_301991.png")
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(title="Aztec Slot Handler", description="User id not **Found**", colour=discord.Colour(0xfa8c68))
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/988618112024871004/1072739850018639912/pngtree-a-logo-simple-and-minimalistic-image_301991.png")
            embed.set_footer(text="Aztec", icon_url="https://cdn.discordapp.com/attachments/988618112024871004/1072739850018639912/pngtree-a-logo-simple-and-minimalistic-image_301991.png")
            await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(title="Aztec Slot Handler", description="**Invalid** Permissions", colour=discord.Colour(0xfa8c68))
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/988618112024871004/1072739850018639912/pngtree-a-logo-simple-and-minimalistic-image_301991.png")
        embed.set_footer(text="Aztec", icon_url="https://cdn.discordapp.com/attachments/988618112024871004/1072739850018639912/pngtree-a-logo-simple-and-minimalistic-image_301991.png")
        await interaction.response.send_message(embed=embed)

@tree.command(guild = discord.Object(id=int(data["ServerID"])), name = 'removetime', description='Removes time from a users key') 
async def slash3(interaction: discord.Interaction, userid: str, days: int, hours: int): 
    role = discord.utils.find(lambda r: r.name == data["AdminRole"], interaction.guild.roles)
    if role in interaction.user.roles:
        res = cur.execute(f"SELECT * FROM Users WHERE Users.UserID = '{userid}'")
        res = res.fetchone()
        if res:
            expire = str(res[4]).split("-")
            day = int(expire[0])
            month = int(expire[1])
            year = int(expire[2])
            hour = int(expire[3])

            hour = hour - int(hours)
            day = day - int(days)

            finaltime = f"{day}-{month}-{year}-{hour}"
            cur.execute(f"UPDATE Users SET Expire = '{finaltime}' WHERE Users.UserID = '{userid}'")
            connection.commit()
            embed = discord.Embed(title="Aztec Slot Handler", description=f"**Successfully** removed time from <@{userid}> key", colour=discord.Colour(0xfa8c68))
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/988618112024871004/1072739850018639912/pngtree-a-logo-simple-and-minimalistic-image_301991.png")
            embed.set_footer(text="Aztec", icon_url="https://cdn.discordapp.com/attachments/988618112024871004/1072739850018639912/pngtree-a-logo-simple-and-minimalistic-image_301991.png")
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(title="Aztec Slot Handler", description="User id not **Found**", colour=discord.Colour(0xfa8c68))
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/988618112024871004/1072739850018639912/pngtree-a-logo-simple-and-minimalistic-image_301991.png")
            embed.set_footer(text="Aztec", icon_url="https://cdn.discordapp.com/attachments/988618112024871004/1072739850018639912/pngtree-a-logo-simple-and-minimalistic-image_301991.png")
            await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(title="Aztec Slot Handler", description="**Invalid** Permissions", colour=discord.Colour(0xfa8c68))
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/988618112024871004/1072739850018639912/pngtree-a-logo-simple-and-minimalistic-image_301991.png")
        embed.set_footer(text="Aztec", icon_url="https://cdn.discordapp.com/attachments/988618112024871004/1072739850018639912/pngtree-a-logo-simple-and-minimalistic-image_301991.png")
        await interaction.response.send_message(embed=embed)

aclient.run(data["Token"])
