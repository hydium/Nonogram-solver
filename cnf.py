import sys, os

class Node:

    def __init__(self, char):

        self.left = None
        self.right = None
        self.char = char

    def push_left(self, node):
        self.left = node

    def push_right(self, node):
        self.right = node

    #pre-order tree traversal, and concatenating node chars during the traversal
    def print_tree(self):
        print(self.char, end =' ')
        if self.left:
            self.left.print_tree()
        if self.right:
            self.right.print_tree()

    #in-order tree traversal, putting  parentheses and concatenating node chars during the traversal
    def infix_print_tree(self, result):
        if self.char == "&":
            result.append("(")
            self.left.infix_print_tree(result)
            result.append(") ")
            result.append(self.char + ' ')
            result.append("(")
            self.right.infix_print_tree(result)
            result.append(") ")
        elif self.left and self.right:
            self.left.infix_print_tree(result)
            result.append(self.char + ' ')
            self.right.infix_print_tree(result)
        elif self.left:
            result.append("- ")
            self.left.infix_print_tree(result)
        else:
            result.append(self.char + " ")


operators = [">", "<", "+", "&", "|", "=", "-"]


#tells whether char is an operator
def operator(char):
    return char in operators

#constructs a tree from the reversed given string
def tree_construction(args):
    char = args.pop()
    node = Node(char)

    if char == "-":
        node.push_left(tree_construction(args))
    elif operator(char):
        node.push_left(tree_construction(args))
        node.push_right(tree_construction(args))

    return node


def implication_free(node):
    if not operator(node.char):
        return node
    elif node.char == ">":
        new_node = Node("|")
        new_node.push_left(Node("-"))
        new_node.left.push_left(implication_free(node.left))
        new_node.push_right(implication_free(node.right))
        return new_node
    elif node.char == "<":
        new_node = Node("|")
        new_node.push_left(Node("-"))
        new_node.left.push_left(implication_free(node.right))
        new_node.push_right(implication_free(node.left))
        return new_node
    elif node.char == "-":
        new_node = Node("-")
        new_node.push_left(implication_free(node.left))
        return new_node
    else:
        node.push_left(implication_free(node.left))
        node.push_right(implication_free(node.right))
        return node

def negation_free(node):
    if not operator(node.char):
        return node
    elif node.char == "-" and node.left.char == "-":
        return negation_free(node.left.left)
    elif node.char == "&":
        node.push_left(negation_free(node.left))
        node.push_right(negation_free(node.right))
        return node
    elif node.char == "|":
        node.push_left(negation_free(node.left))
        node.push_right(negation_free(node.right))
        return node
    elif node.char == "-" and node.left.char == "&":
        node.char = "|"
        node_left = Node("-")
        node_right = Node("-")
        node_left.push_left(node.left.left)
        node_right.push_left(node.left.right)
        node.push_left(node_left)
        node.push_right(node_right)
        return negation_free(node)
    elif node.char == "-" and node.left.char == "|":
        node.char = "&"
        node_left = Node("-")
        node_right = Node("-")
        node_left.push_left(node.left.left)
        node_right.push_left(node.left.right)
        node.push_left(node_left)
        node.push_right(node_right)
        return negation_free(node)
    else:
        return node

def cnf(node):
    if (node.char != "&" and node.char !="|") or node.char == "-":
        return node
    elif node.char == "&":
        node.push_left(cnf(node.left))
        node.push_right(cnf(node.right))
        return node
    else:
        return distr(cnf(node.left), cnf(node.right))



def distr(node1, node2):
    if node1.char == "&":
        new_node = Node("&")
        new_node.push_left(distr(node1.left, node2))
        new_node.push_right(distr(node1.right, node2))
        return new_node
    if node2.char == "&":
        new_node = Node("&")
        new_node.push_left(distr(node1, node2.left))
        new_node.push_right(distr(node1, node2.right))
        return new_node
    else:
        new_node = Node("|")
        new_node.push_left(node1)
        new_node.push_right(node2)
        return new_node



def main():
    args = sys.argv[1]
    args = args.replace(" ", "")
    args = list(args)
    args.reverse()

    root = Node(args.pop())

    if root.char == "-":
        root.push_left(tree_construction(args))
    elif operator(root.char):
        root.push_left(tree_construction(args))
        root.push_right(tree_construction(args))

    implication_free_root = implication_free(root)
    negation_free_root = negation_free(implication_free_root)
    cnf_root = cnf(negation_free_root)

    cnf_root.print_tree()
    print()


    print_result = []
    cnf_root.infix_print_tree(print_result)
    opened = False #determines whether the last char was "("
    closed = False #determines whether the last char was ") "

    for i in range(len(print_result)):
        if opened and print_result[i] == "(":
            print_result[i] = ""
        if print_result[i] == "(":
            opened = True

        elif print_result[i] != "" and print_result[i] != ") ":
            opened = False

        if closed and print_result[i] == ") ":
            print_result[i] = ""

        if print_result[i] == ") ":
            closed = True
            print_result[i-1] = print_result[i-1].strip()
        elif print_result[i] == "& ":
            closed = False

    print("".join(print_result))

    #this part is for deciding validity of the given formula
    negated_root = Node("-")
    negated_root.push_left(cnf_root)
    nf_negated_root = negation_free(negated_root)
    cnf_negated_root = cnf(nf_negated_root)

    result = []
    cnf_negated_root.infix_print_tree(result)
    opened = False
    closed = False
    clauses = []
    dictionary = [] #dictionary of literals, e.g if we mapped p to 1, then it'd be stored here
    count = 0 #number of literals

    for i in range(len(result)):
        if opened and result[i] == "(":
            result[i] = ""
        if result[i] == "(":
            opened = True
            clauses.append([])
        elif result[i] != "" and result[i] != ") ":
            opened = False

        if closed and result[i] == ") ":
            result[i] = ""

        if result[i] == ") ":
            closed = True

        if result[i] == "& ":
            closed = False

        if (not opened and not closed) and not operator(result[i].strip()):
            found = False
            for j in range(len(dictionary)):
                if dictionary[j][0] == result[i]:
                    if result[i-1] == "- ":
                        clauses[len(clauses) - 1].append(str(0 - dictionary[j][1]))
                    else:
                        clauses[len(clauses) - 1].append(str(dictionary[j][1]))
                    found = True
                    break

            if not found:
                count += 1
                dictionary.append((result[i], count))
                if len(clauses) == 0:
                    clauses.append(["1"])
                elif result[i - 1] == "- ":
                    clauses[len(clauses) - 1].append(str(0 - count))
                else:
                    clauses[len(clauses) - 1].append(str(count))


    text = open("input", "w")
    text.write("p cnf " + str(count) + " " + str(len(clauses)) + "\n")
    for i in range(len(clauses)):
        text.write(" ".join(clauses[i]) + " 0\n")
    text.close()


    os.system("minisat input output > result")

    output = open("output", "r")
    linelist = output.readlines()
    output.close()
    verdict = linelist[0]
    if verdict.strip() == "UNSAT":
        print("Valid")
    else:
        print("Not Valid")


if __name__ == '__main__':
    main()




















