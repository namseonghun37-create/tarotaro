import streamlit as st
import random
from tarot_data import TAROT_CARDS

st.set_page_config(page_title="미스틱 타로", page_icon="🔮", layout="centered", initial_sidebar_state="collapsed")

WIKI_BASE = "https://commons.wikimedia.org/wiki/Special:FilePath/"
POSITIONS = [
    {"label": "과거", "sub": "PAST"},
    {"label": "현재", "sub": "PRESENT"},
    {"label": "미래", "sub": "FUTURE"},
]

# ---------------------------
# 세션 상태 초기화
# ---------------------------
if "deck" not in st.session_state:
    order = list(range(len(TAROT_CARDS)))
    random.shuffle(order)
    st.session_state.deck = order
    st.session_state.deck_reversed = [random.random() < 0.5 for _ in order]
if "picked" not in st.session_state:
    st.session_state.picked = []
if "revealed" not in st.session_state:
    st.session_state.revealed = []
if "session_round" not in st.session_state:
    st.session_state.session_round = 0
if "celebrated" not in st.session_state:
    st.session_state.celebrated = False


def reset_deck():
    order = list(range(len(TAROT_CARDS)))
    random.shuffle(order)
    st.session_state.deck = order
    st.session_state.deck_reversed = [random.random() < 0.5 for _ in order]
    st.session_state.picked = []
    st.session_state.revealed = []
    st.session_state.celebrated = False
    st.session_state.session_round += 1


# 선택된 카드 수만큼 revealed 리스트를 "확장"만 함 (기존 True 값은 보존)
# -> 카드를 고르는 도중 먼저 뒤집어본 카드가 다시 뒷면으로 돌아가는 버그 방지
while len(st.session_state.revealed) < len(st.session_state.picked):
    st.session_state.revealed.append(False)

