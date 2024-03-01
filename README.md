# Puzzle yourself or an animation

I found a reddit post of a pygame project with states. 
As I wanted to learn state management in pygame I added some features to this game.

Original github repo: https://github.com/reddit-pygame/puzzle-challenge
and Reddit Challenge post: https://www.reddit.com/r/pygame/comments/3s9m2j/challenge_a_puzzling_world/

## Get it to work

 - `pip install pygame-ce`
 - `pip install pygame_gui`
 - `pip install pillow`

## Changes

 - Pieces are now rotated by random increments of 90 degrees when the puzzle is scrambled.
 - User can rotate pieces 90 degrees.
 - User is congratulated and can return to the menu at puzzle completion.
 - User can pick a file to puzzle, this can be a animated file(gif, webp), game wil loop it indefinitely.
 - User can pick camera to puzzle their own face.
 - I made some Gifs and put them in resources/temp/
 - Shape of puzzle pieces are streched in stead of the images.

## Controls

 - **Left-click** Grab/place pieces
 - **Right-click** Rotate held piece
 - **F** Toggle fullscreen
 - **ESC** Exit
