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
        if message.author == client.user:
            return

        text = message.content
        output = None

        if text.startswith('$'):
            text = text[1:len(text)]
            print(f'{message.guild}: #{message.channel} >> {text}')
            output = shell.run_command(text)
        else:
            output = shell.input_text(text)
        if output:
            print(f'{message.guild}: #{message.channel} <- {output}')
            await message.channel.send(output)

    client.run(TOKEN)

if __name__ == '__main__':
    main()



    