# ---------------------------
# 전역 스타일 (스트림릿 기본 크롬 제거 + 네이티브 앱 룩)
# ---------------------------
st.markdown("""
<style>
    #MainMenu, header, footer, [data-testid="stToolbar"],
    [data-testid="stDecoration"], [data-testid="stStatusWidget"] { display: none !important; }
    .stApp { background: #0b0713; }
    .block-container { padding-top: 2rem !important; padding-bottom: 3rem !important; max-width: 480px !important; }
    * { font-family: -apple-system, BlinkMacSystemFont, "Pretendard", "Segoe UI", sans-serif !important; }
    div[data-testid="stButton"] button {
        border: none !important; box-shadow: none !important;
        background: rgba(166,136,240,0.14) !important; color: #c3aef4 !important;
        border-radius: 12px !important; font-weight: 600 !important;
    }
    iframe { border: none !important; }

    .app-header { text-align: center; margin-bottom: 4px; }
    .app-title { font-size: 21px; font-weight: 700; color: #f4edff; margin: 0; }
    .app-subtitle { font-size: 12.5px; color: #7c7291; margin: 4px 0 0; }

    .pos-label {
        text-align: center; font-size: 10.5px; font-weight: 700;
        letter-spacing: 1.5px; color: #9a8cc4; margin-bottom: 6px;
    }
    .flip-scene { perspective: 1000px; }
    .flip-card {
        position: relative; width: 100%; aspect-ratio: 3 / 5;
        transform-style: preserve-3d; transition: transform 0.7s cubic-bezier(.4,.2,.2,1);
        border-radius: 12px;
    }
    .flip-card.flipped { transform: rotateY(180deg); }
    .flip-face { position: absolute; inset: 0; backface-visibility: hidden; border-radius: 12px; overflow: hidden; }
    .flip-back {
        background: linear-gradient(135deg, #3a2c66 0%, #1f1538 100%);
        display: flex; align-items: center; justify-content: center;
        border: 1px solid rgba(255,255,255,0.08);
    }
    .flip-back::before {
        content: ""; width: 60%; height: 72%;
        border: 1.5px solid rgba(255,255,255,0.28); border-radius: 6px;
        background: radial-gradient(circle at center, rgba(255,255,255,0.14) 0%, transparent 65%);
    }
    .flip-front {
        transform: rotateY(180deg); background: #14091f;
        border: 1px solid rgba(255,255,255,0.08);
    }
    .flip-front img {
        width: 100%; height: 100%; object-fit: cover; object-position: top; display: block;
        position: relative; z-index: 1;
    }
    .flip-front img.broken { opacity: 0; }
    .flip-front.rev img { transform: rotate(180deg); }
    .flip-front::after {
        content: "✦"; position: absolute; top: 50%; left: 50%;
        transform: translate(-50%, -50%); font-size: 24px;
        color: rgba(255,255,255,0.22); pointer-events: none;
    }

    .card-name { text-align: center; font-size: 11px; font-weight: 600; color: #d8ceee; margin: 7px 0 0; line-height: 1.3; }
    .card-orient { text-align: center; font-size: 10px; color: #756a90; margin: 1px 0 0; }

    .detail-card {
        background: #14101f; border: 1px solid rgba(255,255,255,0.06);
        border-radius: 12px; padding: 12px 13px; margin-top: 8px;
    }
    .detail-row { margin-bottom: 8px; }
    .detail-row:last-child { margin-bottom: 0; }
    .detail-label {
        font-size: 9.5px; font-weight: 700; color: #a688f0;
        letter-spacing: 0.5px; margin: 0 0 2px; text-transform: uppercase;
    }
    .detail-text { font-size: 11.5px; color: #b8aed6; margin: 0; line-height: 1.5; }

    .summary-banner {
        margin-top: 20px; text-align: center; padding: 16px; border-radius: 14px;
        background: linear-gradient(135deg, rgba(166,136,240,0.12), rgba(255,209,102,0.08));
        border: 1px solid rgba(255,255,255,0.08); color: #e6dcff; font-size: 12.5px; line-height: 1.6;
    }
    .footer-note { text-align: center; font-size: 10.5px; color: #4a4260; margin-top: 26px; }
    .progress-text { text-align: center; font-size: 12px; color: #9a8cc4; margin: 10px 0 2px; }
    .fan-hint { text-align: center; font-size: 10.5px; color: #5c5378; margin: 0 0 10px; }

    .fan-wrap {
        display: flex; overflow-x: auto; overflow-y: hidden;
        padding: 14px 10px 18px; margin: 4px 0 8px;
        scrollbar-width: thin; scrollbar-color: rgba(166,136,240,0.4) transparent;
    }
    .fan-wrap::-webkit-scrollbar { height: 5px; }
    .fan-wrap::-webkit-scrollbar-thumb { background: rgba(166,136,240,0.4); border-radius: 4px; }
    .fan-wrap div[data-testid="column"],
    .fan-wrap div[data-testid="stColumn"] {
        width: 46px !important; flex: none !important; min-width: 46px !important;
        padding: 0 !important; margin-right: -18px !important;
    }
    .fan-wrap div[data-testid="column"]:last-child,
    .fan-wrap div[data-testid="stColumn"]:last-child { margin-right: 0 !important; }
    .fan-wrap div[data-testid="stButton"] button {
        width: 46px !important; height: 78px !important; padding: 0 !important;
        min-height: 78px !important;
        background: linear-gradient(135deg, #3a2c66 0%, #1f1538 100%) !important;
        border: 1px solid rgba(255,255,255,0.18) !important; border-radius: 7px !important;
        box-shadow: 0 3px 8px rgba(0,0,0,0.45) !important;
        color: transparent !important;
        transition: transform 0.15s ease, box-shadow 0.15s ease, filter 0.15s ease !important;
        position: relative !important;
    }
    .fan-wrap div[data-testid="stButton"] button::after {
        content: ""; position: absolute; top: 50%; left: 50%;
        width: 56%; height: 66%; transform: translate(-50%, -50%);
        border: 1px solid rgba(255,255,255,0.25); border-radius: 4px;
        background: radial-gradient(circle at center, rgba(255,255,255,0.13) 0%, transparent 65%);
        pointer-events: none;
    }
    .fan-wrap div[data-testid="stButton"] button:hover {
        filter: brightness(1.35) !important;
        transform: translateY(-10px) !important;
        box-shadow: 0 10px 20px rgba(166,136,240,0.55) !important;
        z-index: 50 !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="app-header">
    <p class="app-title">🔮 미스틱 타로</p>
    <p class="app-subtitle">마음이 이끄는 카드 3장을 직접 골라보세요</p>
</div>
""", unsafe_allow_html=True)

if st.button("🌀 카드 덱 새로 섞기", use_container_width=True):
    reset_deck()
    st.rerun()

