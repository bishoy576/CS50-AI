import sys

from crossword import *
from collections import deque

class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for v in self.domains:
            self.domains[v] = set([d for d in self.domains[v] if len(d) == v.length])

    def revise(self, X, Y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
    #     function Revise(csp, X, Y):

    # revised = false
    # for x in X.domain:
    #     if no y in Y.domain satisfies constraint for (X,Y):
    #         delete x from X.domain
    #         revised = true
    # return revised

        revised = False
        overlaps = self.crossword.overlaps[X, Y]
        if not overlaps:
            return revised
        possible_x = self.domains[X].copy()
        for x in possible_x:
            viable_y = False
            for y in self.domains[Y]:
                i, j = overlaps
                if x[i] == y[j]:
                    viable_y = True
            if not viable_y:
                self.domains[X].remove(x)
                revised = True
        return revised
                




    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
    #     function AC-3(csp):

    # queue = all arcs in csp
    # while queue non-empty:
    #     (X, Y) = Dequeue(queue)
    #     if Revise(csp, X, Y):
    #         if size of X.domain == 0:
    #             return false
    #         for each Z in X.neighbors - {Y}:
    #             Enqueue(queue, (Z,X))
    # return true
        variables = list(self.crossword.variables)
        n = len(variables)
        if arcs is not None:
            queue = deque(arcs)
        else:
            queue = deque()
            for i in range(n):
                for j in range(i+1, n):
                    v1, v2 = variables[i], variables[j]
                    queue.append((v1, v2))
        while queue:
            X, Y = queue.popleft()
            if self.revise(X, Y):
                if len(self.domains[X]) == 0:
                    return False
                for Z in self.crossword.neighbors(X):
                    if Z != Y:
                        queue.append((Z, X))
        return True                



    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        return len(assignment) == len(self.crossword.variables)

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        assignment_pairs = list(assignment.items())
        n = len(assignment_pairs)
        if len(set(assignment.values())) < n:
            return False
        for  i in range(n):
            variable, value = assignment_pairs[i]
            if len(value) != variable.length:
                return False
            for j in range(i+1, n):
                variable2, value2 = assignment_pairs[j]
                if self.crossword.overlaps[variable, variable2] is not None:
                    x, y = self.crossword.overlaps[variable, variable2]
                    if value[x] != value2[y]:
                        return False
        return True
                    



    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        map_to_n = dict()
        for d in self.domains[var]:
            n = 0
            for neighbor in self.crossword.neighbors(var):
                if neighbor not in assignment:
                    i, j = self.crossword.overlaps[var, neighbor]
                    for d2 in self.domains[neighbor]:
                        if d[i] != d2[j]:
                            n += 1
            map_to_n[d] = n
        return sorted(list(self.domains[var]), key=lambda x : map_to_n[x])

                    



    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        # (mRV, -degree)
        unassigned_variables = [v for v in self.crossword.variables if v not in assignment]
        unassigned_variables.sort(key=lambda x : (len(self.domains[x]), -len(self.crossword.neighbors(x))))
        return unassigned_variables[0]


    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        
# if assignment complete:

#     return assignment

# var = Select-Unassigned-Var(assignment, csp)
# for value in Domain-Values(var, assignment, csp):

#     if value consistent with assignment:
#         add {var = value} to assignment
#         inferences = Inference(assignment, csp)
#         if inferences ≠ failure:
#             add inferences to assignment
#         result = Backtrack(assignment, csp)
#         if result ≠ failure:
#             return result
#         remove {var = value} and inferences from assignment
# return failure
        def Inference(assignment, X):
            exit_value = self.ac3(arcs=[(Y, X) for Y in self.crossword.neighbors(X)])
            inferences = dict()
            if not exit_value:
                return exit_value, inferences
            for v in self.domains:
                if v not in assignment and len(self.domains[v]) == 1:
                    inferences[v] = next(iter(self.domains[v]))
            return exit_value, inferences
        def my_backtrack(assignment):
            if self.assignment_complete(assignment):
                return True, assignment
            var = self.select_unassigned_variable(assignment)
            for value in self.order_domain_values(var, assignment):
                new_assignment = assignment.copy()
                new_assignment[var] = value
                if self.consistent(new_assignment):
                    assignment[var] = value
                    exit_val, inferences = Inference(assignment, var)
                    if exit_val:
                        assignment = {**assignment, **inferences}
                    success, result = my_backtrack(assignment)
                    if success:
                        return success, result
                    del assignment[var]
                    assignment = {k : v for k, v in assignment.items() if k not in inferences}
            return False, None
        is_success, answer = my_backtrack(assignment)
        return answer if is_success else None

            



def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
