import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
from datetime import date, datetime

# ============================================================
# FINOVA NEO
# PERSONAL FINANCE OPERATING SYSTEM
# ============================================================

st.set_page_config(
    page_title="Finova Neo",
    page_icon="◉",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CSS
# ============================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: Inter, sans-serif;
}

.stApp {
    background: #f6f7f9;
}

.block-container {
    max-width: 1500px;
    padding-top: 1.3rem;
    padding-bottom: 4rem;
}

/* SIDEBAR */

section[data-testid="stSidebar"] {
    background: #ffffff;
    border-right: 1px solid #e6e8ed;
}

.finova-logo {
    font-size: 28px;
    font-weight: 800;
    letter-spacing: -1.5px;
    color: #111318;
}

.finova-sublogo {
    font-size: 10px;
    color: #969ca7;
    letter-spacing: 2px;
    margin-top: -2px;
    margin-bottom: 28px;
}

/* PAGE */

.page-title {
    font-size: 34px;
    font-weight: 800;
    letter-spacing: -1.5px;
    color: #111318;
}

.page-subtitle {
    color: #858b96;
    font-size: 14px;
    margin-bottom: 28px;
}

/* CARD */

.card {
    background: white;
    border: 1px solid #e7e9ee;
    border-radius: 18px;
    padding: 22px;
    margin-bottom: 16px;
}

.card-title {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: .8px;
    color: #8a909a;
}

.card-value {
    font-size: 28px;
    font-weight: 800;
    color: #111318;
    margin-top: 6px;
    letter-spacing: -1px;
}

.card-small {
    color: #8a909a;
    font-size: 12px;
    margin-top: 5px;
}

.green {
    color: #139447 !important;
}

.red {
    color: #d83d4b !important;
}

.blue {
    color: #3267e3 !important;
}

.orange {
    color: #e58a19 !important;
}

/* HERO */

.hero {
    background: #111318;
    border-radius: 24px;
    padding: 32px;
    color: white;
    margin-bottom: 20px;
}

.hero-label {
    color: #9ca3af;
    font-size: 13px;
}

.hero-value {
    font-size: 48px;
    font-weight: 800;
    letter-spacing: -2.5px;
    margin-top: 4px;
}

.hero-change {
    font-size: 14px;
    margin-top: 5px;
}

/* SECTION */

.section-title {
    font-size: 20px;
    font-weight: 800;
    color: #16181d;
    margin-top: 30px;
    margin-bottom: 15px;
}

/* AI */

.ai-card {
    background: linear-gradient(
        135deg,
        #111318 0%,
        #242934 100%
    );
    color: white;
    border-radius: 23px;
    padding: 30px;
    margin-bottom: 20px;
}

.ai-title {
    font-size: 23px;
    font-weight: 800;
}

.ai-description {
    color: #aeb4be;
    font-size: 13px;
    line-height: 1.6;
}

.ai-score {
    font-size: 62px;
    font-weight: 800;
    letter-spacing: -3px;
}

/* GOAL */

.goal-card {
    background: white;
    border: 1px solid #e6e8ed;
    border-radius: 17px;
    padding: 18px;
    margin-bottom: 10px;
}

.goal-title {
    font-weight: 750;
    font-size: 15px;
}

.goal-text {
    color: #858b95;
    font-size: 12px;
    margin-top: 4px;
}

/* LESSON */

.lesson {
    background: white;
    border: 1px solid #e6e8ed;
    border-radius: 18px;
    padding: 22px;
    min-height: 175px;
    margin-bottom: 15px;
}

.lesson-number {
    color: #3267e3;
    font-size: 11px;
    font-weight: 800;
}

.lesson-title {
    font-size: 18px;
    font-weight: 750;
    margin-top: 9px;
}

.lesson-description {
    color: #7d838e;
    font-size: 12px;
    line-height: 1.5;
    margin-top: 8px;
}

/* STOCK */

.stock-header {
    background: white;
    border: 1px solid #e6e8ed;
    border-radius: 20px;
    padding: 24px;
    margin-bottom: 18px;
}

.stock-symbol {
    font-size: 30px;
    font-weight: 800;
}

.stock-price {
    font-size: 38px;
    font-weight: 800;
}

/* FOOTER */

.footer {
    text-align: center;
    color: #9aa0aa;
    font-size: 11px;
    padding: 35px;
}

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# SESSION STATE
# ============================================================

