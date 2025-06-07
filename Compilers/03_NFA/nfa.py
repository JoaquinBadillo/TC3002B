from collections import deque
from dataclasses import dataclass
from typing import Dict, Set

from tabulate import tabulate
from graphviz import Digraph

def transition_table_str(transition, alphabet, title="Transition Table") -> str:
    alphabet = sorted(alphabet)

    all_states = set(transition.keys())
    for trans in transition.values():
        for dest in trans.values():
            if isinstance(dest, set):
                all_states.update(dest)
            else:
                all_states.add(dest)

    states = sorted(all_states)


    headers = ["State"] + alphabet
    rows = []

    for state in states:
        row = [state]
        for symbol in alphabet:
            default = set() if any(isinstance(v, set) for t in transition.values() for v in t.values()) else ''
            target = transition.get(state, {}).get(symbol, default)

            if isinstance(target, set):
                row.append("∅" if not target else "{" + ",".join(sorted(target)) + "}")
            else:
                row.append(str(target))
        rows.append(row)

    table_str = f"{title}:\n" + tabulate(rows, headers=headers, tablefmt="grid")
    return table_str

@dataclass
class DFA:
    states: Set[str]
    alphabet: Set[str]  
    transition: Dict[str, Dict[str, str]]
    initial: str
    accepting: Set[str]

    def __str__(self) -> str:
        return transition_table_str(self.transition,
                                    self.alphabet,
                                    title="Transition Table")
    
    def to_graph(self, filename="dfa", view=True):
        dot = Digraph(comment="DFA")
        dot.attr(rankdir="LR")

        for state in self.states:
            if state in self.accepting:
                dot.node(state, shape='doublecircle')
            else:
                dot.node(state, shape='circle')

        # Start arrow (goes from nothing to start)
        dot.node('', shape='none')
        dot.edge('', self.initial)

        # Transition edges
        for state, trans in self.transition.items():
            for symbol, dest in trans.items():
                dot.edge(state, dest, label=symbol)

        dot.render(filename=filename, format='png', view=view)

@dataclass
class NFA:
    states: Set[str]
    alphabet: Set[str]  
    transition: Dict[str, Dict[str, str]]
    initial: str
    accepting: Set[str]

    def to_dfa(self, print_state=False): 
        initial_dfa_state = frozenset([self.initial])
        dfa_states = set()
        dfa_transition = {}
        dfa_accepting = set()
        queue = deque([initial_dfa_state])

        while queue:
            current = queue.popleft()
            if current not in dfa_states:
                if print_state:
                    print(f"Adding {{{', '.join(current)}}} to states...")

                dfa_states.add(current)
                dfa_state_name = ','.join(sorted(current))
                dfa_transition[dfa_state_name] = {}

                for symbol in self.alphabet:
                    next_states = set()
                    for nfa_state in current:
                        if symbol in self.transition.get(nfa_state, {}):
                            next_states.update(self.transition[nfa_state][symbol])
                    
                    if next_states:
                        next_state_frozen = frozenset(next_states)
                        next_state_name = ','.join(sorted(next_states))
                        dfa_transition[dfa_state_name][symbol] = next_state_name

                        if next_state_frozen not in dfa_states:
                            queue.append(next_state_frozen)
                
            
            if print_state:
                print(transition_table_str(
                    transition=dfa_transition,
                    alphabet=self.alphabet,
                    title='Table in Progress (order not preserved)'
                ), end='\n\n\n')

        # Determine DFA accepting states
        for state in dfa_states:
            if any(s in self.accepting for s in state):
                dfa_accepting.add(','.join(sorted(state)))

        return DFA(
            states={','.join(sorted(s)) for s in dfa_states},
            alphabet=self.alphabet,
            transition=dfa_transition,
            initial=','.join(sorted(initial_dfa_state)),
            accepting=dfa_accepting
        )

    def __str__(self) -> str:
        return transition_table_str(self.transition,
                                    self.alphabet,
                                    title="Transition Table")

    def to_graph(self, filename="nfa", view=True):
        dot = Digraph(comment="NFA")
        dot.attr(rankdir="LR")

        for state in self.states:
            if state in self.accepting:
                dot.node(state, shape='doublecircle')
            else:
                dot.node(state, shape='circle')

        # Start arrow
        dot.node('', shape='none')
        dot.edge('', self.initial)

        # Transition edges
        for state, trans in self.transition.items():
            for symbol, dests in trans.items():
                for dest in dests:
                    dot.edge(state, dest, label=symbol)

        dot.render(filename=filename, format='png', view=view)
