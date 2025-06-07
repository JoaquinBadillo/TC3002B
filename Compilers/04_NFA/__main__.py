from argparse import ArgumentParser
from nfa import NFA


if __name__ == "__main__":
    argparser = ArgumentParser()
    argparser.add_argument("-v",
                           "--verbose",
                           dest="verbose",
                           help="Enable verbose mode (show table creation)",
                           action="store_true")
    args = argparser.parse_args()
    verbose = bool(args.verbose)

    states = input("Write states separated by commas:\n").split(',')
    alphabet = input("Write alphabet separated by commas:\n").split(',')
    q0 = input("Write starting state: ")
    accepting = input("Write accepting states separated by commas:\n").split(',')
    
    print("Write transition function rows separated by commas")
    print("  - States that map to multiple states should use |")
    print("  - Use \\ for empty")
    print("  - Write empty line to end")
    
    print(f"State  {'  '.join(alphabet)}")
    transition = {s: dict() for s in states}
    
    while((row := input().strip()) != ''):
        row = row.split(',')
        for column, char in zip(row[1:], alphabet):
            if column == '\\':
                continue

            mapping = set(column.split('|'))
            transition[row[0]][char] = mapping  
    
    nfa = NFA(states=set(states),
              alphabet=set(alphabet),
              initial=q0,
              accepting=set(accepting),
              transition=transition)

    dfa = nfa.to_dfa(print_state=verbose)
    print(f"\n\n{'*'*50}\n\n")
    print(dfa)
    dfa.to_graph(filename='dfa')
