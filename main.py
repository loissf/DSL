import discord
from shell import Shell

# Discord bot token
TOKEN = ''
with open('TOKEN.txt', 'r') as file:
    TOKEN = file.read()

def main():

    shell = Shell()

    client = discord.Client()

    @client.event
    async def on_ready():
        print(f'we have logged as {client.user}')

    @client.event
    async def on_message(message):
        # Ignore messages from the bot itself
        if message.author == client.user:
            return

        text = message.content
        output = None

        # Check if input is a command
        # Send a command to the shell
        if text.startswith('$'):
            text = text[1:len(text)]
            print(f'{message.guild}: #{message.channel} >> {text}')
            output = shell.run_command(text)

        if text.startswith('```') and text.endswith('```'):
            text = text[3:-3]
            if text.startswith('dsl'):
                text = text[3:len(text)]
                print(f'{message.guild}: #{message.channel} >> code block:\n{text}')
                output = shell.run_command(text)
        
        # If input is just a message
        # Send a text input to the shell
        else:
            output = shell.input_text(text, message.author.name)
            if output:
                print(f'{message.guild}: #{message.channel} : {text}')

        # Once the message is processed, send any output the shell may have produced
        if output:
            print(f'{message.guild}: #{message.channel} <- {output}')
            await message.channel.send(output)

    client.run(TOKEN)

if __name__ == '__main__':
    main()



    