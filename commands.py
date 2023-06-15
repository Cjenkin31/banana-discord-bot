def DefineAllCommands():
    mainServerId=discord.Object(id=222147212681936896)
    sideServerId=discord.Object(id=1101665956314501180)
    servers = [mainServerId, sideServerId]
    for server in servers:
        @tree.command(name="randomtank", description="rolls a random tank hero from overwatch", guild=server)
        async def first_command(interaction):
            await interaction.response.send_message(random.choice(overwatchHeroTankList))

        @tree.command(name="randomsupport", description="rolls a random support hero from overwatch", guild=server)
        async def first_command(interaction):
            await interaction.response.send_message(random.choice(overwatchHeroSupportList))

        @tree.command(name="randomvoiceline", description="rolls a random voiceline from overwatch", guild=server)
        async def first_command(interaction):
            await interaction.response.send_message(random.choice(overwatchVoiceLines))

        @tree.command(name="randomdps", description="rolls a random support dps from overwatch", guild=server)
        async def first_command(interaction):
            await interaction.response.send_message(random.choice(overwatchHeroDPSList))

        @tree.command(name="randomroleow", description="rolls a random role for overwatch", guild=server)
        async def first_command(interaction):
            await interaction.response.send_message(random.choice(overwatchRoleList))

        @tree.command(name="randomgamemodeow", description="rolls a random game mode for overwatch", guild=server)
        async def first_command(interaction):
            await interaction.response.send_message(random.choice(overwatchGameModeList))

        @tree.command(name = "yesno", description = "picks yes or no", guild=server) 
        async def first_command(interaction):
            await interaction.response.send_message(random.choice(["Yes", "No"]))

        @tree.command(name = "pickfromlist", description = "input things to be chosen seperated by a ,. Ex. Overwatch,League", guild=server) 
        async def self(interaction: discord.Interaction, items: str):
            await interaction.response.send_message(random.choice(items.split(',')))

        @tree.command(name = "randomnumber", description = "Choose a random number between 2 inputs", guild=server) 
        async def self(interaction: discord.Interaction, items: str):
            try:
                await interaction.response.send_message(random.randint(int(items.split(',')[0]),int(items.split(',')[1])))
            except:
                await interaction.response.send_message("Either you messed up or I did. But It was prob you")

        @tree.command(name="rhythmroll", description="rolls number 1-100", guild=server) 
        async def first_command(interaction):
            await interaction.response.send_message(random.randint(0,100))

        @tree.command(name = "randomfullcomp", description = "Rolls 1 tank, 2 dps, 2 supports", guild=server) 
        async def first_command(interaction):
            firstDPS=random.choice(overwatchHeroDPSList)
            secondDPS=random.choice(overwatchHeroDPSList)
            while(firstDPS==secondDPS):
                secondDPS=random.choice(overwatchHeroDPSList)
            
            firstSupport=random.choice(overwatchHeroSupportList)
            secondSupport=random.choice(overwatchHeroSupportList)
            while(firstSupport==secondSupport):
                secondSupport=random.choice(overwatchHeroSupportList)
            
            await interaction.response.send_message("Tank: "+random.choice(overwatchHeroTankList)+"\nDPS: "+firstDPS+", "+secondDPS+"\nSupport: "+firstSupport+", "+secondSupport)

@tree.command(name = "coinflip", description = "flips a coin") 
async def self(interaction: discord.Interaction, items: str):
    await interaction.response.send_message(random.choice(["Heads","Tails"]))