if "transactions" not in st.session_state:
    st.session_state.transactions = [
        {
            "date": "2026-10-01",
            "type": "Income",
            "category": "Salary",
            "description": "Monthly salary",
            "amount": 3800.0
        },
        {
            "date": "2026-10-02",
            "type": "Expense",
            "category": "Food",
            "description": "Lunch",
            "amount": 12.0
        },
        {
            "date": "2026-10-02",
            "type": "Expense",
            "category": "Transport",
            "description": "Transport",
            "amount": 5.0
        },
        {
            "date": "2026-10-03",
            "type": "Expense",
            "category": "Housing",
            "description": "Rent",
            "amount": 750.0
        },
        {
            "date": "2026-10-04",
            "type": "Expense",
            "category": "Food",
            "description": "Dinner",
            "amount": 15.0
        }
    ]

if "portfolio" not in st.session_state:
    st.session_state.portfolio = [
        {
            "ticker": "VOO",
            "shares": 10.0,
            "avg_cost": 500.0
        },
        {
            "ticker": "NVDA",
            "shares": 5.0,
            "avg_cost": 150.0
        },
        {
            "ticker": "GOOGL",
            "shares": 3.0,
            "avg_cost": 180.0
        }
    ]

if "watchlist" not in st.session_state:
    st.session_state.watchlist = [
        "NVDA",
        "GOOGL",
        "AMZN",
        "VOO",
        "QQQM"
    ]

if "goals" not in st.session_state:
    st.session_state.goals = [
        {
            "name": "Emergency Fund",
            "current": 2400,
            "target": 5000
        },
        {
            "name": "First RM50,000",
            "current": 23000,
            "target": 50000
        },
        {
            "name": "Investment Capital",
            "current": 10000,
            "target": 20000
        }
    ]


# ============================================================
# DATA FUNCTIONS
# ============================================================

@st.cache_data(ttl=300)
def get_quote(ticker):

    try:

        stock = yf.Ticker(ticker)
        info = stock.fast_info

        price = float(
            info.get("last_price", 0)
        )

        previous = float(
            info.get("previous_close", price)
        )

        change = price - previous

        change_pct = (
            change / previous * 100
            if previous != 0
            else 0
        )

        return {
            "price": price,
            "previous": previous,
            "change": change,
            "change_pct": change_pct
        }

    except Exception:

        return {
            "price": 0,
            "previous": 0,
            "change": 0,
            "change_pct": 0
        }


@st.cache_data(ttl=600)
def get_history(ticker, period="1y"):

    try:

        data = yf.download(
            ticker,
            period=period,
            auto_adjust=True,
            progress=False
        )

        if data.empty:
            return pd.DataFrame()

        if isinstance(
            data.columns,
            pd.MultiIndex
        ):
            data.columns = (
                data.columns
                .get_level_values(0)
            )

        return data

    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=1800)
def get_stock_info(ticker):

    try:

        return yf.Ticker(ticker).info

    except Exception:

        return {}


# ============================================================
# FINANCIAL CALCULATIONS
# ============================================================

def get_transaction_df():

    return pd.DataFrame(
        st.session_state.transactions
    )


def cash_flow():

    df = get_transaction_df()

    if df.empty:
        return 0, 0, 0

    income = df.loc[
        df["type"] == "Income",
        "amount"
    ].sum()

    expenses = df.loc[
        df["type"] == "Expense",
        "amount"
    ].sum()

    net = income - expenses

    return income, expenses, net


def get_portfolio_df():

    rows = []

    for position in st.session_state.portfolio:

        ticker = position["ticker"]

        quote = get_quote(ticker)

        price = quote["price"]

        shares = position["shares"]

        avg_cost = position["avg_cost"]

        market_value = price * shares

        cost_basis = avg_cost * shares

        pnl = market_value - cost_basis

        pnl_pct = (
            pnl / cost_basis * 100
            if cost_basis
            else 0
        )

        rows.append(
            {
                "Ticker": ticker,
                "Shares": shares,
                "Avg Cost": avg_cost,
                "Price": price,
                "Market Value": market_value,
                "P/L": pnl,
                "P/L %": pnl_pct
            }
        )

    return pd.DataFrame(rows)


