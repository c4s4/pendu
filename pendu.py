#!/usr/bin/env python
# encoding: UTF-8

import sys
import random

# fichier par défaut pour le dictionnaire
DEFAULT_DICT = 'dictionnaire.txt'
# encoding du dictionnaire
DICT_ENCODING = 'ISO-8859-1'
# caractère remplaçant les lettres non trouvées
HIDDEN = '-'
# nombre d'erreurs
MAX_ERRORS = 7
# taille minimale des mots
MIN_SIZE = 6
# ordre des lettres en français (source : Wikipedia)
LETTERS = ['e', 'a', 'i', 's', 'n', 'r', 't', 'o', 'l', 'u',
           'd', 'c', 'm', 'p', 'g', 'b', 'v', 'h', 'f', 'q',
           'y', 'x', 'j', 'k', 'w', 'z']


def load_dictionnary(filename):
    '''Charge le dictionnaire comme une liste de mots. Les mots sont ensuite :
    - Filtrés en enlevant ceux qui comportent des lettres accentuées.
    - Nettoyés d'éventuels espaces avant ou après.'''
    with open(filename, encoding='iso-8859-1') as stream:
        content = stream.read()
    letters = set(LETTERS)
    dictionnary = [word.strip()
                   for word in content.split('\n')
                   if word != '' and set(word).issubset(letters)
                   and ' ' not in word]
    return dictionnary


def choose_word(dictionnary):
    '''Choisit un mot aléatoirement dans le dictionnaire.'''
    word = ''
    while len(word) < MIN_SIZE:
        word = random.choice(dictionnary)
    return word


def discovered_letters(word, letters):
    '''Renvoie le mot avec les lettres trouvées affichées et celles qui ne le
    sont pas remplacées par des tirets.'''
    discovered = ''
    for letter in word:
        if letter in letters:
            discovered += letter
        else:
            discovered += HIDDEN
    return discovered


def list_words(dictionnary, letter, position):
    '''Renvoie la liste des mots pour lesquels la lettre donnée est à la bonne
    position.'''
    words = []
    for word in dictionnary:
        if word[position] == letter:
            words.append(word)
    return words


def letter_frequencies(dictionnary):
    '''Renvoie les fréquences des lettres dans les mots du dictionnaires sous
    la forme d'un dictionnaire associant le nombre d'apparitions à chaque
    lettre.'''
    frequencies = {}
    total = 0
    for word in dictionnary:
        for letter in word:
            total += 1
            if letter in frequencies:
                frequencies[letter] += 1
            else:
                frequencies[letter] = 1
    return frequencies


def ordered_letters(dictionnary, discovered):
    '''Renvoie le liste des lettres du dictionare ordonnées par fréquence
    d'apparition décroissante.'''
    # si le l'ordi a découvert au moins une lettre
    if discovered != [None]*len(discovered):
        frequencies = letter_frequencies(dictionnary)
        ordered_letters = []
        maximum = max(frequencies.values())
        minimum = min(frequencies.values())
        for freq in range(maximum, minimum-1, -1):
            for letter in frequencies:
                if frequencies[letter] == freq:
                    ordered_letters.append(letter)
        return ordered_letters
    else:
        # si l'ordi n'a trouvé aucune lettre, on renvoie une copie de LETTERS
        return LETTERS[:]


def ask_letter(letters):
    '''Demande une lettre au joueur et le renvoie.'''
    while True:
        letter = input("Lettre: ")
        if letter in letters:
            print("Lettre déjà proposée")
        elif letter not in LETTERS:
            print("Proposer uniquement des lettres minuscules non accentuées")
        else:
            return letter


def player(dictionnary):
    '''C'est le joueur qui doit deviner le mot. Renvoit 1 si le joueur
    gagne, 0 sinon.'''
    print("Le joueur doit deviner le mot choisi par l'ordinateur")
    word = choose_word(dictionnary)
    # les lettres proposées par le joueur (set cat non ordonnées et sans
    # doublon)
    letters = set([])
    errors = 0
    while errors < MAX_ERRORS:
        letter = ask_letter(letters)
        if letter in word:
            letters.add(letter)
            print(discovered_letters(word, letters))
            if set(word).issubset(letters):
                print("Gagné!")
                return 1
        else:
            errors += 1
            print("Raté, %i erreurs..." % errors)
    print("Perdu!")
    print("Le mot était '%s'" % word)
    return 0


