# Application Features

1. Improve the Design: modern, sleek, easy on the eyes for children and adults.
   Done. Cool gray light theme, dim dark theme, and a Dark / Light control that is remembered on this device.
2. A "delayed image" mode: audio is played, image is "revealed". Allows user to test their comprehension.
   Done. "Listen first" plays the line once, then reveals the picture, then plays it again. "Picture stays" keeps the picture up.
3. Users start on Course level selection pages -> moves to Course Steps page based on level selected -> Whichever step they pick, that begins the interaction.
   Done. Levels 2 and 3, and lessons 2 and 3 of level 1, are selectable and empty.

## Underlying design

- Intuitive text based:
    - User provides transcript (never shows or is processed but is the scaffold)
    - User adds audio and images in separate folders: the name determines the order (or this could be transcripted? (this could also be a side-app: an editor that allows users to drop and place, then generate the database.

# Repo

- Set up security and testing workflows in this repo.
  Done. Dependabot alerts and security updates are on. CI runs the unit tests, typecheck, and a secret scan. Branch protection, required reviews, and GitHub secret scanning need GitHub Pro while this repository is private.
