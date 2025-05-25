import pygame
secret_word = "PyGame"
lives = 10

while lives > 0:  # Burada iki nokta (:) eklendi
    guess = input("Guess the secret word: ")
    
    if guess in secret_word:
        print("YOU'RE THE WINNER")
        break
    else:
        print("Incorrect guess.")
        lives -= 1
        print(f"Lives remaining: {lives}")
        
        if lives == 0:
            print("YOU'RE DEAD")
