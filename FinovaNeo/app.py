"""Finova - personal finance & investing app (Streamlit + SQLite)

    pip install streamlit pandas plotly
    streamlit run finova_app.py

Data is stored in finova.db next to this file. First run seeds demo data.
"""
import re
import sqlite3
from datetime import date

import pandas as pd
import plotly.express as px
import streamlit as st

DB = "finova.db"
PALETTE = ["#0F6B5C", "#B8892B", "#5B7C99", "#8A9A5B", "#B0675A", "#6C5B7B"]
CATS = ["Dining", "Transport", "Housing", "Entertainment", "Shopping", "Health", "Other"]

st.set_page_config(page_title="Finova", page_icon="💹", layout="wide")
st.markdown("""<style>
html,body,[class*="css"]{font-family:'Inter',system-ui,sans-serif}
[data-testid="stMetric"]{background:rgba(15,107,92,.07);border:1px solid rgba(15,107,92,.2);padding:14px 16px;border-radius:12px}
.hero{font-size:clamp(2.4rem,6vw,3.8rem);font-weight:700;letter-spacing:-.03em;line-height:1.05;margin:0}
.sub{opacity:.7;margin:0 0 .5rem}.stTabs [data-baseweb="tab"]{font-weight:600}
</style>""", unsafe_allow_html=True)


# ---------------------------------------------------------------- database
def run(sql, args=()):
    with sqlite3.connect(DB) as c:
        c.execute(sql, args)


def q(sql, args=()):
    with sqlite3.connect(DB) as c:
        return pd.read_sql_query(sql, c, params=args)


def kv(key, default=None):
    r = q("SELECT v FROM kv WHERE k=?", (key,))
    return r.v[0] if len(r) else default


def set_kv(key, val):
    run("INSERT OR REPLACE INTO kv VALUES (?,?)", (key, str(val)))


