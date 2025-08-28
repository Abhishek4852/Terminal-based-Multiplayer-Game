#!/usr/bin/env python3
# client.py - Multiplayer Snake terminal client

import curses, socket, json, threading, queue, time, sys

SERVER_W, SERVER_H = 40, 20

def net_thread(host, port, in_q, out_q):
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.connect((host,port))
    s.settimeout(0.1)
    buf=b""
    try:
        while True:
            try:
                data = s.recv(4096)
                if not data: break
                buf += data
                while b"\n" in buf:
                    line, buf = buf.split(b"\n",1)
                    try: msg=json.loads(line.decode()); in_q.put(msg)
                    except: pass
            except socket.timeout: pass
            try:
                pkt=out_q.get_nowait()
                s.sendall((json.dumps(pkt)+"\n").encode())
            except queue.Empty: pass
    except: pass
    finally:
        in_q.put({"type":"disconnect"})
        s.close()

def map_coord(x,y,w,h):
    return int(x*(w-1)/(SERVER_W-1)), int(y*(h-1)/(SERVER_H-1))

def main(stdscr,host,port):
    curses.curs_set(0)
    stdscr.nodelay(True)
    in_q, out_q = queue.Queue(), queue.Queue()
    threading.Thread(target=net_thread,args=(host,port,in_q,out_q),daemon=True).start()
    state, pid = {}, None
    last_render=0
    while True:
        # handle net
        try:
            while True:
                msg=in_q.get_nowait()
                if msg.get("type")=="assign_id": pid=msg["id"]
                elif msg.get("type")=="state": state=msg
                elif msg.get("type")=="disconnect":
                    stdscr.addstr(0,0,"Disconnected. Press key.")
                    stdscr.nodelay(False); stdscr.getch(); return
        except queue.Empty: pass
        # input
        try: key=stdscr.getkey()
        except: key=None
        if key in ("KEY_UP","w","W"): out_q.put({"type":"input","dir":"UP"})
        elif key in ("KEY_DOWN","s","S"): out_q.put({"type":"input","dir":"DOWN"})
        elif key in ("KEY_LEFT","a","A"): out_q.put({"type":"input","dir":"LEFT"})
        elif key in ("KEY_RIGHT","d","D"): out_q.put({"type":"input","dir":"RIGHT"})
        elif key in ("q","Q"): return
        # render
        if time.time()-last_render>0.1:
            stdscr.erase(); h,w=stdscr.getmaxyx()
            # draw walls
            for (x,y) in state.get("walls",[]):
                sx,sy=map_coord(x,y,w,h)
                try: stdscr.addch(sy,sx,"#")
                except: pass
            # draw food
            for (x,y) in state.get("food",[]):
                sx,sy=map_coord(x,y,w,h)
                try: stdscr.addch(sy,sx,"*")
                except: pass
            # draw snakes
            for sid,s in state.get("snakes",{}).items():
                for i,(x,y) in enumerate(s["body"]):
                    sx,sy=map_coord(x,y,w,h)
                    ch="O" if i==0 else "o"
                    try: stdscr.addch(sy,sx,ch)
                    except: pass
                try: stdscr.addstr(0, 10+int(sid)*8, f"P{sid}:{s['score']}")
                except: pass
            try: stdscr.addstr(h-1,2,"WASD/Arrows to move, Q quit")
            except: pass
            stdscr.refresh(); last_render=time.time()
        time.sleep(0.01)

if __name__=="__main__":
    host=sys.argv[1] if len(sys.argv)>1 else "localhost"
    port=int(sys.argv[2]) if len(sys.argv)>2 else 9000
    curses.wrapper(main,host,port)
