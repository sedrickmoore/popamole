# Pop-A-Mole

A fun arcade-style whack-a-mole shooter made with Python and Pygame!

Players move side to side, fire projectiles to hit moles, and try to get the highest score before time runs out.

---

## Controls

| Action       | Key(s)                  |
|--------------|--------------------------|
| Move Left    | A or Left Arrow          |
| Move Right   | D or Right Arrow         |
| Shoot        | E, Spacebar, or Up Arrow |
| Quit         | Escape                   |

---

## Features

- Projectile-based mole shooting
- Countdown timer and bonus time rewards
- High score tracking per player
- Nickname entry and validation
- Leaderboard display (Top 5 scores)
- Local SQLite database to save scores
- macOS `.app` build support with py2app

---

## Setup

### 1. Clone the repo

```
git clone https://github.com/sedrickmoore/pop-a-mole.git
cd pop-a-mole
```

### 2. Install dependencies
You’ll need Python 3 and pip. Then run:
```
pip install pygame
```

### 3. Run the game

```
python popamole.py
```

### (Optional) macOS Build
To build a standalone .app using py2app:
```
pip install py2app
python setup.py py2app
```
The app will be created in the dist/ folder.