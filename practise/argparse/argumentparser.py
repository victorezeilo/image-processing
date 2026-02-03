import argparse
def main():
    parser = argparse.ArgumentParser(description="What the script does...")

    #positional argument
    parser.add_argument("file_path", help="the input file path")

    subparsers = parser.add_subparsers(help="sub-command help info", dest="subparser_name")

    cmd_parser = subparsers.add_parser("cmd", help="help for cmd")

    cmd_parser.add_argument("--optional_1", dest="opt1", default="something default", help="the 1st optional argument")

    run_parser = subparsers.add_parser("run", help="help for run")

    #optional arguments
    run_parser.add_argument("--optional_1", default="something default", help="the 1st optional arg")
    parser.add_argument("-o", "--optional_2", action="store_true", help="the 2nd optional arg")

    #argument with a type
    parser.add_argument("--job", type=int, help="the number of jobs")

    args = parser.parse_args()

    print(args)
    print(args.subparser_name)

if __name__ == "__main__":
    main()
