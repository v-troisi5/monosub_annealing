import random
import math
import string

ALPHABET = string.ascii_uppercase
ciphertext = "QCCQCCRFXBQFRKOWXDRZODQBXQCLQNDQUCXQVFDKYQVFRKOQUCXQBFQCDKQIROFKQVGFXQWQZXDQOWQFFXOFRJXQEECRVQFRKO"
ITERATIONS = 30

def load_tetragrams(filename):
    counts = {}
    total = 0

    with open(filename) as f:
        for line in f:
            key, count = line.split()
            count = int(count)

            counts[key] = count
            total += count

    table = {}

    for key in counts:
        table[key] = math.log10(counts[key] / total)

    floor = math.log10(0.01 / total)

    return table, floor

def make_fitness_function(table, floor):
    def fitness(text):
        score = 0
        table_get = table.get

        for i in range(len(text) - 3):
            score += table_get(text[i:i+4], floor)

        return score

    return fitness

def decrypt(ciphertext, key):
    mapping = {ALPHABET[i]: key[i] for i in range(26)}

    return ''.join(
        mapping.get(c, c)
        for c in ciphertext
    )

def random_key():
    letters = list(ALPHABET)
    random.shuffle(letters)
    return ''.join(letters)

def swap_mutation(key):
    key_list = list(key)
    i, j = random.sample(range(len(key_list)), 2)
    key_list[i], key_list[j] = key_list[j], key_list[i]
    return ''.join(key_list)

def simulated_annealing(ciphertext, initial_key, decrypt, fitness,
                        T_start=10.0, T_end=0.001, alpha=0.995, iterations_per_temp=200):

    current_key = initial_key
    current_plain = decrypt(ciphertext, current_key)
    current_score = fitness(current_plain)

    best_key = current_key
    best_score = current_score

    T = T_start

    while T > T_end:
        for _ in range(iterations_per_temp):
            candidate_key = swap_mutation(current_key)
            candidate_plain = decrypt(ciphertext, candidate_key)
            candidate_score = fitness(candidate_plain)

            delta = candidate_score - current_score

            if delta > 0 or random.random() < math.exp(delta / T):
                current_key = candidate_key
                current_score = candidate_score

                if current_score > best_score:
                    best_key = current_key
                    best_score = current_score
        T *= alpha

    return best_key, best_score

table, floor = load_tetragrams("english_quadgrams.txt")
fitness = make_fitness_function(table, floor)

for i in range(ITERATIONS):
    best_key, best_score = simulated_annealing(ciphertext, random_key(), decrypt, fitness)
    print(
        f"Iteration {i+1}:" +
        f"\nBest solution: {best_key}" +
        f"\nWith fitness: {best_score}" + 
        f"\nAnd plaintext: {decrypt(ciphertext, best_key)}\n"
    )
