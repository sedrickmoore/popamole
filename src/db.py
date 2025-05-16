import sqlite3
import re
import pygame

# Database setup
def init_db():
    """
    Connects to or creates the database and creates the 'scores' table if it doesn't exist.
    Returns the database connection object.
    """
    conn = sqlite3.connect("scores.db")
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS scores (
            nickname TEXT PRIMARY KEY,
            high_score INTEGER
        )
    ''')
    conn.commit()
    return conn

# Save player's new highest score
def save_score(conn, nickname, score):
    """
    Inserts a new score into the table for the player (identified by their nickname).
    If the nickname already exists, updates the score only if the new score is higher than the saved score.
    """
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO scores (nickname, high_score)
        VALUES (?, ?)
        ON CONFLICT(nickname) DO UPDATE SET high_score = 
        CASE WHEN excluded.high_score > scores.high_score THEN excluded.high_score ELSE scores.high_score END
    ''', (nickname, score))
    conn.commit()

# Retrieve the top player scores (default limit to 5)
def get_leaderboard(conn, limit=5):
    """
    Returns a list of tuples (nickname, high_score) sorted by the highest score.
    Limits results to a specified number (default is 5).
    """
    cur = conn.cursor()
    cur.execute('''
        SELECT nickname, MAX(high_score) as score
        FROM scores
        GROUP BY nickname
        ORDER BY score DESC
        LIMIT ?
    ''', (limit,))
    return cur.fetchall()

# Ask the player to enter a valid nickname using regex
def get_nickname(screen, font):
    """
    Asks the player to enter a nickname (3–12 characters).
    Accepts only letters, digits, and underscores using regex validation.
    Returns the nickname when Enter is pressed and input is valid.
    """
    nickname = ""
    input_active = True
    pattern = re.compile(r"^[A-Za-z0-9_]{3,12}$")

    while input_active:
        screen.fill("forestgreen")
        prompt = font.render("Enter your nickname:", True, (255, 255, 255))
        input_display = font.render(nickname, True, (0, 255, 0))
        screen.blit(prompt, (screen.get_width() // 2 - prompt.get_width() // 2, 200))
        screen.blit(input_display, (screen.get_width() // 2 - input_display.get_width() // 2, 300))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and pattern.fullmatch(nickname):
                    return nickname
                elif event.key == pygame.K_BACKSPACE:
                    nickname = nickname[:-1]
                elif len(nickname) < 12 and event.unicode.isprintable():
                    nickname += event.unicode