# ---------------------------
# 1단계: 카드 덱에서 직접 3장 선택
# ---------------------------
if len(st.session_state.picked) < 3:
    remaining = 3 - len(st.session_state.picked)
    st.markdown(f'<p class="progress-text">카드를 클릭해서 골라주세요 · {remaining}장 남음</p>', unsafe_allow_html=True)
    st.markdown('<p class="fan-hint">옆으로 넘기며 마음이 가는 카드를 찾아보세요 →</p>', unsafe_allow_html=True)

    deck_indices = [i for i in st.session_state.deck if i not in st.session_state.picked]

    st.markdown('<div class="fan-wrap">', unsafe_allow_html=True)
    fan_cols = st.columns(len(deck_indices), gap="small")
    for idx, card_i in enumerate(deck_indices):
        with fan_cols[idx]:
            if st.button("\U0001F0A0", key=f"pick_{card_i}_{st.session_state.session_round}"):
                st.session_state.picked.append(card_i)
                st.session_state.revealed.append(False)
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------
# 2단계: 선택된 카드 표시 + 뒤집기 + 상세 해석
# ---------------------------
if st.session_state.picked:
    st.write("")
    cols = st.columns(3, gap="small")
    for i in range(3):
        with cols[i]:
            st.markdown(f'<div class="pos-label">{POSITIONS[i]["label"]}<br>{POSITIONS[i]["sub"]}</div>', unsafe_allow_html=True)

            if i < len(st.session_state.picked):
                card_i = st.session_state.picked[i]
                card = TAROT_CARDS[card_i]
                is_rev = st.session_state.deck_reversed[card_i]
                flipped = "flipped" if st.session_state.revealed[i] else ""
                rev_cls = "rev" if is_rev else ""
                img_url = WIKI_BASE + card["file"]

                st.markdown(f"""
                <div class="flip-scene">
                    <div class="flip-card {flipped}">
                        <div class="flip-face flip-back"></div>
                        <div class="flip-face flip-front {rev_cls}">
                            <img src="{img_url}" alt="{card['name']}" loading="lazy" onerror="this.classList.add('broken')" />
                        </div>
                    </div>
                </div>
                <p class="card-name">{card['num']} · {card['kr']}</p>
                """, unsafe_allow_html=True)

                if not st.session_state.revealed[i]:
                    if st.button("뒤집기", key=f"reveal_{i}_{st.session_state.session_round}", use_container_width=True):
                        st.session_state.revealed[i] = True
                        st.rerun()
                else:
                    detail = card["reversed"] if is_rev else card["upright"]
                    orient_label = "역방향" if is_rev else "정방향"
                    st.markdown(f"""
                    <p class="card-orient" style="margin-top:-4px;">{orient_label}</p>
                    <div class="detail-card">
                        <div class="detail-row"><p class="detail-label">상징</p><p class="detail-text">{detail['symbol']}</p></div>
                        <div class="detail-row"><p class="detail-label">사랑</p><p class="detail-text">{detail['love']}</p></div>
                        <div class="detail-row"><p class="detail-label">일 · 재물</p><p class="detail-text">{detail['work']}</p></div>
                        <div class="detail-row"><p class="detail-label">건강</p><p class="detail-text">{detail['health']}</p></div>
                        <div class="detail-row"><p class="detail-label">조언</p><p class="detail-text">{detail['advice']}</p></div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="flip-scene">
                    <div class="flip-card">
                        <div class="flip-face flip-back"></div>
                    </div>
                </div>
                <p class="card-name" style="color:#4a4260;">선택 대기중</p>
                """, unsafe_allow_html=True)

    if len(st.session_state.picked) == 3 and all(st.session_state.revealed):
        st.markdown("""
        <div class="summary-banner">
            ✨ 세 장의 카드가 모두 열렸어요.<br>
            과거의 배경과 현재의 흐름, 미래의 가능성을 이어서 읽어보고<br>
            지금 당신에게 필요한 조언을 마음에 담아보세요.
        </div>
        """, unsafe_allow_html=True)
        if not st.session_state.celebrated:
            st.balloons()
            st.session_state.celebrated = True
else:
    st.markdown("""
    <div class="detail-card" style="text-align:center;">
        <p class="detail-text">위 카드 덱에서 마음이 가는 카드를 3장 골라보세요.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<p class="footer-note">카드 이미지: 1909년 Rider–Waite 타로 원본 (Public Domain)</p>', unsafe_allow_html=True)
