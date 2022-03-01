import shell

from shell import Shell

def main():

    shell = Shell()

    while True:
        text = input('>>')
        output = None
        if text.startswith('$'):
            text = text[1:len(text)]

            if text.startswith('file '):
                text = text[5:len(text)]

                lines = []
                with open(text, 'r') as file:
                    lines += file.readlines()

                program = ''
                for line in lines:
                    if '#' in line:
                        line = line[0:line.index('#')]
                    program += line
            else:
                program = text

            output = shell.run_command(program)
        else:
            output = shell.input_text(text)

        if output:
            print(f'{output}')

if __name__ == '__main__':
    main()