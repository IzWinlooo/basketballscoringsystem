import customtkinter as ctk
import api_client


def open_live_stats(parent, home_id, away_id, game_label, my_team_id):

    win = ctk.CTkToplevel(parent)
    win.title("Live Stats")
    win.state("zoomed")
    win.transient(parent)
    win.grab_set()

    win.grid_rowconfigure(1, weight=1)
    win.grid_columnconfigure(0, weight=20)
    win.grid_columnconfigure(1, weight=45)
    win.grid_columnconfigure(2, weight=35)

    # ---------- top bar ----------
    top = ctk.CTkFrame(win)
    top.grid(row=0, column=0, columnspan=3, sticky="ew", padx=12, pady=(12, 8))
    top.grid_columnconfigure(1, weight=1)

    ctk.CTkLabel(top, text="Game:", font=ctk.CTkFont(size=14, weight="bold")).grid(
        row=0, column=0, padx=(12, 8), pady=10, sticky="w")
    ctk.CTkLabel(top, text=game_label, font=ctk.CTkFont(size=14)).grid(
        row=0, column=1, padx=(0, 12), pady=10, sticky="w")

    team_name_var = ctk.StringVar(value="Loading...")
    ctk.CTkLabel(top, textvariable=team_name_var,
                 font=ctk.CTkFont(size=16, weight="bold")).grid(
        row=0, column=2, padx=(0, 12), pady=10, sticky="e")

    score_var = ctk.StringVar(value="-- : --")
    ctk.CTkLabel(top, textvariable=score_var,
                 font=ctk.CTkFont(size=22, weight="bold")).grid(
        row=0, column=3, padx=(0, 20), pady=10, sticky="e")

    # ---------- left ----------
    left = ctk.CTkFrame(win)
    left.grid(row=1, column=0, sticky="nsew", padx=(12, 6), pady=(0, 12))
    left.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(left, text="LOG", font=ctk.CTkFont(size=16, weight="bold")).grid(
        row=0, column=0, padx=12, pady=(12, 6), sticky="w")
    log_box = ctk.CTkTextbox(left, height=140)
    log_box.grid(row=1, column=0, padx=12, pady=(0, 10), sticky="ew")
    log_box.configure(state="disabled")

    ctk.CTkLabel(left, text="Active Players (5)",
                 font=ctk.CTkFont(size=16, weight="bold")).grid(
        row=2, column=0, padx=12, pady=(6, 6), sticky="w")
    players_list = ctk.CTkScrollableFrame(left, height=320)
    players_list.grid(row=3, column=0, sticky="ew", padx=12, pady=(0, 10))
    players_list.grid_columnconfigure(0, weight=1)

    left_btns = ctk.CTkFrame(left)
    left_btns.grid(row=4, column=0, sticky="ew", padx=12, pady=(0, 12))
    left_btns.grid_columnconfigure(0, weight=1)

    sub_btn = ctk.CTkButton(left_btns, text="SUBSTITUTE", height=42)
    sub_btn.grid(row=0, column=0, sticky="ew", pady=(0, 8))
    undo_btn = ctk.CTkButton(left_btns, text="UNDO LAST ACTION", height=42)
    undo_btn.grid(row=1, column=0, sticky="ew", pady=(0, 8))
    finish_btn = ctk.CTkButton(left_btns, text="FINISH GAME", height=42)
    finish_btn.grid(row=2, column=0, sticky="ew")

    # ---------- middle ----------
    mid = ctk.CTkFrame(win)
    mid.grid(row=1, column=1, sticky="nsew", padx=(6, 6), pady=(0, 12))
    mid.grid_columnconfigure(0, weight=1)

    sel_info = ctk.StringVar(value="Select a player")
    ctk.CTkLabel(mid, textvariable=sel_info,
                 font=ctk.CTkFont(size=18, weight="bold")).grid(
        row=0, column=0, padx=12, pady=(12, 6), sticky="w")

    btns = ctk.CTkFrame(mid)
    btns.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
    btns.grid_columnconfigure(0, weight=1)
    btns.grid_columnconfigure(1, weight=1)

    # ---------- right ----------
    right = ctk.CTkFrame(win)
    right.grid(row=1, column=2, sticky="nsew", padx=(6, 12), pady=(0, 12))
    right.grid_rowconfigure(1, weight=1)
    right.grid_columnconfigure(0, weight=1)

    right_mode = ctk.StringVar(value="SELECTED")

    modebar = ctk.CTkFrame(right)
    modebar.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 6))
    modebar.grid_columnconfigure((0, 1, 2), weight=1)

    right_body = ctk.CTkScrollableFrame(right)
    right_body.grid(row=1, column=0, sticky="nsew", padx=4, pady=(0, 12))
    right_body.grid_columnconfigure(0, weight=1)

    # ---------- state ----------
    state = {
        "team_id": my_team_id,
        "team_name": "",
        "player_id": None,
        "player_name": "",
    }
    active_ids = {"ids": []}
    action_stack = []

    # ---------- helpers ----------
    def add_log(text):
        log_box.configure(state="normal")
        log_box.insert("end", text + "\n")
        log_box.see("end")
        log_box.configure(state="disabled")

    def pct(made, att):
        if att == 0:
            return ""
        return f"{(made/att)*100:.0f}%"

    # ---------- score refresh ----------
    def refresh_score():
        try:
            data = api_client.get_score(game_label)
            score_var.set(f"{data['home_score']}  :  {data['away_score']}")
        except:
            score_var.set("-- : --")
        win.after(5000, refresh_score)

    # ---------- right panel ----------
    def refresh_right_panel():
        for w in right_body.winfo_children():
            w.destroy()

        mode = right_mode.get()
        try:
            rows = api_client.get_stats(game_label, state["team_id"])
        except Exception as e:
            ctk.CTkLabel(right_body, text=f"Connection error:\n{e}",
                         text_color="#cc4444").pack(pady=20)
            return

        if mode == "SELECTED":
            if not state["player_id"]:
                ctk.CTkLabel(right_body, text="Select a player on the left.").pack(pady=20)
                return

            sel = next((r for r in rows if r["player_id"] == state["player_id"]), None)
            if sel is None:
                sel = {
                    "TwoPM": 0, "TwoPA": 0, "ThreePM": 0, "ThreePA": 0,
                    "FTM": 0, "FTA": 0, "REB": 0, "AST": 0,
                    "STL": 0, "BLK": 0, "TOV": 0, "PF": 0
                }

            two_m, two_a = sel["TwoPM"], sel["TwoPA"]
            th_m, th_a = sel["ThreePM"], sel["ThreePA"]
            ft_m, ft_a = sel["FTM"], sel["FTA"]
            fg_m = two_m + th_m
            fg_a = two_a + th_a
            pts = two_m*2 + th_m*3 + ft_m

            ctk.CTkLabel(right_body, text=state["player_name"],
                         font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(10, 10), anchor="w")
            for line in [
                f"FG:  {fg_m}/{fg_a}   {pct(fg_m, fg_a)}",
                f"2PT: {two_m}/{two_a}   {pct(two_m, two_a)}",
                f"3PT: {th_m}/{th_a}   {pct(th_m, th_a)}",
                f"FT:  {ft_m}/{ft_a}   {pct(ft_m, ft_a)}",
                f"REB: {sel['REB']}   AST: {sel['AST']}   STL: {sel['STL']}",
                f"BLK: {sel['BLK']}   TO: {sel['TOV']}   PF: {sel['PF']}",
                f"PTS: {pts}",
            ]:
                ctk.CTkLabel(right_body, text=line, font=ctk.CTkFont(size=16)).pack(anchor="w", pady=5)

        elif mode == "BOX":
            headers = ["Player", "#", "2PM", "2PA", "3PM", "3PA", "FTM", "FTA",
                       "REB", "AST", "STL", "BLK", "TO", "PF", "PTS"]
            col_weights = [3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]

            header_frame = ctk.CTkFrame(right_body, fg_color="#2b5f8e")
            header_frame.pack(fill="x", padx=4, pady=(8, 0))
            for col_i, (h, w) in enumerate(zip(headers, col_weights)):
                header_frame.grid_columnconfigure(col_i, weight=w)
                ctk.CTkLabel(header_frame, text=h,
                             font=ctk.CTkFont(size=11, weight="bold"),
                             text_color="white", width=10).grid(
                    row=0, column=col_i, padx=2, pady=4, sticky="ew")

            t2m=t2a=t3m=t3a=tftm=tfta=treb=tast=tstl=tblk=ttov=tpf=tpts = 0

            for idx, r in enumerate(rows):
                two_m, two_a = r["TwoPM"], r["TwoPA"]
                th_m, th_a   = r["ThreePM"], r["ThreePA"]
                ft_m, ft_a   = r["FTM"], r["FTA"]
                pts = two_m*2 + th_m*3 + ft_m
                t2m+=two_m; t2a+=two_a; t3m+=th_m; t3a+=th_a
                tftm+=ft_m; tfta+=ft_a; treb+=r["REB"]; tast+=r["AST"]
                tstl+=r["STL"]; tblk+=r["BLK"]; ttov+=r["TOV"]; tpf+=r["PF"]; tpts+=pts

                bg = "#1e1e2e" if idx % 2 == 0 else "#2a2a3e"
                if r["player_id"] in active_ids["ids"]:
                    bg = "#1a3a1a"

                row_frame = ctk.CTkFrame(right_body, fg_color=bg)
                row_frame.pack(fill="x", padx=4, pady=0)
                for col_i, w in enumerate(col_weights):
                    row_frame.grid_columnconfigure(col_i, weight=w)

                name = f"{r['last_name']}, {r['first_name']}"
                jersey = "" if r["jersey"] is None else str(r["jersey"])
                vals = [name, jersey, two_m, two_a, th_m, th_a,
                        ft_m, ft_a, r["REB"], r["AST"], r["STL"],
                        r["BLK"], r["TOV"], r["PF"], pts]
                for col_i, (v, w) in enumerate(zip(vals, col_weights)):
                    ctk.CTkLabel(row_frame, text=str(v),
                                 font=ctk.CTkFont(size=11), width=10).grid(
                        row=0, column=col_i, padx=2, pady=3, sticky="ew")

            totals_frame = ctk.CTkFrame(right_body, fg_color="#2b5f8e")
            totals_frame.pack(fill="x", padx=4, pady=(0, 8))
            for col_i, w in enumerate(col_weights):
                totals_frame.grid_columnconfigure(col_i, weight=w)
            totals = ["TEAM", "", t2m, t2a, t3m, t3a, tftm, tfta,
                      treb, tast, tstl, tblk, ttov, tpf, tpts]
            for col_i, (v, w) in enumerate(zip(totals, col_weights)):
                ctk.CTkLabel(totals_frame, text=str(v),
                             font=ctk.CTkFont(size=11, weight="bold"),
                             text_color="white", width=10).grid(
                    row=0, column=col_i, padx=2, pady=4, sticky="ew")

        else:  # SUMMARY
            t = {k: 0 for k in ["pts","reb","ast","stl","blk","tov","pf",
                                  "fg_m","fg_a","two_m","two_a","th_m","th_a","ft_m","ft_a"]}
            for r in rows:
                t["two_m"] += r["TwoPM"]; t["two_a"] += r["TwoPA"]
                t["th_m"] += r["ThreePM"]; t["th_a"] += r["ThreePA"]
                t["ft_m"] += r["FTM"]; t["ft_a"] += r["FTA"]
                t["fg_m"] += r["TwoPM"] + r["ThreePM"]
                t["fg_a"] += r["TwoPA"] + r["ThreePA"]
                t["pts"] += r["TwoPM"]*2 + r["ThreePM"]*3 + r["FTM"]
                t["reb"] += r["REB"]; t["ast"] += r["AST"]; t["stl"] += r["STL"]
                t["blk"] += r["BLK"]; t["tov"] += r["TOV"]; t["pf"] += r["PF"]

            ctk.CTkLabel(right_body, text="TEAM SUMMARY",
                         font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(10, 10), anchor="w")
            for line in [
                f"PTS: {t['pts']}",
                f"FG: {t['fg_m']}/{t['fg_a']}  {pct(t['fg_m'],t['fg_a'])}",
                f"2PT: {t['two_m']}/{t['two_a']}  {pct(t['two_m'],t['two_a'])}",
                f"3PT: {t['th_m']}/{t['th_a']}  {pct(t['th_m'],t['th_a'])}",
                f"FT: {t['ft_m']}/{t['ft_a']}  {pct(t['ft_m'],t['ft_a'])}",
                f"REB {t['reb']} | AST {t['ast']} | STL {t['stl']} | BLK {t['blk']}",
                f"TO {t['tov']} | PF {t['pf']}",
            ]:
                ctk.CTkLabel(right_body, text=line, font=ctk.CTkFont(size=16)).pack(anchor="w", pady=4)

    def set_mode(m):
        right_mode.set(m)
        refresh_right_panel()

    ctk.CTkButton(modebar, text="SELECTED", command=lambda: set_mode("SELECTED")).grid(
        row=0, column=0, padx=6, pady=6, sticky="ew")
    ctk.CTkButton(modebar, text="STAT SHEET", command=lambda: set_mode("BOX")).grid(
        row=0, column=1, padx=6, pady=6, sticky="ew")
    ctk.CTkButton(modebar, text="SUMMARY", command=lambda: set_mode("SUMMARY")).grid(
        row=0, column=2, padx=6, pady=6, sticky="ew")

    # ---------- players ----------
    def select_player(pid, display_name):
        state["player_id"] = pid
        state["player_name"] = display_name
        sel_info.set(f"Selected: {display_name}")
        add_log(f"PLAYER: {display_name}")
        refresh_right_panel()

    def refresh_players_list():
        for w in players_list.winfo_children():
            w.destroy()
        state["player_id"] = None
        state["player_name"] = ""
        sel_info.set("Select a player")

        try:
            all_players = api_client.get_players(state["team_id"])
        except Exception as e:
            ctk.CTkLabel(players_list, text=f"Error: {e}", text_color="#cc4444").grid(
                row=0, column=0, pady=8)
            return

        if not active_ids["ids"]:
            saved = api_client.get_active_players(game_label, state["team_id"])
            active_ids["ids"] = saved if saved else [p["id"] for p in all_players[:5]]

        active_players = [p for p in all_players if p["id"] in active_ids["ids"]]
        for r, p in enumerate(active_players):
            jersey = "" if p["jersey"] is None else str(p["jersey"])
            disp = f"{jersey}  {p['last_name']}, {p['first_name']}".strip()
            ctk.CTkButton(
                players_list, text=disp, height=42,
                command=lambda _pid=p["id"], _disp=disp: select_player(_pid, _disp)
            ).grid(row=r, column=0, sticky="ew", padx=6, pady=4)

        refresh_right_panel()

    # ---------- substitute ----------
    def open_sub_popup():
        try:
            all_players = api_client.get_players(state["team_id"])
        except Exception as e:
            add_log(f"Error: {e}")
            return

        bench = [p for p in all_players if p["id"] not in active_ids["ids"]]
        active = [p for p in all_players if p["id"] in active_ids["ids"]]

        pop = ctk.CTkToplevel(win)
        pop.title("Substitute")
        pop.geometry("560x640")
        pop.resizable(False, False)
        pop.transient(win)
        pop.grab_set()

        ctk.CTkLabel(pop, text="Substitute",
                     font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(14, 6))
        ctk.CTkLabel(pop, text="Pick 1 BENCH (IN) then 1 ACTIVE (OUT)").pack(pady=(0, 10))

        sel_in_text = ctk.StringVar(value="Selected IN: (none)")
        sel_out_text = ctk.StringVar(value="Selected OUT: (none)")
        chosen_in = {"pid": None, "name": ""}
        chosen_out = {"pid": None, "name": ""}

        indicator = ctk.CTkFrame(pop)
        indicator.pack(fill="x", padx=12, pady=(0, 10))
        indicator.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(indicator, textvariable=sel_in_text,
                     font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=0, column=0, sticky="w", padx=10, pady=(8, 2))
        ctk.CTkLabel(indicator, textvariable=sel_out_text,
                     font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=1, column=0, sticky="w", padx=10, pady=(2, 8))

        frames = ctk.CTkFrame(pop)
        frames.pack(fill="both", expand=True, padx=12, pady=8)
        frames.grid_columnconfigure(0, weight=1)
        frames.grid_columnconfigure(1, weight=1)
        frames.grid_rowconfigure(0, weight=1)

        bench_frame = ctk.CTkScrollableFrame(frames, label_text="BENCH (IN)")
        bench_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 6), pady=6)
        active_frame = ctk.CTkScrollableFrame(frames, label_text="ACTIVE (OUT)")
        active_frame.grid(row=0, column=1, sticky="nsew", padx=(6, 0), pady=6)

        def make_disp(p):
            jersey = "" if p["jersey"] is None else str(p["jersey"])
            return f"{jersey}  {p['last_name']}, {p['first_name']}".strip()

        for p in bench:
            disp = make_disp(p)
            ctk.CTkButton(bench_frame, text=disp,
                          command=lambda _pid=p["id"], _d=disp: (
                              chosen_in.update({"pid": _pid, "name": _d}),
                              sel_in_text.set(f"Selected IN: {_d}")
                          )).pack(fill="x", padx=6, pady=4)

        for p in active:
            disp = make_disp(p)
            ctk.CTkButton(active_frame, text=disp,
                          command=lambda _pid=p["id"], _d=disp: (
                              chosen_out.update({"pid": _pid, "name": _d}),
                              sel_out_text.set(f"Selected OUT: {_d}")
                          )).pack(fill="x", padx=6, pady=4)

        msg = ctk.StringVar(value="")
        ctk.CTkLabel(pop, textvariable=msg, text_color="#cc4444").pack(pady=(0, 8))

        def apply_sub():
            if chosen_in["pid"] is None or chosen_out["pid"] is None:
                msg.set("Please select BOTH: one BENCH (IN) and one ACTIVE (OUT).")
                return
            active_ids["ids"] = [
                chosen_in["pid"] if x == chosen_out["pid"] else x
                for x in active_ids["ids"]
            ]
            try:
                api_client.set_active_players(game_label, state["team_id"], active_ids["ids"])
            except Exception as e:
                add_log(f"Warning: could not save sub: {e}")
            add_log(f"SUB: IN {chosen_in['name']} | OUT {chosen_out['name']}")
            pop.destroy()
            refresh_players_list()

        ctk.CTkButton(pop, text="APPLY SUB", height=42, command=apply_sub).pack(pady=(0, 14))

    sub_btn.configure(command=open_sub_popup)

    # ---------- stat actions ----------
    def do_action(action_name, deltas):
        if not state["player_id"]:
            add_log("Select a player first.")
            return
        try:
            for col, amt in deltas:
                api_client.update_stat(
                    game_label, state["player_id"], state["team_id"], col, amt)
            action_stack.append({
                "player_id": state["player_id"],
                "player_name": state["player_name"],
                "team_id": state["team_id"],
                "deltas": deltas,
            })
            add_log(f"{action_name}: {state['player_name']}")
            refresh_right_panel()
        except Exception as e:
            add_log(f"Error: {e}")

    def undo_last():
        if not action_stack:
            add_log("UNDO: nothing to undo")
            return
        last = action_stack.pop()
        try:
            for col, amt in last["deltas"]:
                api_client.update_stat(
                    game_label, last["player_id"], last["team_id"], col, -amt)
            add_log(f"UNDO: {last['player_name']}")
            refresh_right_panel()
        except Exception as e:
            add_log(f"Undo error: {e}")

    undo_btn.configure(command=undo_last)
    finish_btn.configure(command=win.destroy)

    # stat buttons
    ctk.CTkButton(btns, text="2PT MADE (+2)", height=52,
                  command=lambda: do_action("2PT MADE", [("TwoPM", 1), ("TwoPA", 1)])).grid(
        row=0, column=0, padx=8, pady=8, sticky="ew")
    ctk.CTkButton(btns, text="2PT MISS", height=52,
                  command=lambda: do_action("2PT MISS", [("TwoPA", 1)])).grid(
        row=0, column=1, padx=8, pady=8, sticky="ew")
    ctk.CTkButton(btns, text="3PT MADE (+3)", height=52,
                  command=lambda: do_action("3PT MADE", [("ThreePM", 1), ("ThreePA", 1)])).grid(
        row=1, column=0, padx=8, pady=8, sticky="ew")
    ctk.CTkButton(btns, text="3PT MISS", height=52,
                  command=lambda: do_action("3PT MISS", [("ThreePA", 1)])).grid(
        row=1, column=1, padx=8, pady=8, sticky="ew")
    ctk.CTkButton(btns, text="FT MADE (+1)", height=52,
                  command=lambda: do_action("FT MADE", [("FTM", 1), ("FTA", 1)])).grid(
        row=2, column=0, padx=8, pady=8, sticky="ew")
    ctk.CTkButton(btns, text="FT MISS", height=52,
                  command=lambda: do_action("FT MISS", [("FTA", 1)])).grid(
        row=2, column=1, padx=8, pady=8, sticky="ew")
    ctk.CTkButton(btns, text="REB +1", height=46,
                  command=lambda: do_action("REB", [("REB", 1)])).grid(
        row=3, column=0, padx=8, pady=(14, 8), sticky="ew")
    ctk.CTkButton(btns, text="AST +1", height=46,
                  command=lambda: do_action("AST", [("AST", 1)])).grid(
        row=3, column=1, padx=8, pady=(14, 8), sticky="ew")
    ctk.CTkButton(btns, text="STL +1", height=46,
                  command=lambda: do_action("STL", [("STL", 1)])).grid(
        row=4, column=0, padx=8, pady=8, sticky="ew")
    ctk.CTkButton(btns, text="BLK +1", height=46,
                  command=lambda: do_action("BLK", [("BLK", 1)])).grid(
        row=4, column=1, padx=8, pady=8, sticky="ew")
    ctk.CTkButton(btns, text="TO +1", height=46,
                  command=lambda: do_action("TO", [("TOV", 1)])).grid(
        row=5, column=0, padx=8, pady=8, sticky="ew")
    ctk.CTkButton(btns, text="FOUL +1", height=46,
                  command=lambda: do_action("FOUL", [("PF", 1)])).grid(
        row=5, column=1, padx=8, pady=8, sticky="ew")

    # ---------- init ----------
    def init():
        try:
            teams = api_client.get_teams()
            team = next((t for t in teams if t["id"] == my_team_id), None)
            if team:
                state["team_name"] = team["team_name"]
                team_name_var.set(f"Team: {team['team_name']}")
            add_log(f"GAME: {game_label}")
            add_log(f"Controlling: {state['team_name']}")
        except Exception as e:
            add_log(f"Server error: {e}")
        refresh_players_list()
        refresh_score()

    win.protocol("WM_DELETE_WINDOW", win.destroy)
    win.after(100, init)
