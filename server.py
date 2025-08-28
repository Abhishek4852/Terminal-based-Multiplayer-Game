#!/usr/bin/env python3
# server.py - Multiplayer Snake with walls (authoritative server)

import asyncio, json, random, time

WIDTH, HEIGHT = 40, 20
TICK = 0.2   # seconds per tick (5 FPS)

players = {}   # id -> snake state
clients = {}   # id -> writer
next_id = 1
food = []
walls = []

# directions as dx,dy
DIRS = {"UP": (0,-1), "DOWN": (0,1), "LEFT": (-1,0), "RIGHT": (1,0)}

async def send_msg(writer, msg):
    writer.write((json.dumps(msg) + "\n").encode())
    await writer.drain()

def random_empty_cell():
    while True:
        x, y = random.randint(1, WIDTH-2), random.randint(1, HEIGHT-2)
        if (x,y) in walls: continue
        occupied = [p for pl in players.values() for p in pl["body"]]
        if (x,y) not in occupied and (x,y) not in food:
            return (x,y)

async def handle_client(reader, writer):
    global next_id
    pid = str(next_id); next_id += 1
    start = random_empty_cell()
    players[pid] = {"id": pid, "body": [start], "dir": "RIGHT", "alive": True, "score": 0, "input": None}
    clients[pid] = writer
    await send_msg(writer, {"type":"assign_id", "id": pid})
    print(f"Player {pid} connected")

    try:
        while True:
            data = await reader.readline()
            if not data: break
            try:
                msg = json.loads(data.decode())
            except: continue
            if msg.get("type")=="input" and pid in players:
                players[pid]["input"] = msg.get("dir")
    except:
        pass
    finally:
        print(f"Player {pid} disconnected")
        players.pop(pid, None)
        clients.pop(pid, None)
        writer.close()
        await writer.wait_closed()

async def broadcast(packet):
    data = (json.dumps(packet)+"\n").encode()
    for w in list(clients.values()):
        try:
            w.write(data)
            await w.drain()
        except:
            pass

def init_walls():
    global walls
    walls = []
    for x in range(WIDTH):
        walls.append((x,0))
        walls.append((x,HEIGHT-1))
    for y in range(HEIGHT):
        walls.append((0,y))
        walls.append((WIDTH-1,y))

async def game_loop():
    global food
    init_walls()
    food = [random_empty_cell()]
    while True:
        await asyncio.sleep(TICK)
        # update snakes
        dead = []
        for pid, snake in list(players.items()):
            if not snake["alive"]: continue
            # update dir
            newdir = snake["input"]
            if newdir and newdir in DIRS:
                dx,dy = DIRS[newdir]
                cx,cy = DIRS[snake["dir"]]
                # prevent 180° turn
                if (dx,dy) != (-cx,-cy):
                    snake["dir"] = newdir
            dx, dy = DIRS[snake["dir"]]
            headx, heady = snake["body"][0]
            newhead = (headx+dx, heady+dy)
            # check collisions
            if newhead in walls: snake["alive"]=False; dead.append(pid); continue
            for other in players.values():
                if newhead in other["body"]:
                    snake["alive"]=False; dead.append(pid); break
            if not snake["alive"]: continue
            # food check
            if newhead in food:
                snake["body"].insert(0,newhead)
                snake["score"] += 1
                food.remove(newhead)
                food.append(random_empty_cell())
            else:
                snake["body"].insert(0,newhead)
                snake["body"].pop()
        packet = {"type":"state","snakes":players,"food":food,"walls":walls,"t":time.time()}
        await broadcast(packet)

async def main():
    server = await asyncio.start_server(handle_client,"0.0.0.0",9000)
    print("Server running on port 9000")
    asyncio.create_task(game_loop())
    async with server:
        await server.serve_forever()

if __name__=="__main__":
    asyncio.run(main())
