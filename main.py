from email.policy import HTTP
from http.client import HTTPException
import discord
from shell import Shell

# Discord bot token
TOKEN = ''
with open('TOKEN.txt', 'r') as file:
    TOKEN = file.read()

def main():

    client = discord.Client()

    @client.event
    async def on_ready():
        print(f'we have logged as {client.user}')

    @client.event
    async def on_message(message):
        # Ignore messages from the bot itself
        if message.author == client.user:
            return

        async def output_callback(value):
            try:
                await message.channel.send(value)
                print(f'{message.guild}: #{message.channel} <- {value}')
            except discord.errors.HTTPException:
                await message.channel.send('_ _')   # emtpy message
                print(f'{message.guild}: #{message.channel} <- {{EMPTY}}')
                

        shell = Shell(output_callback, message.guild, message.channel)

        text = message.content
        result = None
        
        # Check if input is a command
        # Send a command to the shell
        if text.startswith('$'):
            text = text[1:len(text)]
            print(f'{message.guild}: #{message.channel} >> {text}')
            shell.change_context(message.guild, message.channel)
            result = shell.run_command(text)

        elif text.startswith('```') and text.endswith('```'):
            text = text[3:-3]
            if text.startswith('dsl'):
                text = text[3:len(text)]
                print(f'{message.guild}: #{message.channel} >> code block:\n{text}')
                shell.change_context(message.guild, message.channel)
                result = shell.run_command(text)
        
        # If input is just a message
        # Send a text input to the shell
        else:
            shell.change_context(message.guild, message.channel)
            author = ''
            if isinstance(message.author, discord.Member):
                author = message.author.nick if message.author.nick else message.author.name
            else:
                author = message.author.name
            result = shell.input_text(text, author)
            if result:
                print(f'{message.guild}: #{message.channel} : {text}')

        # Once the message is processed, send any output the shell may have produced
        if result and result != 0:
            print(result)
            await message.channel.send('```' + str(result) + '```')


    client.run(TOKEN)

if __name__ == '__main__':
    main()



    
