# LexiMind: Smart Vocabulary Manager

## 🧠 Overview

**LexiMind** is a powerful, user-centric flashcard application designed to optimize vocabulary acquisition and retention. Built with Python and the PyQt5 framework, it utilizes a sophisticated **Spaced Repetition System (SRS)** algorithm to determine the optimal time for reviewing each word, maximizing learning efficiency and memory consolidation.

The application features a modern, animated graphical user interface, making the learning process engaging and effective.

## ✨ Key Features

* **Intelligent Spaced Repetition (SRS):** Implements a robust SRS logic to manage review intervals, ensuring you study the right words at the right time to move them from short-term to long-term memory.
* **Animated Visuals:** Features a unique, dynamic background (similar to the "Matrix" effect) that provides a modern and engaging user experience.
* **Full CRUD Functionality:** Easily **C**reate, **R**ead, **U**pdate, and **D**elete vocabulary entries through a dedicated management interface.
* **Database Persistence:** Uses a lightweight SQLite database (`flash cards.db`) to store all user-added words, meanings, review statistics, and SRS intervals.
* **Review Modes:** Supports both manual and timed review modes for flexible study sessions.
* **Intuitive GUI:** Built with PyQt5 for a responsive and cross-platform desktop experience.

## 💻 Tech Stack

* **Core Language:** Python 3.x
* **GUI Framework:** PyQt5
* **Database:** SQLite 3
* **Key Modules:** `sqlite3`, `random`, `datetime`

## 🚀 Installation and Setup

### Prerequisites

You need Python 3.x installed on your system.

### Steps

1.  **Clone the Repository (or download files):**
    ```bash
    git clone [YOUR_REPOSITORY_URL]
    cd LexiMind
    ```
2.  **Install Dependencies:**
    The application primarily requires PyQt5.
    ```bash
    pip install PyQt5
    ```
3.  **Run the Application:**
    Execute the main script to start the application:
    ```bash
    python main.py
    ```

## 📚 Usage

### 1. Add New Words (Edit Menu)

Navigate to the "Edit" menu to add new vocabulary. You need to provide the word, its meaning, and an initial review count. The application automatically assigns an SRS code and schedules the first review date.

### 2. Review Session

In the "Review" section, the application retrieves words whose scheduled review date has passed or is due today, based on the SRS logic.

* **Flip Card:** Use the designated button or keyboard shortcut to flip the card and see the meaning.
* **Update SRS:** After viewing the meaning, select a feedback option (e.g., "Easy," "Hard") to update the word's review interval. The system adjusts the next review date to optimize long-term retention.

### 3. Management (Edit/Remove)

The Edit menu also allows you to view all records, search, modify existing entries, or permanently remove words from the database.

## 📂 Project Structure

| File Name | Role | Description |
| :--- | :--- | :--- |
| `main.py` | Main Entry Point | Initializes the application and manages the flow between different screens. |
| `review.py` | SRS Engine | Contains the core database logic for reviewing words and updating the Spaced Repetition statistics. |
| `edit.py` | Management Module | Handles all CRUD operations (Add, Edit, Remove) for the vocabulary stored in the database. |
| `background.py` | UI Component | Implements the custom `AnimatedBackground` class for the dynamic aesthetic. |
| `flash cards.db` | Database | The SQLite file used to store all persistent data. |

---

## ✍️ Contact

If you have any questions or suggestions, please feel free to contact the author:

* **Author:** [Parsa azhari]
* **Email:** [azhari.parsa@gmail.com]
* **LinkedIn/GitHub:** [https://www.linkedin.com/in/parsa-azhari-4689001a9]