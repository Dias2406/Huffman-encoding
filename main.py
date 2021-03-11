import os
from bitstring import BitArray
import pickle

encoding = {}
def frequency_dict (text) :
    """Creates a dictionary with frequencies of each character"""
    frequency = {}
    for ch in text :
        if ch in frequency:
            frequency[ch] += 1
        else:
            frequency[ch] = 1
    return frequency

def partition(list, first, last):
    small = (first-1)
    pivot = list[last]

    for i in range(first, last):
        if list[i] <= pivot:
            small = small+1
            list[small], list[i] = list[i], list[small]

    list[small+1], list[last] = list[last], list[small+1]
    return (small+1)

def quickSort(list, first, last):
    """Sorts the list"""
    if len(list) == 1:
        return list

    if first < last:
        index = partition(list, first, last)
        quickSort(list, first, index-1)
        quickSort(list, index+1, last)

def sort_frequency (dictionary):
    """Returns sorted list of frequencies and characters"""
    list = []
    for char in dictionary:
        list.append((dictionary[char],char))
    quickSort(list, 0, len(list)-1)
    return list

def create_tree(list) :
    """Returns the tree"""
    while len(list) > 1 :
        # takes first two elements with lowest frequencies
        small_freq = tuple(list[0:2])
        # sums up their frequencies
        sum_freq = small_freq[0][0] + small_freq[1][0]
        # creates tree with a combined frequency at the root and puts in the end of the list
        list = list[2:] + [(sum_freq,small_freq)]
        # sorts the list
        list = sorted(list, key=lambda elem: elem[0])
    return list[0]

def char_tree (tree) :
    """Returns a list of chars, without their frequencies"""
    chars = tree[1]
    if type(chars) == str:
        return chars
    else:
        return (char_tree(chars[0]), char_tree(chars[1]))

def create_codes (tree, code=''):
    """Creates dictionary with encoded characters"""
    global encoding
    if type(tree) == str:
        # saves encoded character into the dictionary
        encoding[tree] = code
    else:
        # assigns 0 to the left edge
        create_codes(tree[0], code+"0")
        # assigns 1 to the right edge
        create_codes(tree[1], code+"1")

def compress (path) :
    """Encodes and Compresses the text file"""
    global encoding
    filename, ext = os.path.splitext(path)
    output = filename + ".bin"
    output_tree = filename + "_tree" + ".pickle"
    output_decompress = filename + "_decompressed" + ".txt"

    with open(path, 'r') as f:
        text = f.read()

    # creates frequency dictionary
    frequency = frequency_dict(text)
    # inserts to the list and sorts
    list = sort_frequency(frequency)
    # creates tree
    tree = create_tree(list)
    # removes frequencies from the list
    tree = char_tree(tree)
    # encodes each character
    create_codes(tree)
    # encodes the text
    encoded_text = ""
    for ch in text:
        encoded_text += encoding[ch]

    print("Compressing...\n")

    # writes tree to the file
    with open(output_tree, 'wb') as f:
        pickle.dump(tree, f)
    # converts string to bits
    bits = BitArray(bin=encoded_text)
    # writes encoded text to the file
    with open(output, 'wb') as f:
        bits.tofile(f)

    original_file = os.path.getsize(path)
    compressed = os.path.getsize(filename + ".bin")
    print(f'{filename} was compressed' )
    print(f'Original file: {original_file} bytes')
    print(f'Compressed file: {compressed} bytes')
    proportion = str(round(((original_file-compressed)/original_file)*100))
    print("Compressed file to about: " + proportion + "% of original")

def decompress(path):
    """Decodes and Decompresses the text file"""
    filename, ext = os.path.splitext(path)
    output = filename + ".bin"
    output_tree = filename + "_tree" + ".pickle"
    output_decompress = filename + "_decompressed" + ".txt"

    with open(path, 'rb') as f:
        bits = BitArray(f.read())

    with open(output_tree, 'rb') as f:
         tree = pickle.load(f)

    decoded_text = ""
    char = tree
    # converts bits to string
    encoded_text = bits.bin
    # convers encoded text to decoded
    for bit in encoded_text :
        if bit == '0':
            # moves by the left edge
            char = char[0]
        else:
            # moves by the right edge
            char = char[1]
        if type(char) == str:
            # adds a character to the decoded_text
            decoded_text += char
            char = tree

    # writes decoded text to a file
    with open(output_decompress, 'w') as file:
        file.write(decoded_text)


    print("Decomressing...\n")
    print("Decompressed")

if __name__ == "__main__" :
    choice = int(input("To compress file type 1\nTo decompress press 2:\n"))
    if choice == 1:
        text = input("Input the file/path to be compressed(txt files only): ")
        try:
            compress(text)
        except FileNotFoundError:
            print("No such file or directory")
    elif choice == 2:
        text = input("Input the file/path to be decompressed(bin files only): ")
        try:
            decompress(text)
        except FileNotFoundError:
            print("No such file or directory")
    else:
        print("Invalid Input")