def portfolio_summary():

    df = get_portfolio_df()

    if df.empty:

        return 0, 0, 0, 0

    value = df["Market Value"].sum()

    cost = df["Avg Cost"].mul(
        df["Shares"]
    ).sum()

    pnl = value - cost

    pnl_pct = (
        pnl / cost * 100
        if cost
        else 0
    )

    return value, cost, pnl, pnl_pct


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div class="finova-logo">
            finova
        </div>

        <div class="finova-sublogo">
            PERSONAL FINANCE OS
        </div>
        """,
        unsafe_allow_html=True
    )

    st.caption("MAIN")

    page = st.radio(
        "Main",
        [
            "Overview",
            "Cash Flow",
            "Transactions"
        ],
        label_visibility="collapsed"
    )

    st.caption("INVEST")

    page2 = st.radio(
        "Invest",
        [
            "Portfolio",
            "Markets",
            "Stock Search",
            "Watchlist"
        ],
        label_visibility="collapsed"
    )

    st.caption("PLAN")

    page3 = st.radio(
        "Plan",
        [
            "Budgets",
            "Goals",
            "FIRE"
        ],
        label_visibility="collapsed"
    )

    st.caption("LEARN")

    page4 = st.radio(
        "Learn",
        [
            "Finova Academy",
            "Global Finance"
        ],
        label_visibility="collapsed"
    )

    st.caption("AI")

    page5 = st.radio(
        "AI",
        [
            "Finova AI",
            "Financial Health",
            "Action Center"
        ],
        label_visibility="collapsed"
    )

    if page != "Overview":
        selected_page = page
    elif page2 != "Portfolio":
        selected_page = page2
    elif page3 != "Budgets":
        selected_page = page3
    elif page4 != "Finova Academy":
        selected_page = page4
    elif page5 != "Finova AI":
        selected_page = page5
    else:
        selected_page = "Overview"


# ============================================================
# OVERVIEW
# ============================================================

if selected_page == "Overview":

    st.markdown(
        '<div class="page-title">Overview</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="page-subtitle">'
        'Your financial life, in one place.'
        '</div>',
        unsafe_allow_html=True
    )

    value, cost, pnl, pnl_pct = portfolio_summary()

    income, expenses, net = cash_flow()

    savings_rate = (
        net / income * 100
        if income
        else 0
    )

    st.markdown(
        f"""
        <div class="hero">

            <div class="hero-label">
                TOTAL INVESTMENT PORTFOLIO
            </div>

            <div class="hero-value">
                RM {value:,.2f}
            </div>

            <div class="hero-change">
                <span style="color:#57db8b;">
                    {"+" if pnl >= 0 else ""}
                    RM {pnl:,.2f}
                    ({pnl_pct:.2f}%)
                </span>
                &nbsp; all time
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    c1, c2, c3, c4 = st.columns(4)

    cards = [
        (
            "NET CASH FLOW",
            f"RM {net:,.0f}",
            "This month",
            "green"
        ),
        (
            "INCOME",
            f"RM {income:,.0f}",
            "This month",
            ""
        ),
        (
            "SPENDING",
            f"RM {expenses:,.0f}",
            "This month",
            ""
        ),
        (
            "SAVINGS RATE",
            f"{savings_rate:.1f}%",
            "Income retained",
            "blue"
        )
    ]

    for col, card in zip(
        [c1, c2, c3, c4],
        cards
    ):

        title, value_text, small, color = card

        with col:

            st.markdown(
                f"""
                <div class="card">

                    <div class="card-title">
                        {title}
                    </div>

                    <div class="card-value {color}">
                        {value_text}
                    </div>

                    <div class="card-small">
                        {small}
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )

    # MARKET

    st.markdown(
        '<div class="section-title">Markets</div>',
        unsafe_allow_html=True
    )

    markets = [
        ("S&P 500", "^GSPC"),
        ("NASDAQ", "^IXIC"),
        ("Dow Jones", "^DJI"),
        ("VIX", "^VIX")
    ]

    cols = st.columns(4)

    for col, (name, ticker) in zip(
        cols,
        markets
    ):

        q = get_quote(ticker)

        color = (
            "green"
            if q["change"] >= 0
            else "red"
        )

        with col:

            st.markdown(
                f"""
                <div class="card">

                    <div class="card-title">
                        {name}
                    </div>

                    <div class="card-value">
                        {q["price"]:,.2f}
                    </div>

                    <div class="{color}">
                        {"+" if q["change"] >= 0 else ""}
                        {q["change_pct"]:.2f}%
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )

    # PORTFOLIO

    st.markdown(
        '<div class="section-title">Portfolio Allocation</div>',
        unsafe_allow_html=True
    )

    pdf = get_portfolio_df()

    if not pdf.empty:

        c1, c2 = st.columns(
            [1.4, 1]
        )

        with c1:

            fig = px.bar(
                pdf,
                x="Ticker",
                y="Market Value"
            )

            fig.update_layout(
                template="simple_white",
                height=340,
                margin=dict(
                    l=10,
                    r=10,
                    t=10,
                    b=10
                )
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        with c2:

            fig = px.pie(
                pdf,
                names="Ticker",
                values="Market Value",
                hole=.68
            )

            fig.update_layout(
                template="simple_white",
                height=340
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )


# ============================================================
# CASH FLOW
# ============================================================

elif selected_page == "Cash Flow":

    st.markdown(
        '<div class="page-title">Cash Flow</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="page-subtitle">'
        'Track the movement of your money.'
        '</div>',
        unsafe_allow_html=True
    )

    income, expenses, net = cash_flow()

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "Income",
            f"RM {income:,.2f}"
        )

    with c2:
        st.metric(
            "Expenses",
            f"RM {expenses:,.2f}"
        )

    with c3:
        st.metric(
            "Net Cash Flow",
            f"RM {net:,.2f}"
        )

    df = get_transaction_df()

    if not df.empty:

        expense_df = df[
            df["type"] == "Expense"
        ]

        if not expense_df.empty:

            category = (
                expense_df
                .groupby("category")["amount"]
                .sum()
                .reset_index()
            )

            st.markdown(
                '<div class="section-title">'
                'Where your money goes'
                '</div>',
                unsafe_allow_html=True
            )

            c1, c2 = st.columns(2)

            with c1:

                fig = px.pie(
                    category,
                    names="category",
                    values="amount",
                    hole=.65
                )

                fig.update_layout(
                    height=400
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

            with c2:

                st.dataframe(
                    category,
                    use_container_width=True,
                    hide_index=True
                )


# ============================================================
# TRANSACTIONS
# ============================================================

elif selected_page == "Transactions":

    st.markdown(
        '<div class="page-title">Transactions</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="page-subtitle">'
        'Record and understand every movement of money.'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="ai-card">'
        '<div class="ai-title">✦ Finova AI Capture</div>'
        '<div class="ai-description">'
        'Describe your transaction naturally and Finova '
        'will help categorize it.'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )

    ai_text = st.text_input(
        "AI transaction input",
        placeholder=(
            "Example: I spent RM12 on lunch today"
        )
    )

    if st.button(
        "Analyze transaction"
    ):

        if ai_text:

            amount = None

            import re

            match = re.search(
                r'RM\s?([0-9]+(?:\.[0-9]+)?)',
                ai_text,
                re.I
            )

            if match:
                amount = float(
                    match.group(1)
                )

            lower = ai_text.lower()

            if "lunch" in lower or "food" in lower:
                category = "Food"

            elif "grab" in lower or "transport" in lower:
                category = "Transport"

            elif "rent" in lower:
                category = "Housing"

            elif "salary" in lower:
                category = "Salary"

            else:
                category = "Other"

            if amount:

                tx_type = (
                    "Income"
                    if "salary" in lower
                    else "Expense"
                )

                st.session_state.transactions.append(
                    {
                        "date": str(date.today()),
                        "type": tx_type,
                        "category": category,
                        "description": ai_text,
                        "amount": amount
                    }
                )

                st.success(
                    f"Detected {tx_type}: "
                    f"RM {amount:.2f} · {category}"
                )

                st.rerun()

            else:

                st.warning(
                    "I couldn't detect an amount."
                )

    with st.expander(
        "＋ Manual transaction"
    ):

        c1, c2, c3 = st.columns(3)

        with c1:

            tx_type = st.selectbox(
                "Type",
                [
                    "Income",
                    "Expense"
                ]
            )

            tx_category = st.selectbox(
                "Category",
                [
                    "Salary",
                    "Food",
                    "Housing",
                    "Transport",
                    "Shopping",
                    "Investment",
                    "Education",
                    "Healthcare",
                    "Entertainment",
                    "Other"
                ]
            )

        with c2:

            tx_amount = st.number_input(
                "Amount",
                min_value=0.0,
                step=1.0
            )

            tx_date = st.date_input(
                "Date",
                value=date.today()
            )

        with c3:

            description = st.text_input(
                "Description"
            )

            if st.button(
                "Save transaction"
            ):

                st.session_state.transactions.append(
                    {
                        "date": str(tx_date),
                        "type": tx_type,
                        "category": tx_category,
                        "description": description,
                        "amount": tx_amount
                    }
                )

                st.success(
                    "Transaction saved."
                )

                st.rerun()

    df = get_transaction_df()

    st.markdown(
        '<div class="section-title">'
        'Transaction history'
        '</div>',
        unsafe_allow_html=True
    )

    st.dataframe(
        df.sort_values(
            "date",
            ascending=False
        ),
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# PORTFOLIO
# ============================================================

elif selected_page == "Portfolio":

    st.markdown(
        '<div class="page-title">Portfolio</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="page-subtitle">'
        'Track your investments and performance.'
        '</div>',
        unsafe_allow_html=True
    )

    value, cost, pnl, pnl_pct = portfolio_summary()

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "Portfolio Value",
            f"RM {value:,.2f}"
        )

    with c2:
        st.metric(
            "Total P/L",
            f"RM {pnl:,.2f}",
            f"{pnl_pct:.2f}%"
        )

    with c3:
        st.metric(
            "Cost Basis",
            f"RM {cost:,.2f}"
        )

    df = get_portfolio_df()

    st.markdown(
        '<div class="section-title">Holdings</div>',
        unsafe_allow_html=True
    )

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    if not df.empty:

        st.markdown(
            '<div class="section-title">'
            'Asset Allocation'
            '</div>',
            unsafe_allow_html=True
        )

        fig = px.pie(
            df,
            names="Ticker",
            values="Market Value",
            hole=.65
        )

        fig.update_layout(
            height=420
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with st.expander(
        "＋ Add position"
    ):

        c1, c2, c3 = st.columns(3)

        with c1:

            ticker = st.text_input(
                "Ticker",
                placeholder="AAPL"
            )

        with c2:

            shares = st.number_input(
                "Shares",
                min_value=.01,
                value=1.0
            )

        with c3:

            avg_cost = st.number_input(
                "Average Cost",
                min_value=0.0,
                value=100.0
            )

        if st.button(
            "Add position"
        ):

            if ticker:

                st.session_state.portfolio.append(
                    {
                        "ticker": ticker.upper(),
                        "shares": shares,
                        "avg_cost": avg_cost
                    }
                )

                st.success(
                    f"{ticker.upper()} added."
                )

                st.rerun()


# ============================================================
# MARKETS
# ============================================================

elif selected_page == "Markets":

    st.markdown(
        '<div class="page-title">Markets</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="page-subtitle">'
        'Global market dashboard.'
        '</div>',
        unsafe_allow_html=True
    )

    assets = [
        ("S&P 500", "^GSPC"),
        ("NASDAQ", "^IXIC"),
        ("Dow Jones", "^DJI"),
        ("VIX", "^VIX"),
        ("Gold", "GC=F"),
        ("Bitcoin", "BTC-USD"),
        ("Crude Oil", "CL=F"),
        ("US 10Y", "^TNX")
    ]

    cols = st.columns(4)

    for i, (name, ticker) in enumerate(
        assets
    ):

        q = get_quote(ticker)

        with cols[i % 4]:

            color = (
                "green"
                if q["change"] >= 0
                else "red"
            )

            st.markdown(
                f"""
                <div class="card">

                    <div class="card-title">
                        {name}
                    </div>

                    <div class="card-value">
                        {q["price"]:,.2f}
                    </div>

                    <div class="{color}">
                        {"+" if q["change"] >= 0 else ""}
                        {q["change_pct"]:.2f}%
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown(
        '<div class="section-title">Market Chart</div>',
        unsafe_allow_html=True
    )

    selected_market = st.selectbox(
        "Market",
        [
            "^GSPC",
            "^IXIC",
            "^DJI",
            "^VIX",
            "GC=F",
            "BTC-USD",
            "CL=F"
        ]
    )

    period = st.selectbox(
        "Period",
        [
            "1mo",
            "3mo",
            "6mo",
            "1y",
            "5y"
        ]
    )

    history = get_history(
        selected_market,
        period
    )

    if not history.empty:

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=history.index,
                y=history["Close"],
                mode="lines",
                name=selected_market
            )
        )

        fig.update_layout(
            template="simple_white",
            height=470,
            margin=dict(
                l=10,
                r=10,
                t=15,
                b=10
            )
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


# ============================================================
# STOCK SEARCH
# ============================================================

elif selected_page == "Stock Search":

    st.markdown(
        '<div class="page-title">Stock Search</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="page-subtitle">'
        'Search companies, ETFs and market assets.'
        '</div>',
        unsafe_allow_html=True
    )

    ticker = st.text_input(
        "Search ticker",
        placeholder="NVDA"
    )

    if ticker:

        ticker = ticker.upper()

        q = get_quote(ticker)

        info = get_stock_info(ticker)

        st.markdown(
            f"""
            <div class="stock-header">

                <div class="stock-symbol">
                    {ticker}
                </div>

                <div class="stock-price">
                    ${q["price"]:,.2f}
                </div>

                <div class="
                    {"green"
                     if q["change"] >= 0
                     else "red"}
                ">

                    {"+" if q["change"] >= 0 else ""}
                    {q["change"]:.2f}
                    ({q["change_pct"]:.2f}%)

                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

        c1, c2, c3, c4 = st.columns(4)

        market_cap = info.get(
            "marketCap",
            0
        )

        pe = info.get(
            "trailingPE",
            None
        )

        high = info.get(
            "fiftyTwoWeekHigh",
            None
        )

        low = info.get(
            "fiftyTwoWeekLow",
            None
        )

        with c1:
            st.metric(
                "Market Cap",
                (
                    f"${market_cap/1e9:.1f}B"
                    if market_cap
                    else "N/A"
                )
            )

        with c2:
            st.metric(
                "P/E",
                (
                    f"{pe:.2f}"
                    if pe
                    else "N/A"
                )
            )

        with c3:
            st.metric(
                "52W High",
                (
                    f"${high:.2f}"
                    if high
                    else "N/A"
                )
            )

        with c4:
            st.metric(
                "52W Low",
                (
                    f"${low:.2f}"
                    if low
                    else "N/A"
                )
            )

        history = get_history(
            ticker,
            "1y"
        )

        if not history.empty:

            fig = go.Figure()

            fig.add_trace(
                go.Scatter(
                    x=history.index,
                    y=history["Close"],
                    mode="lines",
                    name=ticker
                )
            )

            fig.update_layout(
                template="simple_white",
                height=480
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        company = info.get(
            "longBusinessSummary",
            ""
        )

        if company:

            st.markdown(
                '<div class="section-title">'
                'Company'
                '</div>',
                unsafe_allow_html=True
            )

            st.write(company)


# ============================================================
# WATCHLIST
# ============================================================

elif selected_page == "Watchlist":

    st.markdown(
        '<div class="page-title">Watchlist</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="page-subtitle">'
        'Your selected assets.'
        '</div>',
        unsafe_allow_html=True
    )

    new_ticker = st.text_input(
        "Add ticker",
        placeholder="AAPL"
    )

    if st.button(
        "Add to watchlist"
    ):

        if new_ticker:

            ticker = new_ticker.upper()

            if ticker not in st.session_state.watchlist:

                st.session_state.watchlist.append(
                    ticker
                )

                st.rerun()

    for ticker in st.session_state.watchlist:

        q = get_quote(ticker)

        c1, c2, c3 = st.columns(
            [3, 2, 1]
        )

        with c1:

            st.markdown(
                f"### {ticker}"
            )

        with c2:

            st.write(
                f"${q['price']:,.2f}"
            )

        with c3:

            color = (
                "green"
                if q["change"] >= 0
                else "red"
            )

            st.markdown(
                f'<span class="{color}">'
                f'{"+" if q["change"] >= 0 else ""}'
                f'{q["change_pct"]:.2f}%'
                f'</span>',
                unsafe_allow_html=True
            )


# ============================================================
# BUDGET
# ============================================================

elif selected_page == "Budgets":

    st.markdown(
        '<div class="page-title">Budgets</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="page-subtitle">'
        'Control spending before it controls you.'
        '</div>',
        unsafe_allow_html=True
    )

    budgets = {
        "Food": (380, 500),
        "Housing": (750, 750),
        "Transport": (80, 150),
        "Entertainment": (90, 150),
        "Shopping": (120, 200)
    }

    for category, (spent, budget) in budgets.items():

        progress = min(
            spent / budget,
            1
        )

        st.markdown(
            f"""
            <div class="goal-card">

                <div class="goal-title">
                    {category}
                </div>

                <div class="goal-text">
                    RM {spent:,.0f}
                    /
                    RM {budget:,.0f}
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

        st.progress(
            progress
        )


# ============================================================
# GOALS
# ============================================================

elif selected_page == "Goals":

    st.markdown(
        '<div class="page-title">Goals</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="page-subtitle">'
        'Turn financial goals into measurable progress.'
        '</div>',
        unsafe_allow_html=True
    )

    for goal in st.session_state.goals:

        progress = min(
            goal["current"] /
            goal["target"],
            1
        )

        st.markdown(
            f"""
            <div class="goal-card">

                <div class="goal-title">
                    {goal["name"]}
                </div>

                <div class="goal-text">
                    RM {goal["current"]:,.0f}
                    /
                    RM {goal["target"]:,.0f}

                    ·

                    {progress * 100:.1f}%
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

        st.progress(
            progress
        )


# ============================================================
# FIRE
# ============================================================

elif selected_page == "FIRE":

    st.markdown(
        '<div class="page-title">FIRE Planner</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="page-subtitle">'
        'Financial Independence, Retire Early.'
        '</div>',
        unsafe_allow_html=True
    )

    c1, c2 = st.columns(2)

    with c1:

        current = st.number_input(
            "Current investments",
            min_value=0.0,
            value=10000.0
        )

        monthly = st.number_input(
            "Monthly contribution",
            min_value=0.0,
            value=500.0
        )

        annual_expenses = st.number_input(
            "Annual expenses",
            min_value=0.0,
            value=24000.0
        )

    with c2:

        return_rate = st.slider(
            "Expected return",
            1.0,
            15.0,
            8.0
        )

        withdrawal = st.slider(
            "Withdrawal rate",
            2.0,
            6.0,
            4.0
        )

    fire_number = (
        annual_expenses /
        (withdrawal / 100)
    )

    monthly_return = (
        return_rate / 100 / 12
    )

    balance = current

    years = []
    balances = []

    for year in range(41):

        years.append(year)

        balances.append(
            balance
        )

        for _ in range(12):

            balance = (
                balance *
                (1 + monthly_return)
                + monthly
            )

    projection = pd.DataFrame(
        {
            "Year": years,
            "Portfolio": balances
        }
    )

    st.markdown(
        f"""
        <div class="hero">

            <div class="hero-label">
                FIRE NUMBER
            </div>

            <div class="hero-value">
                RM {fire_number:,.0f}
            </div>

            <div class="hero-change">
                Based on a {withdrawal:.1f}% withdrawal rate
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    fig = px.line(
        projection,
        x="Year",
        y="Portfolio"
    )

    fig.add_hline(
        y=fire_number,
        line_dash="dash",
        annotation_text="FIRE Target"
    )

    fig.update_layout(
        template="simple_white",
        height=470
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# FINOVA ACADEMY
# ============================================================

elif selected_page == "Finova Academy":

    st.markdown(
        '<div class="page-title">Finova Academy</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="page-subtitle">'
        'From financial basics to advanced investing.'
        '</div>',
        unsafe_allow_html=True
    )

    courses = [

        (
            "01",
            "Financial Basics",
            "Money, interest, inflation, compounding and the time value of money."
        ),

        (
            "02",
            "Savings & Emergency Funds",
            "Build liquidity and understand how much cash you really need."
        ),

        (
            "03",
            "Investing 101",
            "Stocks, ETFs, index funds, diversification and risk."
        ),

        (
            "04",
            "Stocks",
            "Understand companies, ownership, valuation and market risk."
        ),

        (
            "05",
            "ETF & Index Investing",
            "Learn passive investing and long-term portfolio construction."
        ),

        (
            "06",
            "Bonds & REITs",
            "Understand fixed income, interest rates and property exposure."
        ),

        (
            "07",
            "Financial Statements",
            "Income statement, balance sheet and cash-flow analysis."
        ),

        (
            "08",
            "Portfolio Management",
            "Asset allocation, diversification, risk and performance."
        ),

        (
            "09",
            "Macroeconomics",
            "Interest rates, inflation, GDP, employment and economic cycles."
        ),

        (
            "10",
            "Behavioral Finance",
            "Understand fear, greed, bias and investor psychology."
        ),

        (
            "11",
            "Global Finance",
            "Currencies, capital markets, international investing and geopolitics."
        ),

        (
            "12",
            "Advanced Investing",
            "Valuation, DCF, risk management, PE, VC and capital structure."
        )
    ]

    for i in range(
        0,
        len(courses),
        2
    ):

        cols = st.columns(2)

        for col, course in zip(
            cols,
            courses[i:i+2]
        ):

            number, title, description = course

            with col:

                st.markdown(
                    f"""
                    <div class="lesson">

                        <div class="lesson-number">
                            LESSON {number}
                        </div>

                        <div class="lesson-title">
                            {title}
                        </div>

                        <div class="lesson-description">
                            {description}
                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True
                )


# ============================================================
# GLOBAL FINANCE
# ============================================================

elif selected_page == "Global Finance":

    st.markdown(
        '<div class="page-title">Global Finance</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="page-subtitle">'
        'Understand the forces moving global markets.'
        '</div>',
        unsafe_allow_html=True
    )

    topics = [
        "Federal Reserve",
        "Interest Rates",
        "Inflation",
        "US Dollar",
        "Global Equities",
        "Oil",
        "Gold",
        "Emerging Markets",
        "Europe",
        "Asia"
    ]

    for topic in topics:

        with st.expander(
            topic
        ):

            st.write(
                f"""
                Finova educational module:

                {topic}

                The module will explain the concept,
                major drivers, market relationships,
                historical context and potential
                implications for investors.
                """
            )


# ============================================================
# FINOVA AI
# ============================================================

elif selected_page == "Finova AI":

    st.markdown(
        '<div class="page-title">Finova AI</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="page-subtitle">'
        'Your financial intelligence layer.'
        '</div>',
        unsafe_allow_html=True
    )

    value, cost, pnl, pnl_pct = portfolio_summary()

    income, expenses, net = cash_flow()

    savings_rate = (
        net / income * 100
        if income
        else 0
    )

    score = 70

    if savings_rate >= 20:
        score += 10

    if savings_rate >= 30:
        score += 5

    if value > 0:
        score += 5

    score = min(
        score,
        100
    )

    st.markdown(
        f"""
        <div class="ai-card">

            <div class="ai-title">
                ✦ Finova AI Analyst
            </div>

            <div class="ai-description">
                Automated analysis of your financial position.
            </div>

            <br>

            <div class="ai-score">
                {score}
            </div>

            <div class="ai-description">
                FINANCIAL HEALTH SCORE
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-title">'
        'AI Insights'
        '</div>',
        unsafe_allow_html=True
    )

    if savings_rate >= 20:

        st.success(
            f"Your savings rate is {savings_rate:.1f}%. "
            "Your cash-flow discipline is currently strong."
        )

    else:

        st.warning(
            f"Your savings rate is {savings_rate:.1f}%. "
            "Consider reviewing discretionary spending."
        )

    if value > 0:

        st.info(
            f"Tracked investment portfolio: "
            f"RM {value:,.2f}."
        )

    if expenses > income * .7:

        st.warning(
            "Your tracked expenses are relatively high "
            "compared with income."
        )

    else:

        st.success(
            "Your tracked expenses remain below "
            "70% of income."
        )

    st.markdown(
        '<div class="section-title">'
        'Ask Finova'
        '</div>',
        unsafe_allow_html=True
    )

    question = st.text_input(
        "Question",
        placeholder=(
            "Why am I spending so much?"
        )
    )

    if st.button(
        "Analyze"
    ):

        if question:

            q = question.lower()

            if (
                "spending" in q
                or "expense" in q
            ):

                st.write(
                    """
                    Based on your current transaction data,
                    Finova recommends reviewing your largest
                    expense categories first.
                    """
                )

            elif (
                "portfolio" in q
                or "investment" in q
            ):

                st.write(
                    """
                    Your portfolio should be evaluated across
                    diversification, concentration, risk,
                    liquidity and time horizon.
                    """
                )

            elif "saving" in q:

                st.write(
                    f"""
                    Your current tracked savings rate is
                    approximately {savings_rate:.1f}%.
                    """
                )

            else:

                st.write(
                    """
                    Finova recommends analyzing the question
                    using your cash flow, goals, portfolio and
                    financial-health data.
                    """
                )

    st.warning(
        "Finova AI is currently an educational prototype "
        "and does not provide personalized regulated "
        "financial advice."
    )


# ============================================================
# FINANCIAL HEALTH
# ============================================================

elif selected_page == "Financial Health":

    st.markdown(
        '<div class="page-title">Financial Health</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="page-subtitle">'
        'A five-dimensional view of your financial life.'
        '</div>',
        unsafe_allow_html=True
    )

    income, expenses, net = cash_flow()

    savings_rate = (
        net / income * 100
        if income
        else 0
    )

    scores = {

        "Cash Flow":
            min(
                100,
                int(
                    max(
                        0,
                        savings_rate * 2
                    )
                ) + 50
            ),

        "Liquidity": 72,

        "Savings": min(
            100,
            int(
                50 + savings_rate
            )
        ),

        "Investing": 79,

        "Risk": 68
    }

    cols = st.columns(5)

    for col, (
        category,
        score
    ) in zip(
        cols,
        scores.items()
    ):

        with col:

            st.markdown(
                f"""
                <div class="card">

                    <div class="card-title">
                        {category.upper()}
                    </div>

                    <div class="card-value">
                        {score}
                    </div>

                    <div class="card-small">
                        / 100
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )

    df = pd.DataFrame(
        {
            "Category":
                list(scores.keys()),

            "Score":
                list(scores.values())
        }
    )

    fig = px.bar(
        df,
        x="Category",
        y="Score",
        range_y=[0, 100]
    )

    fig.update_layout(
        template="simple_white",
        height=430
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# ACTION CENTER
# ============================================================

elif selected_page == "Action Center":

    st.markdown(
        '<div class="page-title">Action Center</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="page-subtitle">'
        'What Finova thinks you should review next.'
        '</div>',
        unsafe_allow_html=True
    )

    actions = [

        (
            "HIGH",
            "Emergency Fund",
            "Review whether your liquid reserve is sufficient."
        ),

        (
            "MEDIUM",
            "Portfolio",
            "Review concentration and asset allocation."
        ),

        (
            "MEDIUM",
            "Budget",
            "Review your largest spending categories."
        ),

        (
            "LOW",
            "Education",
            "Continue learning before using complex products."
        )

    ]

    for priority, title, description in actions:

        st.markdown(
            f"""
            <div class="card">

                <div class="card-title">
                    {priority}
                </div>

                <div class="card-value"
                     style="font-size:20px;">
                    {title}
                </div>

                <div class="card-small">
                    {description}
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">

        FINOVA NEO · PERSONAL FINANCE OPERATING SYSTEM

        <br><br>

        Market data may be delayed.
        Educational information only.

    </div>
    """,
    unsafe_allow_html=True
)