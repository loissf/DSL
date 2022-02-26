from shell import Shell

def main():

    shell = Shell()

    while True:
        text = input('>>')

        output = shell.run_command(text)

        if output:
            print(f'{output}')

if __name__ == '__main__':
    main()