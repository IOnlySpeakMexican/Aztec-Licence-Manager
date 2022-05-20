
import discord
from discord import  Guild, Interaction, Role, ui, app_commands
from datetime import datetime
import requests
import secrets
import sqlite3
import datetime
from discord.ext import commands, tasks
import discord
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
            await tree.sync(guild = discord.Object(id=YOUSERVERIDHERE))
            self.synced = True
        print("Logged on")
        license_check.start()

class addkey(ui.Modal, title="Licence Generation"):
    amount = ui.TextInput(label="Amount", style=discord.TextStyle.short, placeholder="Amount of keys to generate.", required = True, max_length=50)
    role = ui.TextInput(label="Role ID", style=discord.TextStyle.short, placeholder="The role ID you wish to be linked to key", required = True, max_length=50)
    timee = ui.TextInput(label="Time", style=discord.TextStyle.short, placeholder="Time till expire (year-month-day)", required = True, max_length=50)
    async def on_submit(self, interaction: discord.Interaction):
        for val in range(int(self.amount.value)):
            key = f"{secrets.token_hex(4)}-{secrets.token_hex(4)}-{secrets.token_hex(4)}"
            cur.execute(f"INSERT INTO Keys (Key, Exipry, Role) VALUES ('{key}', '{self.timee}', '{self.role}')")
            connection.commit()
            await interaction.user.send(key)
        embed = discord.Embed(title="Howl Licence Manager", description="```Successfully Created Licence Keys```")
        embed.add_field(name="Expire Date", value=f"``{self.timee}``", inline=True)
        embed.add_field(name="Amount", value=f"``{self.amount}``", inline=True)
        await interaction.response.send_message(embed=embed)

class claimkey(ui.Modal, title="Licence Redemption"):
    key = ui.TextInput(label="Licence", style=discord.TextStyle.short, placeholder="Licence key to be redeemed", required = True, max_length=50)
    async def on_submit(self, interaction: discord.Interaction):
        resule = cur.execute(f"SELECT * FROM Keys WHERE Keys.Key = '{self.key}'")
        data = cur.fetchone()
        if data:
            query = cur.execute(f"DELETE FROM Keys WHERE Keys.Key = '{self.key}'")
            cur.execute(f"INSERT INTO Users (Licence, User, Role, Expires) VALUES ('{self.key}','{interaction.user.id}', '{data[2]}', '{data[1]}')")
            role = interaction.guild.get_role(data[2])
            await interaction.user.add_roles(role)
            connection.commit()
            embed = discord.Embed(title="Howl Licence Manager", description="```Successfully Redeemed Licence Key```")
            embed.add_field(name="Expire Date", value=f"``{data[1]}``", inline=True)
            embed.add_field(name="Role", value=f"``<@{data[2]}>``", inline=True)
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(title="Howl Licence Manager", description="```Licence Key Was Not Found```")
            await interaction.response.send_message(embed=embed)


@tasks.loop(seconds=10.0)
async def license_check():
    cur.execute(f"SELECT * FROM Users WHERE Users.Expires = '{datetime.date.today()}'")
    res = cur.fetchone()
    if res:
        guild = aclient.get_guild(YOUSERVERIDHERE)
        member = guild.get_member(int(res[1]))
        print(res[2])
        role = get(guild.roles, id=int(res[2]))
        await member.remove_roles(role)
        cur.execute(f"DELETE FROM Users WHERE Users.Licence = '{res[0]}'")
        connection.commit()
    else:
        cur.execute(f"SELECT * FROM Keys WHERE Keys.Exipry = '{datetime.date.today()}'")
        ress = cur.fetchone()
        if ress:
            cur.execute(f"DELETE FROM Keys WHERE Keys.Exipry = '{datetime.date.today()}'")
            connection.commit()
            print("deleted from key table")


aclient = client()
tree = app_commands.CommandTree(aclient)

@tree.command(guild = discord.Object(id=YOUSERVERIDHERE), name = "generate", description="Brings up generation prompt")
async def generate(interaction: discord.Interaction):
    await interaction.response.send_modal(addkey())

@tree.command(guild = discord.Object(id=YOUSERVERIDHERE), name = "redeem", description="Brings up redmeption prompt")
async def redeem(interaction: discord.Interaction):
    await interaction.response.send_modal(claimkey())

@tree.command(guild = discord.Object(id=YOUSERVERIDHERE), name = "expiration", description="Brings up expiration prompt")
async def expiration(interaction: discord.Interaction):
        resule = cur.execute(f"SELECT * FROM Users WHERE Users.User = '{interaction.user.id}'")
        data = cur.fetchone()
        if data:
            embed = discord.Embed(title="Howl Licence Manager", description="```Successfully Found Licence Key```")
            embed.add_field(name="Expire Date", value=f"``{data[3]}``", inline=True)
            embed.add_field(name="Role", value=f"``<@{data[1]}>``", inline=True)
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(title="Howl Licence Manager", description="```Licence Key Was Not Found For You```")
            await interaction.response.send_message(embed=embed)


aclient.run("")



