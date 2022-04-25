# from concurrent.futures import ThreadPoolExecutor
# from time import sleep

# def count_number_of_words(sentence):
#   number_of_words = len(sentence.split())
#   sleep(1)
#   print("Number of words in the sentence :",sentence," : {}".format(number_of_words),end="\n")

# def count_number_of_characters(sentence):
#   number_of_characters = len(sentence)
#   sleep(1)
#   print("Number of characters in the sentence :",sentence," : {}".format(number_of_characters),end="\n")
  
# if __name__ == '__main__':
#   sentence = "Python Multiprocessing is an important library for achieving parallel programming."  
#   executor = ThreadPoolExecutor(4)
#   thread1 = executor.submit(count_number_of_words, (sentence))
#   thread2 = executor.submit(count_number_of_characters, (sentence))
#   print("Thread 1 executed ? :",thread1.done())
#   print("Thread 2 executed ? :",thread2.done())
#   sleep(2)
#   print("Thread 1 executed ? :",thread1.done())
#   print("Thread 2 executed ? :",thread2.done())


from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
import numpy as np
from time import sleep

def log(n):
    log_value = np.log(n)
    sleep(1)
    return log_value

if __name__ == '__main__':
    values = [1,10,100,1000]
    with ThreadPoolExecutor(max_workers = 3) as executor:
        thread1 = executor.map(log, values)
    for result in thread1:
        print(np.round(result,2))
