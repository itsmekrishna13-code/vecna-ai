
from dotenv import load_dotenv
load_dotenv()

from livekit import agents, rtc
from livekit.agents import AgentServer, AgentSession, Agent, room_io
from livekit.plugins import google, noise_cancellation

# ===============================
# VECNA PROMPTS (Hindi + Vecna)
# ===============================
from Vecna_prompts import behavior_prompts, Reply_prompts, VECNA_SYSTEM_PROMPT

# ===============================
# TOOLS (SYSTEM + WEB)
# ===============================
from Vecna_google_search import google_search, get_current_datetime
from vecna_get_whether import get_weather
from Vecna_window_CTRL import open, close, folder_file
from vecna_file_opner import Play_file

# ===============================
# INPUT CONTROL TOOLS
# ===============================
from keyboard_mouse_CTRL import (
    move_cursor_tool,
    mouse_click_tool,
    scroll_cursor_tool,
    type_text_tool,
    press_key_tool,
    press_hotkey_tool,
    control_volume_tool,
    swipe_gesture_tool,
)

# ==================================================
# VECNA ASSISTANT CLASS
# ==================================================
class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=VECNA_SYSTEM_PROMPT,  # Combined Vecna personality + Lore
            tools=[
                # 🌐 Information tools
                google_search,
                get_current_datetime,
                get_weather,

                # 🖥 System control
                open,              # apps open
                close,             # apps close
                folder_file,       # folder open
                Play_file,         # media / file open

                # 🖱 Mouse & keyboard
                move_cursor_tool,
                mouse_click_tool,
                scroll_cursor_tool,
                type_text_tool,
                press_key_tool,
                press_hotkey_tool,
                control_volume_tool,
                swipe_gesture_tool,
            ],
        )

# ==================================================
# AGENT SERVER
# ==================================================
server = AgentServer()

@server.rtc_session()
async def vecna_agent(ctx: agents.JobContext):
    """
    LiveKit session using Google Realtime Voice model.
    Vecna listens → understands Hindi/English → responds in Vecna tone.
    """

    try:
        print(f"Agent interacting with room: {ctx.room.name}")
        session = AgentSession(
            llm=google.beta.realtime.RealtimeModel(
                voice="Charon",   # Deep, dark voice fits Vecna
            )
        )

        await session.start(
            room=ctx.room,
            agent=Assistant(),
        )

        # Initial Vecna presence reply
        await session.generate_reply()
    except Exception as e:
        print(f"❌ Connection error: {e}")

# ==================================================
# RUN APP
# ==================================================
if __name__ == "__main__":
    # Run Agent
    agents.cli.run_app(server)