def seed():
    with sqlite3.connect(DB) as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS kv(k TEXT PRIMARY KEY, v TEXT);
        CREATE TABLE IF NOT EXISTS tx(id INTEGER PRIMARY KEY, d TEXT, name TEXT, cat TEXT, amount REAL);
        CREATE TABLE IF NOT EXISTS holdings(symbol TEXT, name TEXT, qty REAL, cost REAL, price REAL);
        CREATE TABLE IF NOT EXISTS watch(symbol TEXT, name TEXT, price REAL, chg REAL);
        CREATE TABLE IF NOT EXISTS budgets(cat TEXT PRIMARY KEY, lim REAL);
        CREATE TABLE IF NOT EXISTS goals(id INTEGER PRIMARY KEY, name TEXT, target REAL, saved REAL);
        CREATE TABLE IF NOT EXISTS debts(id INTEGER PRIMARY KEY, name TEXT, balance REAL, original REAL, rate REAL, minpay REAL);
        CREATE TABLE IF NOT EXISTS bills(id INTEGER PRIMARY KEY, name TEXT, amount REAL, due TEXT, paid INTEGER);
        CREATE TABLE IF NOT EXISTS nw(m TEXT PRIMARY KEY, v REAL);""")
        if c.execute("SELECT COUNT(*) FROM kv").fetchone()[0]:
            return
        today = date.today()
        inc = [9800, 9800, 10400, 9800, 11200, 10600]
        base = {"Dining": 1300, "Transport": 520, "Housing": 2800, "Entertainment": 480, "Shopping": 700, "Health": 150}
        for i in range(6):
            m = (today.month - 5 + i - 1) % 12 + 1
            y = today.year + ((today.month - 5 + i - 1) // 12)
            c.execute("INSERT INTO tx(d,name,cat,amount) VALUES (?,?,?,?)", (f"{y}-{m:02d}-01", "Salary", "Income", inc[i]))
            for k, (cat, b) in enumerate(base.items()):
                amt = round(b * (0.85 + 0.1 * ((i * 7 + k * 3) % 4)), 0)
                c.execute("INSERT INTO tx(d,name,cat,amount) VALUES (?,?,?,?)", (f"{y}-{m:02d}-{10 + k:02d}", f"{cat} spending", cat, -amt))
        c.executemany("INSERT INTO holdings VALUES (?,?,?,?,?)", [
            ("VOO", "S&P 500 ETF", 150, 410, 468), ("AAPL", "Apple", 120, 158, 231), ("MSFT", "Microsoft", 60, 350, 430),
            ("NVDA", "Nvidia", 400, 70, 118), ("VT", "Total World ETF", 300, 95, 118)])
        c.executemany("INSERT INTO watch VALUES (?,?,?,?)", [("QQQ", "Nasdaq-100 ETF", 512.4, 0.8), ("TSLA", "Tesla", 248.1, -1.6), ("BND", "Total Bond ETF", 72.9, 0.1)])
        c.executemany("INSERT INTO budgets VALUES (?,?)", [("Dining", 1500), ("Transport", 600), ("Housing", 2800), ("Entertainment", 500), ("Shopping", 800), ("Health", 250)])
        c.executemany("INSERT INTO goals(name,target,saved) VALUES (?,?,?)", [("Japan trip", 12000, 7400), ("New laptop", 6500, 2100), ("Down payment", 50000, 18500)])
        c.executemany("INSERT INTO debts(name,balance,original,rate,minpay) VALUES (?,?,?,?,?)", [("Mortgage", 310000, 360000, 4.2, 1900), ("Car loan", 38000, 60000, 3.1, 620), ("Credit card", 4200, 4200, 15.0, 150)])
        c.executemany("INSERT INTO bills(name,amount,due,paid) VALUES (?,?,?,?)", [("Electricity", 186, "18th", 0), ("Internet", 129, "20th", 1), ("Insurance", 420, "25th", 0), ("Card minimum", 150, "28th", 0)])
        for k, v in {"currency": "$", "property": 420000, "retirement": 96000, "other": 12000}.items():
            c.execute("INSERT INTO kv VALUES (?,?)", (k, str(v)))
        spent = c.execute("SELECT SUM(amount) FROM tx").fetchone()[0]
        c.execute("INSERT INTO kv VALUES ('opening_cash',?)", (str(48200 - spent),))


seed()
CUR = kv("currency", "$")
money = lambda x: f"{'-' if x < 0 else ''}{CUR}{abs(x):,.0f}"
clamp = lambda x: max(0.0, min(1.0, float(x)))


# ---------------------------------------------------------------- finance logic
def snapshot():
    h = q("SELECT * FROM holdings")
    tx = q("SELECT amount FROM tx").amount.sum()
    cash = float(kv("opening_cash")) + tx
    invested = (h.qty * h.price).sum()
    debts = q("SELECT balance FROM debts").balance.sum()
    other = float(kv("property")) + float(kv("retirement")) + float(kv("other"))
    return dict(cash=cash, invested=invested, debts=debts, assets=cash + invested + other,
                nw=cash + invested + other - debts, alloc={
                    "Cash": cash, "Stocks & ETFs": invested, "Property": float(kv("property")),
                    "Retirement": float(kv("retirement")), "Other": float(kv("other"))})


def monthly():
    t = q("SELECT substr(d,1,7) m, SUM(CASE WHEN amount>0 THEN amount END) income, "
          "-SUM(CASE WHEN amount<0 THEN amount END) expense FROM tx GROUP BY m ORDER BY m").fillna(0)
    return t.tail(6)


def health(s, m):
    last = m.iloc[-1]
    rate = (last.income - last.expense) / last.income if last.income else 0
    months = s["cash"] / max(m.expense.mean(), 1)
    dr = s["debts"] / s["assets"]
    h = q("SELECT qty*price v FROM holdings").v
    top = h.max() / h.sum() if h.sum() else 0
    parts = [("Savings rate", clamp(rate / .3), f"{rate:.0%}"), ("Emergency fund", clamp(months / 6), f"{months:.1f} months"),
             ("Debt load", clamp(1 - dr / .6), f"{dr:.0%} of assets"), ("Diversification", clamp(1 - (top - .2) / .6), f"top holding {top:.0%}")]
    return round(sum(p[1] for p in parts) * 25), parts, rate, months, top


def payoff(extra, method):
    d = q("SELECT balance b, rate r, minpay p FROM debts WHERE balance>0").to_dict("records")
    months = interest = 0
    while any(x["b"] > 0 for x in d) and months < 600:
        months += 1
        for x in d:
            i = x["b"] * x["r"] / 1200
            x["b"] += i
            interest += i
        pool = extra
        for x in d:
            pay = min(x["p"], x["b"])
            x["b"] -= pay
        live = [x for x in d if x["b"] > 0]
        live.sort(key=(lambda x: -x["r"]) if method == "Avalanche" else (lambda x: x["b"]))
        for x in live:
            pay = min(pool, x["b"])
            x["b"] -= pay
            pool -= pay
    return months, interest


def fire(start, monthly_add, ret, spend, age):
    target, bal, yrs = spend * 25, start, 0
    while bal < target and yrs < 80:
        bal = bal * (1 + ret / 100) + monthly_add * 12
        yrs += 1
    return target, yrs, age + yrs


def actions(s, m):
    score, parts, rate, months, top = health(s, m)
    out = []
    if months < 6:
        out.append(f"Build your emergency fund: {money(m.expense.mean() * 6 - s['cash'])} to reach 6 months of expenses.")
    d = q("SELECT * FROM debts WHERE rate>=10 AND balance>0")
    out += [f"Pay down {r['name']} first: {r['rate']}% APR costs more than most investments earn." for _, r in d.iterrows()]
    b = q("SELECT b.cat, b.lim, -COALESCE(SUM(t.amount),0) spent FROM budgets b LEFT JOIN tx t ON t.cat=b.cat AND substr(t.d,1,7)=? GROUP BY b.cat",
          (date.today().strftime("%Y-%m"),))
    out += [f"{r.cat} is {money(r.spent - r.lim)} over budget this month." for _, r in b[b.spent > b.lim].iterrows()]
    if top > .25:
        out.append(f"Your largest holding is {top:.0%} of your portfolio. Consider rebalancing into index funds.")
    if rate < .2:
        out.append(f"Savings rate is {rate:.0%}. Aim for 20% or more by trimming discretionary spending.")
    return out or ["You're on track. Keep contributing and review quarterly."]


def reply(text, s, m):
    score, parts, rate, months, top = health(s, m)
    t = text.lower()
    if re.search(r"score|health", t):
        return f"Your health score is **{score}/100**. Weakest area: **{min(parts, key=lambda p: p[1])[0]}**."
    if re.search(r"save|budget|spend|cut", t):
        return "Top actions:\n" + "\n".join(f"- {a}" for a in actions(s, m)[:3])
    if re.search(r"invest|risk|stock|portfolio", t):
        return f"Your largest holding is {top:.0%} of the portfolio. Above 25% in one stock raises volatility; broad ETFs reduce that."
    if re.search(r"debt|loan|owe", t):
        a, b = payoff(500, "Avalanche"), payoff(500, "Snowball")
        return f"With an extra {money(500)}/month, avalanche saves {money(b[1] - a[1])} in interest versus snowball."
    if re.search(r"emergency|fund", t):
        return f"You hold {months:.1f} months of expenses in cash. Target: 6."
    if re.search(r"fire|retire", t):
        return "Use the FIRE calculator on this page. Your target is 25x annual spending."
    return "Ask me about your health score, budget, investing risk, debt payoff, emergency fund, or FIRE."


# ---------------------------------------------------------------- sidebar
S = snapshot()
M = monthly()
run("INSERT OR REPLACE INTO nw VALUES (?,?)", (date.today().strftime("%Y-%m"), S["nw"]))
with st.sidebar:
    st.title("💹 Finova")
    cur = st.selectbox("Currency", ["$", "£", "€", "RM", "S$"], index=["$", "£", "€", "RM", "S$"].index(CUR))
    if cur != CUR:
        set_kv("currency", cur)
        st.rerun()
    st.download_button("Export transactions (CSV)", q("SELECT d date,name,cat category,amount FROM tx ORDER BY d DESC").to_csv(index=False), "transactions.csv")
    up = st.file_uploader("Import transactions (CSV)", type="csv", help="Columns: date, name, category, amount")
    if up and st.button("Import file"):
        f = pd.read_csv(up)
        f.columns = [c.lower() for c in f.columns]
        for _, r in f.iterrows():
            run("INSERT INTO tx(d,name,cat,amount) VALUES (?,?,?,?)", (str(r["date"])[:10], r["name"], r.get("category", "Other"), float(r["amount"])))
        st.rerun()
    if st.button("Reset demo data"):
        import os
        os.remove(DB)
        st.rerun()
    st.caption("Demo data. Not financial advice.")

tabs = st.tabs(["Overview", "Personal Finance", "Portfolio", "Intelligence"])

# ---------------------------------------------------------------- overview
with tabs[0]:
    hist = q("SELECT * FROM nw ORDER BY m")
    st.markdown(f"<p class='sub'>Net worth</p><p class='hero'>{money(S['nw'])}</p>", unsafe_allow_html=True)
    c = st.columns(4)
    delta = S["nw"] - hist.v.iloc[0] if len(hist) > 1 else 0
    c[0].metric("Total assets", money(S["assets"]))
    c[1].metric("Total liabilities", money(S["debts"]))
    c[2].metric("Net cash flow (this month)", money(M.iloc[-1].income - M.iloc[-1].expense))
    c[3].metric("Change since start", money(delta))
    l, r = st.columns([3, 2])
    with l:
        st.subheader("Income vs expenses")
        fig = px.bar(M.melt("m", var_name="type", value_name="amount"), x="m", y="amount", color="type", barmode="group", color_discrete_sequence=PALETTE)
        fig.update_layout(height=320, margin=dict(t=10, b=10), xaxis_title=None, yaxis_title=None)
        st.plotly_chart(fig, use_container_width=True)
    with r:
        st.subheader("Asset allocation")
        fig = px.pie(names=list(S["alloc"]), values=list(S["alloc"].values()), hole=.55, color_discrete_sequence=PALETTE)
        fig.update_layout(height=320, margin=dict(t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)
    if len(hist) > 1:
        st.subheader("Net worth trend")
        st.plotly_chart(px.area(hist, x="m", y="v", color_discrete_sequence=[PALETTE[0]]).update_layout(height=260, margin=dict(t=10), xaxis_title=None, yaxis_title=None), use_container_width=True)
    score, parts, *_ = health(S, M)
    st.subheader(f"Financial health score: {score}/100")
    for n, v, lbl in parts:
        st.progress(v, text=f"{n}: {lbl}")

# ---------------------------------------------------------------- personal finance
with tabs[1]:
    st.subheader("Add transaction")
    with st.form("tx", clear_on_submit=True):
        a, b, c2, d = st.columns([2, 2, 2, 2])
        name = a.text_input("Description")
        amt = b.number_input("Amount (negative = expense)", value=0.0, step=10.0)
        cat = c2.selectbox("Category", ["Income"] + CATS)
        dt = d.date_input("Date", date.today())
        if st.form_submit_button("Save transaction", type="primary"):
            if not name.strip() or amt == 0:
                st.error("Enter a description and a non-zero amount.")
            else:
                run("INSERT INTO tx(d,name,cat,amount) VALUES (?,?,?,?)", (dt.isoformat(), name.strip(), cat, amt))
                st.rerun()
    t = q("SELECT id, d date, name, cat category, amount FROM tx ORDER BY d DESC, id DESC LIMIT 200")
    f = st.multiselect("Filter by category", sorted(t.category.unique()))
    shown = t[t.category.isin(f)] if f else t
    st.dataframe(shown.drop(columns="id").head(15), hide_index=True, use_container_width=True)
    if len(t):
        del_id = st.selectbox("Delete a transaction", [None] + t.id.tolist()[:15], format_func=lambda i: "Select…" if i is None else f"{t[t.id == i].name.iloc[0]} ({money(t[t.id == i].amount.iloc[0])})")
        if del_id and st.button("Delete"):
            run("DELETE FROM tx WHERE id=?", (del_id,))
            st.rerun()

    st.subheader("Budgets (this month)")
    bd = q("SELECT b.cat, b.lim, -COALESCE(SUM(t.amount),0) spent FROM budgets b LEFT JOIN tx t ON t.cat=b.cat AND substr(t.d,1,7)=? GROUP BY b.cat", (date.today().strftime("%Y-%m"),))
    for _, r in bd.iterrows():
        st.progress(clamp(r.spent / r.lim), text=f"{r.cat}: {money(r.spent)} of {money(r.lim)}" + ("  ⚠ over budget" if r.spent > r.lim else ""))
    with st.expander("Edit budget limits"):
        e = st.data_editor(bd[["cat", "lim"]], hide_index=True, key="bud")
        if st.button("Save budgets"):
            for _, r in e.iterrows():
                run("UPDATE budgets SET lim=? WHERE cat=?", (r.lim, r.cat))
            st.rerun()

    g, dcol = st.columns(2)
    with g:
        st.subheader("Savings goals")
        for _, r in q("SELECT * FROM goals").iterrows():
            st.progress(clamp(r.saved / r.target), text=f"{r['name']}: {money(r.saved)} / {money(r.target)}")
            if st.button(f"Add {money(500)}", key=f"g{r.id}"):
                run("UPDATE goals SET saved=MIN(target, saved+500) WHERE id=?", (r.id,))
                st.rerun()
        with st.expander("New goal"):
            gn, gt = st.text_input("Goal name"), st.number_input("Target", min_value=100.0, value=5000.0)
            if st.button("Create goal") and gn:
                run("INSERT INTO goals(name,target,saved) VALUES (?,?,0)", (gn, gt))
                st.rerun()
    with dcol:
        st.subheader("Debt payoff planner")
        for _, r in q("SELECT * FROM debts").iterrows():
            st.progress(clamp(1 - r.balance / r.original), text=f"{r['name']} ({r.rate}% APR): {money(r.balance)} left")
        extra = st.slider("Extra monthly payment", 0, 3000, 500, 50)
        for meth in ("Avalanche", "Snowball"):
            mo, it = payoff(extra, meth)
            st.write(f"**{meth}:** debt-free in {mo // 12}y {mo % 12}m, interest {money(it)}")

    e1, e2 = st.columns(2)
    with e1:
        st.subheader("Emergency fund")
        mths = S["cash"] / max(M.expense.mean(), 1)
        st.metric("Months of expenses covered", f"{mths:.1f}")
        st.progress(clamp(mths / 6), text=f"Goal: 6 months ({money(M.expense.mean() * 6)})")
    with e2:
        st.subheader("Bills")
        for _, r in q("SELECT * FROM bills").iterrows():
            if st.checkbox(f"{r['name']}: {money(r.amount)}, due {r.due}", bool(r.paid), key=f"b{r.id}") != bool(r.paid):
                run("UPDATE bills SET paid=1-paid WHERE id=?", (r.id,))
                st.rerun()

# ---------------------------------------------------------------- portfolio
with tabs[2]:
    h = q("SELECT rowid id, * FROM holdings")
    h["value"], h["cost_basis"] = h.qty * h.price, h.qty * h.cost
    h["pnl"], h["pnl_pct"] = h.value - h.cost_basis, (h.price / h.cost - 1) * 100
    st.markdown(f"<p class='sub'>Portfolio value</p><p class='hero'>{money(h.value.sum())}</p>", unsafe_allow_html=True)
    pl = h.pnl.sum()
    st.write(f"Total P&L: :{'green' if pl >= 0 else 'red'}[{money(pl)} ({pl / h.cost_basis.sum():+.1%})]")
    st.dataframe(h[["symbol", "name", "qty", "cost", "price", "value", "pnl", "pnl_pct"]].style.format(
        {"value": "{:,.0f}", "pnl": "{:+,.0f}", "pnl_pct": "{:+.1f}%"}), hide_index=True, use_container_width=True)
    with st.expander("Edit holdings"):
        ed = st.data_editor(q("SELECT symbol,name,qty,cost,price FROM holdings"), num_rows="dynamic", hide_index=True, key="hold")
        if st.button("Save holdings"):
            ed = ed.dropna(subset=["symbol"])
            run("DELETE FROM holdings")
            for _, r in ed.iterrows():
                run("INSERT INTO holdings VALUES (?,?,?,?,?)", (r.symbol, r["name"], r.qty or 0, r.cost or 0, r.price or 0))
            st.rerun()
    p1, p2 = st.columns(2)
    with p1:
        st.subheader("Allocation")
        st.plotly_chart(px.pie(h, names="symbol", values="value", hole=.55, color_discrete_sequence=PALETTE).update_layout(height=300, margin=dict(t=10, b=10)), use_container_width=True)
    with p2:
        st.subheader("Analysis")
        w = h.value / h.value.sum()
        best, worst = h.loc[h.pnl_pct.idxmax()], h.loc[h.pnl_pct.idxmin()]
        st.metric("Best performer", best.symbol, f"{best.pnl_pct:+.1f}%")
        st.metric("Weakest performer", worst.symbol, f"{worst.pnl_pct:+.1f}%")
        hhi = (w ** 2).sum()
        st.metric("Concentration (HHI)", f"{hhi:.2f}", "diversified" if hhi < .2 else "concentrated", delta_color="normal" if hhi < .2 else "inverse")
    st.subheader("Watchlist")
    wl = st.data_editor(q("SELECT symbol,name,price,chg FROM watch"), num_rows="dynamic", hide_index=True, key="watch")
    if st.button("Save watchlist"):
        run("DELETE FROM watch")
        for _, r in wl.dropna(subset=["symbol"]).iterrows():
            run("INSERT INTO watch VALUES (?,?,?,?)", (r.symbol, r["name"], r.price or 0, r.chg or 0))
        st.rerun()

# ---------------------------------------------------------------- intelligence
with tabs[3]:
    cc, fc = st.columns(2)
    with cc:
        st.subheader("AI financial assistant")
        st.session_state.setdefault("chat", [("assistant", "Hi, I'm Finova. Ask about your score, budget, investing risk, debt or FIRE.")])
        box = st.container(height=340)
        if p := st.chat_input("Ask about your money…"):
            st.session_state.chat += [("user", p), ("assistant", reply(p, S, M))]
        for role, msg in st.session_state.chat:
            box.chat_message(role).markdown(msg)
    with fc:
        st.subheader("FIRE calculator")
        age = st.slider("Current age", 20, 60, 32)
        spend = st.slider("Annual spending", 20000, 200000, int(M.expense.mean() * 12), 5000)
        start = st.slider("Invested today", 0, 2000000, int(S["invested"] + float(kv("retirement"))), 10000)
        add = st.slider("Monthly contribution", 0, 20000, 3000, 500)
        ret = st.slider("Expected annual return (%)", 2.0, 12.0, 6.0, 0.5)
        target, yrs, fage = fire(start, add, ret, spend, age)
        st.metric("Projected FIRE age", "80+ years away" if yrs >= 80 else f"{fage}")
        st.caption(f"Target {money(target)} (25x annual spending), reached in about {yrs} years.")
    st.subheader("Your action plan")
    for i, a in enumerate(actions(S, M)):
        st.checkbox(a, key=f"act{i}")
    st.subheader("Finova Academy")
    ac = st.columns(4)
    for col, (title, pct) in zip(ac, [("Budgeting 101", 100), ("Index investing", 60), ("Debt strategies", 20), ("FIRE roadmap", 0)]):
        col.metric(title, f"{pct}%")
        col.progress(pct / 100)
