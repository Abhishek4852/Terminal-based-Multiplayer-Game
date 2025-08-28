# 🎮 Terminal-based Multiplayer Game (Networking)  

## 📌 Problem Statement  
Most multiplayer games need heavy graphics and powerful systems, which makes them harder to run on low-resource machines. This project solves that problem by creating a **real-time multiplayer game** that works completely in the terminal using simple **ASCII graphics** (text-based visuals).  

The goal is to make the game fun and engaging, just like old classics such as *Snake*, *Pong*, or simple turn-based games, but still **lightweight and easy to run**.  

---

## 🖥️ System Architecture  
The game follows a **client-server architecture**:  
- The **Server** manages the game state, player connections, and synchronization.  
- The **Clients** send player inputs and render the game using ASCII graphics.  

![System Architecture](https://github.com/user-attachments/assets/312efcab-6aee-47b8-8c5a-0a035534ecf8)  

---

## ⚙️ Tech Stack  
- **Programming Language:** 🐍 Python (for both server and client)  
- **Networking:** `socket` module (for client-server communication)  
- **Concurrency:** `threading` module (for handling multiple clients at the same time)  
- **Game Interface:** `curses` library (for ASCII-based terminal graphics)  
- **Data Exchange:** `JSON` (to encode and decode game state/messages)  
- **Operating System:** Works on Linux, macOS, and Windows (with terminal support)  

---

## ✨ Features  
- Multiplayer support over a network 🌐  
- Real-time communication ⚡  
- Lightweight terminal-based UI (ASCII graphics)  
- Cross-platform compatibility 🖥️  
- Smooth gameplay with low latency 🎯  

---

## 🚀 How to Run the Application  

### 1️⃣ Clone the Repository  
```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name

2️⃣ Start the Server

Run the server script to host the game:

3️⃣ Start the Client(s)

In a new terminal window, run the client script:

python client.py
