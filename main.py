import discord
from shell import Shell

# Discord bot logic token
TOKEN = ''

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

        if text.startswith('$'):
            text = text[1:len(text)]
            print(f'{message.guild}: #{message.channel} >> {text}')
            output = shell.run_command(text)
            if output:
                print(f'{message.guild}: #{message.channel} <- {output}')
                await message.channel.send(output)
        else:
            pass

    client.run(TOKEN)

if __name__ == '__main__':
    main()



    
