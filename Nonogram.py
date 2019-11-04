import os, sys, copy

#line means line of marked cells in a row
#finds all acceptable configurations with 0's mapped to 1's, and 1's mapped to 0's, given how long the row/column is, lines of 1's there and sum of lengths of those lines
#it does it by putting the next line in all possible places(so that there's enough space for other lines), for every option it calls the functions with the cells it leaves for left lines and subtracts the length of the put line from the sum
#sum is actually not required, however it's an optimization so that it's not recalculated every time
def acceptable_options(cells_left, lines, current_sum):
    if current_sum == 0:
        return [[1]*(cells_left + 1)]

    results = []
    length = lines.pop()
    new_sum = current_sum - length

    for i in range(cells_left - length, new_sum + len(lines) - 1, -1):
        new_cells_left = i - 1
        arrays = acceptable_options(new_cells_left, lines[:], new_sum)
        inserted = (0 in arrays[0])
        for array in arrays:
            if inserted:
                array.append(1)
            array.extend([0]*length)
            array.extend([1]*(cells_left - len(array)))
        results.extend(arrays)

    return results

#returns all possible configurations for a row/column
#for example, if all_options(2) is called, it'd be [[0,0], [0,1], [1,0], [1,1]], not in this order though
def all_options(cells_left):
    if cells_left == 1:
        return [[0], [1]]

    extension = []
    arrays = all_options(cells_left - 1)
    for array in arrays: #in every configuration append 0, and also have a copy where 1's are appended instead of 0's
        copy = array[:]
        copy.append(1)
        array.append(0)
        extension.append(copy)
    arrays.extend(extension)

    return arrays



def main():
    arg = sys.argv[1]
    file = open(arg, "r")
    rows = int(file.readline()) #number of rows
    cols = int(file.readline()) # number of cols
    row_lines = []
    col_lines = []
    for row in range(rows):
        row_lines.append(list(map(int, file.readline().strip().split()))) #given information about rows

    for col in range(cols):
        col_lines.append(list(map(int, file.readline().strip().split()))) #given information about cols



    all_row_options = all_options(cols)
    all_col_options = all_options(rows)
    excluded_row_options = []

    for i in range(rows):
        row_options = copy.deepcopy(all_row_options)

        row = row_lines[i]
        current_sum = sum(row)

        if current_sum == 0: #if there're no marked cells the configuration is obvious
            for j in range(cols):
                excluded_row_options.append([str(-1 - i * cols - j)])
            continue
        elif current_sum == cols: #if all cells are marked the configuration is obvious
            for j in range(cols):
                excluded_row_options.append([str(1 + i * cols + j)])
            continue
        else:
            options = acceptable_options(cols, row, current_sum)

        for array in options:
            row_options.remove(array)


        for array in row_options:
            for j in range(cols):
                if array[j] == 0:
                    array[j] = str(-1 - i * cols - j)
                else:
                    array[j] = str(1 + i * cols + j)

        excluded_row_options.append(row_options)


    excluded_col_options = []

    for i in range(cols):
        col_options = copy.deepcopy(all_col_options)

        col = col_lines[i]
        current_sum = sum(col)

        if current_sum == 0: #if there're no marked cells the configuration is obvious
            for j in range(rows):
                excluded_col_options.append([str(-1 - j * cols - i)])
            continue
        elif current_sum == rows: #if all cells are marked the configuration is obvious
            for j in range(rows):
                excluded_col_options.append([str(1 + j * cols + i)])
            continue
        else:
            options = acceptable_options(rows, col, current_sum)

        for array in options:
            col_options.remove(array)

        for array in col_options:
            for j in range(rows):
                if array[j] == 0:
                    array[j] = str(-1 - j * cols - i)
                else:
                    array[j] = str(1 + j * cols + i)

        excluded_col_options.append(col_options)



    clauses = 0
    for array in excluded_row_options:
        clauses += len(array)

    for array in excluded_col_options:
        clauses += len(array)


    text = open("input", "w")
    text.write("p cnf " + str(rows * cols) + " " + str(clauses) + "\n")

    for arrays in excluded_row_options:
        if len(arrays) > 1:
            for array in arrays:
                text.write(" ".join(array) + " 0\n")
        else:
            text.write(arrays[0] + " 0\n")

    for arrays in excluded_col_options:
        if len(arrays) > 1:
            for array in arrays:
                text.write(" ".join(array) + " 0\n")
        else:
            text.write(arrays[0] + " 0\n")

    text.close()

    os.system("minisat input output")

    output = open("output", "r")
    if output.readline().strip() != "SAT":
        print("something is wrong")
        return 0

    result = list(map(int, output.readline().strip().split()))
    for row in range(rows):
        for col in range(cols):
            if result[row * cols + col] > 0:
                print("#", end = " ")
            else:
                print(".", end = " ")
        print()




if __name__ == '__main__':
    main()







