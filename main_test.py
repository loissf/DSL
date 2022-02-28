import shell

from shell import Shell

def main():

    shell = Shell()

    while True:
        text = input('>>')

        if text.startswith('file '):
            text = text[5:len(text)]

            lines = []
            with open(text, 'r') as file:
                lines += file.readlines()

            program = ''
            for line in lines:
                program += line
        else:
            program = text

        output = shell.run_command(program)

        if output:
            print(f'{output}')

if __name__ == '__main__':
    main()