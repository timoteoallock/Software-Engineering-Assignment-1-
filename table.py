import sys
from tokenizer import Tokenizer
from parser import Parser
from solver_final import Solver

def process_file(filename):
    try:
  
        with open(filename, 'r') as f:
            data = f.read()

        tokenizer = Tokenizer(data)

 
        parser = Parser(tokenizer)


        ast = parser.parse()

   
        solver = Solver(ast)
        solver.solve()

    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
    except Exception as e:
        print(f"Error during execution: {e}")


if __name__ == '__main__':
    process_file(sys.argv[1])
