import numpy as np
from midi_to_statematrix import noteStateMatrixToMidi



def main():
    input_array = np.load('predict.npy')
    print (input_array.shape)
    result = np.zeros((101,78,2))
    for j in range(101):
        i = 0
        while i < 156:
            if input_array[j,i] == 1:
                result[j,i/2,0] = 1
                if input_array[j,i+1] == 1:
                    result[j,i/2,1] = input_array[j,i+1]
            i = i + 2
    print (result)
    noteStateMatrixToMidi(result, name="ex6")


if __name__ == "__main__":
    main()