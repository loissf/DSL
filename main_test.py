from shell import Shell
from events import Event, EventType

async def output_callback(value):
    print(value)

def main():

    shell = Shell(output_callback=output_callback)

    while True:
        text = input('>>')
        result = None
        if text.startswith('$'):
            text = text[1:len(text)]

            if text.startswith('file '):
                text = text[5:len(text)]

                result = shell.open_file(text)      # user input = $file <path>
            else:
                result = shell.run_command(text)    # user input = $expression
        else:
            result = shell.throw_event(Event(EventType.MESSAGE, (text, 'shell', None)))         # user input = message

        if result != 0:
            print(f'{result}')

if __name__ == '__main__':
    main()