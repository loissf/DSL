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

                output = shell.open_file(text)      # user input = $file <path>
            else:
                output = shell.run_command(text)    # user input = $expression
        else:
            output = shell.input_text(text)         # user input = message

        if output:
            print(f'{output}')

if __name__ == '__main__':
    main()