def ask_size():
    '''Renvoit la taille du mot choisi par le joueur.'''
    while True:
        size = input("Taille du mot choisi: ")
        if not size.isdigit():
            print("%s n'est pas un entier positif " % size)
            continue
        elif int(size) < MIN_SIZE:
            print("Le mot doit faire au moins %i lettres" % MIN_SIZE)
        else:
            return int(size)


def filter_dictionnary(dictionnary, discovered, letters):
    size = len(discovered)
    filtered = [word for word in dictionnary if len(word) == size]
    position = 0
    for letter in discovered:
        if letter:
            filtered = list_words(filtered, letter, position)
        position += 1
    # enlever les mots qui contiennent des lettres qui ont été proposées
    # mais qui ne sont pas dans les lettres découvertes
    bad_letters = letters - set([l for l in discovered if l])
    return [word for word in filtered
            if not bad_letters.intersection(set(word))]


def guess_letter(letter, size):
    '''L'ordinateur propose une lettre et l'utilisateur doit entrer
    sa/ses positions dans le mot, séparées par des espaces. Renvoie la
    liste des positions.'''
    while True:
        positions = input("Positions de la lettre '%s': " % letter)
        positions = [positions for position in positions.strip().split(' ')
                     if position]
        error = False
        for position in positions:
            if not position.isdigit():
                print("Les positions doivent être des nombres entiers")
                error = True
                break
            if int(position) < 1 or int(position) > size:
                print("Les positions doivent être comprises entre 1 et %i" %
                      size)
                error = True
                break
        if not error:
            return [int(position)-1 for position in positions]


def ask_word():
    while True:
        word = input("Mot du joueur: ").strip()
        if not set(word).issubset(set(LETTERS)):
            print("Le mot doit être composé de lettres minuscules "
                  "sans accents")
        else:
            return word


def add_word_dictionnary(word):
    with open(DEFAULT_DICT, encoding=DICT_ENCODING) as stream:
        content = stream.read()
    content += word + "\n"
    with open(DEFAULT_DICT, 'w', encoding=DICT_ENCODING) as stream:
        content = stream.write(content)


def computer(dictionnary):
    '''C'est l'ordinateur qui doit deviner le mot du joueur. Renvoit
    1 si l'ordinateur trouve et 0 sinon.'''
    print("L'ordinateur doit deviner le mot auquel vous pensez")
    size = ask_size()
    discovered = [None for i in range(size)]
    letters = set([])
    errors = 0
    while errors < MAX_ERRORS:
        words = filter_dictionnary(dictionnary, discovered, letters)
        if len(words) == 0:
            print("Aucun mot du dictionnaire ne correspond, abandon")
            break
        ordered = ordered_letters(words, discovered)
        for letter in ordered:
            if letter not in letters:
                positions = guess_letter(letter, size)
                if not positions:
                    errors += 1
                for position in positions:
                    discovered[position] = letter
                letters.add(letter)
                break
        if None not in discovered:
            word = ''.join(discovered)
            print("L'ordinateur a découvert le mot '%s'" % word)
            return 1
        else:
            print("L'ordinateur a fait %s erreurs" % errors)
    print("L'ordinateur n'a pas trouvé")
    word = ask_word()
    add_word_dictionnary(word)
    dictionnary.append(word)
    print("Le mot %s a été ajouté au dictionnaire" % word)
    return 0


def ask_another(score_computer, score_player):
    print("Score de l'ordinateur %i" % score_computer)
    print("Score du joueur       %i" % score_player)
    return input("Une autre (o/n): ") in ('o', 'O')


def computer_first(dictionnary, score_computer, score_player):
    score_computer += computer(dictionnary)
    score_player += player(dictionnary)


def player_first(dictionnary, score_computer, score_player):
    score_player += player(dictionnary)
    score_computer += computer(dictionnary)


def main(filename):
    dictionnary = load_dictionnary(filename)
    score_computer = 0
    score_player = 0
    another = True
    sequence = random.choice([computer_first, player_first])
    while another:
        sequence(dictionnary, score_computer, score_player)
        another = ask_another(score_computer, score_player)


if __name__ == '__main__':
    main(DEFAULT_DICT)
